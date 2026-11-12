"""Offline, fail-closed import of structured engineering task events.

Reads only operator-provided JSON from local files. Never calls GitHub, GAS,
HTTP or databases. Never modifies a source file. Output is an untrusted,
pending-human-review *proposal*, never an approved real-world outcome.

This tool enforces a strict safe-field allowlist and drops ALL free-text notes,
rather than claiming that regex PII redaction can be perfect. Real usage needs
separate, verifiable data-owner approval outside this repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
IDENT = re.compile(r"^(?:EV|C|G|B|P|REV)_[0-9a-f]{12}$")
TASK_FAMILIES = frozenset({"github_ci", "gas_api", "web_qa", "database", "security", "general"})
OPERATIONS = frozenset({
    "GET_INVENTORY", "GET_CONTENT", "CREATE_VERSION", "CREATE_DEPLOYMENT",
    "CODE_PATCH", "UI_UAT", "READ_DATA", "UNKNOWN",
})
RESULTS = frozenset({"success", "failure", "unknown", "partial"})
EVIDENCE_TYPES = frozenset({
    "remote_readback", "ui_uat", "ci_only", "log_only", "not_verified",
})
SOURCE_KINDS = frozenset({"github_actions", "gas", "ui", "manual", "other"})
SCOPES = frozenset({"synthetic", "reviewed_real"})
EVENT_FIELDS = frozenset({
    "event_id", "case_id", "group_id", "project_id", "task_family",
    "source_kind", "operation", "result", "evidence_type",
    "evidence_sha256", "source_commit_sha", "occurred_at_utc",
    "write_authorized", "http_status", "note",
})
AUTH_FIELDS = frozenset({
    "schema_version", "scope", "purpose", "approved", "approved_by",
    "expires_at_utc", "allowed_operations", "allowed_projects",
    "source_sha256", "operator_confirmed",
})
BATCH_FIELDS = frozenset({"schema_version", "scope", "batch_id", "events"})
MAX_BYTES = 1_048_576
MAX_EVENTS = 250
MAX_EVIDENCE_BYTES = 64 * 1024 * 1024

def _outside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
        return False
    except ValueError:
        return True

def _time(raw: str) -> datetime:
    if type(raw) is not str or not re.fullmatch(
        r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", raw
    ):
        raise ValueError("invalid UTC timestamp")
    try:
        return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError("invalid UTC timestamp") from exc

def _closed_dict(raw: Any, keys: frozenset, required: frozenset, name: str) -> dict:
    if type(raw) is not dict or not required.issubset(raw) or set(raw) - keys:
        raise ValueError("invalid " + name + " fields (raw content not accepted)")
    return raw

def _ident(raw: Any, prefix: str) -> str:
    if type(raw) is not str or not IDENT.fullmatch(raw) or not raw.startswith(prefix + "_"):
        raise ValueError("invalid pseudonymous identifier")
    return raw

def _read_file(path: Path, *, max_bytes: int = MAX_BYTES) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("source must be a regular non-symlink file")
    if path.stat().st_size > max_bytes:
        raise ValueError("source exceeds size limit")
    with path.open("rb") as f:
        raw = f.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError("source exceeds size limit")
    return raw

def _json(raw: bytes) -> Any:
    def reject_duplicate_keys(pairs):
        data = {}
        for key, value in pairs:
            if key in data:
                raise ValueError("duplicate JSON keys are forbidden")
            data[key] = value
        return data
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("invalid or ambiguous JSON input") from exc

def load_authorization(path: Path, scope: str, now: datetime | None = None) -> dict:
    if scope not in SCOPES:
        raise ValueError("invalid requested scope")
    if scope == "reviewed_real" and not _outside_repo(path):
        raise ValueError("real authorization must remain outside public repository")
    auth = _closed_dict(_json(_read_file(path)), AUTH_FIELDS, AUTH_FIELDS, "authorization")
    if type(auth["schema_version"]) is not int or auth["schema_version"] != 1 or auth["scope"] != scope:
        raise ValueError("authorization scope/version mismatch")
    if auth["purpose"] != "engineering_task_feedback":
        raise ValueError("unauthorized purpose")
    if auth["approved"] is not True or auth["operator_confirmed"] is not True:
        raise ValueError("explicit human/operator authorization required")
    if scope == "reviewed_real":
        _ident(auth["approved_by"], "REV")
        if type(auth["source_sha256"]) is not str or not HEX64.fullmatch(auth["source_sha256"]):
            raise ValueError("real source digest approval required")
    elif auth["approved_by"] != "SYNTHETIC_FIXTURE":
        raise ValueError("synthetic scope must be labeled fixture")
    if auth["source_sha256"] is not None and (
        type(auth["source_sha256"]) is not str or not HEX64.fullmatch(auth["source_sha256"])
    ):
        raise ValueError("invalid approved source digest")
    if type(auth["allowed_operations"]) is not list or not auth["allowed_operations"]:
        raise ValueError("missing operation allowlist")
    if any(type(x) is not str or x not in OPERATIONS for x in auth["allowed_operations"]):
        raise ValueError("unsafe operation allowlist")
    projects = auth["allowed_projects"]
    if type(projects) is not list or not projects:
        raise ValueError("missing project allowlist")
    for project in projects:
        _ident(project, "P")
    instant = now or datetime.now(timezone.utc)
    if _time(auth["expires_at_utc"]) <= instant:
        raise ValueError("authorization expired")
    return auth

def _validate_event(event: Any, scope: str, auth: dict) -> tuple[dict, bool]:
    req = EVENT_FIELDS - {"note"}
    e = _closed_dict(event, EVENT_FIELDS, req, "event")
    for name, prefix in (
        ("event_id", "EV"), ("case_id", "C"), ("group_id", "G"),
        ("project_id", "P"),
    ):
        _ident(e[name], prefix)
    for name, allowed in (
        ("task_family", TASK_FAMILIES), ("source_kind", SOURCE_KINDS),
        ("operation", OPERATIONS), ("result", RESULTS),
        ("evidence_type", EVIDENCE_TYPES),
    ):
        if type(e[name]) is not str or e[name] not in allowed:
            raise ValueError("invalid event enum")
    if e["project_id"] not in auth["allowed_projects"]:
        raise ValueError("project not authorized")
    if e["operation"] not in auth["allowed_operations"]:
        raise ValueError("operation not authorized")
    _time(e["occurred_at_utc"])
    if type(e["write_authorized"]) is not bool:
        raise ValueError("write authorization must be boolean")
    if e["source_commit_sha"] is not None and (
        type(e["source_commit_sha"]) is not str or not HEX40.fullmatch(e["source_commit_sha"])
    ):
        raise ValueError("source commit must be exact SHA")
    if e["evidence_sha256"] is not None and (
        type(e["evidence_sha256"]) is not str or not HEX64.fullmatch(e["evidence_sha256"])
    ):
        raise ValueError("evidence must be SHA256 digest, never source bytes or URL")
    if scope == "reviewed_real" and e["evidence_sha256"] is None:
        raise ValueError("real events require an independently verified evidence digest")
    status = e["http_status"]
    if status is not None and (type(status) is not int or status < 100 or status > 599):
        raise ValueError("invalid HTTP status")
    # DROP all free-text, even if it contains URLs, PII or secrets.
    if "note" in e and e["note"] is not None and type(e["note"]) is not str:
        raise ValueError("note must be text")
    dropped = bool(e.get("note"))
    safe = {key: e[key] for key in (EVENT_FIELDS - {"note"})}
    # A result=success never means an already verified task outcome.
    return safe, dropped

def ingest(source: Path, authorization: Path, scope: str,
           now: datetime | None = None) -> dict:
    """Validate before producing an in-memory sanitized *unapproved* queue.

    No writes are performed. For real data, operator-supplied paths must be
    outside the public repository; approval metadata is a human assertion,
    NOT cryptographic proof of legal authority.
    """
    auth = load_authorization(authorization, scope, now)
    if scope == "reviewed_real" and not _outside_repo(source):
        raise ValueError("real source must remain outside public repository")
    raw = _read_file(source)
    digest = hashlib.sha256(raw).hexdigest()
    if auth["source_sha256"] is not None and auth["source_sha256"] != digest:
        raise ValueError("source digest differs from operator-approved fingerprint")
    batch = _closed_dict(_json(raw), BATCH_FIELDS, BATCH_FIELDS, "batch")
    if type(batch["schema_version"]) is not int or batch["schema_version"] != 1 or batch["scope"] != scope:
        raise ValueError("event batch scope/version mismatch")
    _ident(batch["batch_id"], "B")
    if type(batch["events"]) is not list or not 1 <= len(batch["events"]) <= MAX_EVENTS:
        raise ValueError("batch event count outside limits")
    seen = set()
    grouped: dict[str, dict] = {}
    notes_dropped = 0
    for raw_event in batch["events"]:
        event, dropped = _validate_event(raw_event, scope, auth)
        if event["event_id"] in seen:
            raise ValueError("duplicate event identifier")
        seen.add(event["event_id"])
        notes_dropped += int(dropped)
        case = event["case_id"]
        if case not in grouped:
            grouped[case] = {
                "queue_id": "Q_" + case[2:], "case_id": case,
                "group_id": event["group_id"], "project_id": event["project_id"],
                "task_family": event["task_family"],
                "event_ids": [], "events": [], "evidence_sha256": [],
                "status": "PENDING_HUMAN_REVIEW", "verified": False,
                "outcome": "unknown", "expected_action": None,
                "write_authorized": False, "human_review_required": True,
            }
        row = grouped[case]
        if (event["group_id"], event["project_id"], event["task_family"]) != (
            row["group_id"], row["project_id"], row["task_family"]
        ):
            raise ValueError("case identity changed between events")
        row["event_ids"].append(event["event_id"])
        row["events"].append({
            "event_id": event["event_id"],
            "occurred_at_utc": event["occurred_at_utc"],
            "source_kind": event["source_kind"],
            "operation": event["operation"],
            "result": event["result"],
            "http_status": event["http_status"],
            "evidence_type": event["evidence_type"],
            "evidence_sha256": event["evidence_sha256"],
            "source_commit_sha": event["source_commit_sha"],
            "write_authorized_at_event": event["write_authorized"],
        })
        if event["evidence_sha256"] is not None:
            row["evidence_sha256"].append(event["evidence_sha256"])
    queue = []
    for _, row in sorted(grouped.items()):
        row["event_ids"].sort()
        row["events"].sort(key=lambda x: (x["occurred_at_utc"], x["event_id"]))
        row["evidence_sha256"] = sorted(set(row["evidence_sha256"]))
        queue.append(row)
    return {
        "schema_version": 1, "scope": scope, "batch_id": batch["batch_id"],
        "source_sha256": digest, "authorization_attested": True,
        "authorization_externally_verified": False,
        "records": queue, "redacted_free_text_count": notes_dropped,
        "source_was_modified": False, "formal_review_completed": False,
    }

def safe_summary(queue: dict) -> dict:
    return {
        "scope": queue["scope"],
        "source_sha256": queue["source_sha256"],
        "events": sum(len(x["event_ids"]) for x in queue["records"]),
        "pending_cases": len(queue["records"]),
        "redacted_free_text_count": queue["redacted_free_text_count"],
        "approved_cases": 0,
        "remote_action_performed": False,
    }

def write_queue_private(queue: dict, output: Path) -> None:
    if queue["scope"] == "reviewed_real" and not _outside_repo(output):
        raise ValueError("real queue must remain outside public repository")
    if output.is_symlink() or output.exists():
        raise ValueError("refuse to replace existing queue or symlink")
    if not output.parent.is_dir():
        raise ValueError("output parent directory must already exist")
    # Never write source files or overwrite a pre-existing queue (idempotency).
    payload = json.dumps(queue, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if queue["scope"] == "reviewed_real":
        mode = 0o600
    else:
        mode = 0o600
    fd = os.open(str(output), os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
    except BaseException:
        output.unlink(missing_ok=True)
        raise

def verify_evidence_bytes(path: Path, expected_sha256: str,
                          approved_root: Path) -> dict:
    """Offline SHA verification. Never stores, emits or processes the raw bytes.

    Explicit local approval/root selection must be checked *before* calling.
    SHA equality does not prove the evidence source's truth or origin.
    """
    if type(expected_sha256) is not str or not HEX64.fullmatch(expected_sha256):
        raise ValueError("invalid evidence SHA")
    if path.is_symlink() or not path.is_file():
        raise ValueError("evidence must be a regular non-symlink file")
    if approved_root.is_symlink() or not approved_root.is_dir():
        raise ValueError("approved evidence root invalid")
    try:
        path.resolve().relative_to(approved_root.resolve())
    except ValueError as exc:
        raise ValueError("evidence outside approved local directory") from exc
    h = hashlib.sha256()
    count = 0
    with path.open("rb") as source:
        while True:
            block = source.read(1024 * 1024)
            if not block:
                break
            count += len(block)
            if count > MAX_EVIDENCE_BYTES:
                raise ValueError("evidence exceeds size cap")
            h.update(block)
    return {"matches_expected_sha256": h.hexdigest() == expected_sha256,
            "bytes_read": count, "raw_evidence_exported": False,
            "truth_of_source_verified": False}

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("validate", "preview", "prepare"))
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--authorization", required=True, type=Path)
    p.add_argument("--scope", choices=sorted(SCOPES), required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    try:
        queue = ingest(args.input, args.authorization, args.scope)
        result = safe_summary(queue)
        if args.command == "prepare":
            if args.output is None or args.output.resolve() == args.input.resolve():
                raise ValueError("prepare requires a distinct explicit output path")
            write_queue_private(queue, args.output)
            result["queue_written"] = True
        else:
            if args.output is not None:
                raise ValueError("only prepare may write a new output")
            result["queue_written"] = False
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        # Never echo raw input, paths, tokens, or user-provided values.
        print("TASK_INGEST_BLOCKED: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
