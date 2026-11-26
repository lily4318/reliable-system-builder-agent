"""Offline provider request/response evidence reconciliation; NEVER invokes an API.

A valid normalized response is a LOCAL COPY, NOT a cryptographically authenticated
provider response. A dishonest runner can forge a mutually consistent manifest.
Independent, provider-controlled verification and human approval are separate.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

from src.llm_requirements_eval import ROOT, PUBLIC_DATASET, load_dataset, runner_payload
from src.llm_runner_preflight import audit as audit_runner

HEX = re.compile(r"^[0-9a-f]{64}$")
IDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$")
MANIFEST_FIELDS = frozenset((
    "schema_version", "split", "case_id", "dataset_sha256", "provider",
    "requested_model", "requested_model_version", "runner_sha256",
    "prompt_sha256", "evaluator_sha256", "harness_payload_sha256",
    "request_id", "response_id", "response_path", "response_sha256",
    "response_origin", "call_started_at_utc", "call_finished_at_utc",
    "authorization",
))
AUTH_FIELDS = frozenset((
    "scope", "approval_reference", "approved_by_ref", "approved_at_utc",
    "expires_at_utc", "data_handling_reviewed",
))
RESPONSE_FIELDS = frozenset((
    "provider", "model", "model_version", "request_id", "response_id",
    "created_at_utc", "status", "output",
))
MAX_BYTES = 131072


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(obj: object) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _private_json(path: Path) -> tuple[object, bytes] | None:
    path = Path(path)
    if not path.is_absolute() or path.is_symlink() or (
        path.resolve().is_relative_to(ROOT.resolve())
    ):
        return None
    try:
        if not path.is_file() or path.stat().st_size > MAX_BYTES:
            return None
        raw = path.read_bytes()
        return json.loads(raw), raw
    except (OSError, ValueError, UnicodeError):
        return None


def _utc(x: object) -> datetime | None:
    if not isinstance(x, str) or not x.endswith("Z"):
        return None
    try:
        dt = datetime.fromisoformat(x[:-1] + "+00:00")
        return dt if dt.utcoffset().total_seconds() == 0 else None
    except (ValueError, OverflowError, AttributeError):
        return None


def _string(x: object, size: int = 160) -> bool:
    return isinstance(x, str) and 0 < len(x) <= size and x == x.strip()


def _status(value: str) -> dict:
    return {
        "status": value,
        "evidence_type": "offline_local_normalized_copy_only",
        "local_integrity_consistent": False,
        "provider_origin_independently_verified": False,
        "model_version_provider_authenticated": False,
        "provider_response_id_independently_checked": False,
        "authorization_independently_verified": False,
        "actual_llm_executed_by_this_audit": False,
        "live_inference_authorized_by_this_audit": False,
        "actual_model_accuracy_measured": False,
    }


def audit_evidence(manifest_path: Path | None = None,
                   runner_config: Path | None = None) -> dict:
    """Strict local consistency checker. Never returns provider-authenticated."""
    if manifest_path is None or runner_config is None:
        return _status("BLOCKED_MISSING_PRIVATE_EVIDENCE_OR_CONFIG")
    if audit_runner(runner_config)["status"] != (
        "CONFIG_HASHES_MATCH_PROVIDER_AND_APPROVAL_STILL_UNVERIFIED"
    ):
        return _status("BLOCKED_RUNNER_CONFIG_OR_SOURCE_INTEGRITY")
    loaded = _private_json(manifest_path)
    config_loaded = _private_json(runner_config)
    if loaded is None or config_loaded is None:
        return _status("BLOCKED_PRIVATE_EVIDENCE_UNAVAILABLE")
    receipt, _ = loaded
    cfg, _ = config_loaded
    if not isinstance(receipt, dict) or set(receipt) != MANIFEST_FIELDS or (
        type(receipt.get("schema_version")) is not int or
        receipt["schema_version"] != 1 or receipt.get("split") != "public_dev"
    ):
        return _status("BLOCKED_EVIDENCE_SCHEMA_OR_SCOPE")
    auth = receipt.get("authorization")
    if not isinstance(auth, dict) or set(auth) != AUTH_FIELDS or (
        auth.get("scope") != "public_dev" or
        auth.get("data_handling_reviewed") is not True or
        not _string(auth.get("approval_reference")) or
        not _string(auth.get("approved_by_ref")) or
        auth["approval_reference"] != cfg["approval_reference"]
    ):
        return _status("BLOCKED_AUTHORIZATION_SCOPE_OR_REFERENCE")
    if not all(_string(receipt.get(k)) for k in (
        "provider", "requested_model", "requested_model_version"
    )):
        return _status("BLOCKED_MODEL_IDENTITY_DECLARATION")
    if receipt["provider"] != cfg["provider"] or (
        receipt["requested_model"] != cfg["model_id"]
    ):
        return _status("BLOCKED_REQUESTED_PROVIDER_OR_MODEL")
    hash_keys = ("runner_sha256", "prompt_sha256", "evaluator_sha256",
                 "dataset_sha256", "harness_payload_sha256", "response_sha256")
    if any(not isinstance(receipt.get(k), str) or
           not HEX.fullmatch(receipt[k]) for k in hash_keys):
        return _status("BLOCKED_HASH_FORMAT")
    if any(receipt[k] != cfg[k] for k in (
        "runner_sha256", "prompt_sha256", "evaluator_sha256"
    )):
        return _status("BLOCKED_SOURCE_HASH_MISMATCH")
    if not _string(receipt.get("case_id"), 12):
        return _status("BLOCKED_CASE_ID")
    if any(not isinstance(receipt.get(k), str) or
           not IDENT.fullmatch(receipt[k]) for k in ("request_id", "response_id")):
        return _status("BLOCKED_PROVIDER_REQUEST_RESPONSE_ID")
    if receipt.get("response_origin") != "unverified_local_normalized_copy":
        return _status("BLOCKED_FALSE_PROVIDER_ORIGIN_CLAIM")
    times = [_utc(auth.get(k)) for k in ("approved_at_utc", "expires_at_utc")]
    times += [_utc(receipt.get(k)) for k in (
        "call_started_at_utc", "call_finished_at_utc"
    )]
    if any(x is None for x in times) or not (
        times[0] < times[2] <= times[3] < times[1]
    ):
        return _status("BLOCKED_AUTHORIZATION_WINDOW_OR_CALL_ORDER")
    try:
        dataset, dataset_sha = load_dataset(PUBLIC_DATASET, split="public_dev")
    except (OSError, ValueError):
        return _status("BLOCKED_PUBLIC_DATASET_INVALID")
    if receipt["dataset_sha256"] != dataset_sha:
        return _status("BLOCKED_DATASET_SHA_MISMATCH")
    cases = [x for x in dataset["cases"] if x["id"] == receipt["case_id"]]
    if len(cases) != 1:
        return _status("BLOCKED_UNKNOWN_PUBLIC_CASE")
    payload_sha = _sha(_canonical(runner_payload(cases[0])))
    if payload_sha != receipt["harness_payload_sha256"]:
        return _status("BLOCKED_HARNESS_TO_RUNNER_PAYLOAD_SHA")
    if not isinstance(receipt.get("response_path"), str):
        return _status("BLOCKED_RESPONSE_PATH")
    normalized = _private_json(Path(receipt["response_path"]))
    if normalized is None:
        return _status("BLOCKED_RESPONSE_UNAVAILABLE_OR_PUBLIC")
    response, response_bytes = normalized
    if _sha(response_bytes) != receipt["response_sha256"]:
        return _status("BLOCKED_RESPONSE_BYTES_TAMPERED")
    if not isinstance(response, dict) or set(response) != RESPONSE_FIELDS or (
        response.get("status") != "completed"
    ):
        return _status("BLOCKED_NORMALIZED_RESPONSE_SCHEMA")
    if any(not _string(response.get(k)) for k in (
        "provider", "model", "model_version"
    )) or any(response.get(k) != receipt[k2] for k, k2 in (
        ("provider", "provider"), ("model", "requested_model"),
        ("model_version", "requested_model_version")
    )):
        return _status("BLOCKED_RESPONSE_MODEL_OR_VERSION_MISMATCH")
    if any(response.get(k) != receipt[k] for k in ("request_id", "response_id")):
        return _status("BLOCKED_REQUEST_RESPONSE_ID_MISMATCH")
    if not isinstance(response.get("output"), dict):
        return _status("BLOCKED_NORMALIZED_RESPONSE_OUTPUT")
    response_time = _utc(response.get("created_at_utc"))
    if response_time is None or not times[2] <= response_time <= times[3]:
        return _status("BLOCKED_RESPONSE_CHRONOLOGY")
    # Never print raw IDs/paths/output, only hashes of IDs and source fingerprints.
    return {
        **_status("MATCHED_LOCAL_EVIDENCE_PROVIDER_AND_APPROVAL_UNVERIFIED"),
        "local_integrity_consistent": True,
        "declared_model_version_unverified": receipt["requested_model_version"],
        "request_id_sha256": _sha(receipt["request_id"].encode("utf-8")),
        "response_id_sha256": _sha(receipt["response_id"].encode("utf-8")),
        "dataset_sha256": dataset_sha,
        "harness_payload_sha256": payload_sha,
        "prompt_sha256": receipt["prompt_sha256"],
        "runner_sha256": receipt["runner_sha256"],
        "evaluator_sha256": receipt["evaluator_sha256"],
        "response_sha256": receipt["response_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit",))
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--runner-config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-local-match", action="store_true")
    args = parser.parse_args()
    try:
        report = audit_evidence(args.manifest, args.runner_config)
        data = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        print(data)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(data, encoding="utf-8")
        return 2 if args.require_local_match and not report["local_integrity_consistent"] else 0
    except (ValueError, OSError, UnicodeError):
        print("PROVIDER_EVIDENCE_AUDIT_BLOCKED", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
