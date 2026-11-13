"""Offline Agent task packet and submission importer (no model or code execution).

Prepare B001-B005 packets without reference answers; import independently produced
candidate artifacts plus Python source into a NEW private workspace; run AST-only
structural assessment. A user-supplied run_id or model_id is NEVER proof an Agent
executed. Public CI uses only synthetic protocol fixtures.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from src.capability_prompts import task_prompt
from src.capability_workbench import (
    ROOT, TASKS, REFERENCE, evaluate, load_submissions, load_tasks,
)

MAX_BUNDLE_BYTES = 1024 * 1024
MAX_SOURCE_CHARS = 65536
IDS = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.:-]{7,127}$")
BLOCK_CODES = frozenset(("NO_AUTHORIZED_RUNNER", "RUNNER_FAILED", "OUTPUT_WITHHELD"))
SUBMISSION_FIELDS = frozenset((
    "task_id", "requirements", "architecture", "plan", "implementation",
    "qa", "handoffs", "risk", "claims",
))


def _serialize(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def _sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _permitted_directory(path: Path) -> Path:
    path = Path(path).absolute()
    target = path.resolve()
    if target.is_relative_to(ROOT.resolve()) and not target.is_relative_to(
        (ROOT / "output").resolve()
    ):
        raise ValueError("generated files must stay outside repository or under ignored output/")
    if path.is_symlink() or path.exists() or not path.parent.is_dir():
        raise ValueError("output directory must be new, non-symlink, with existing parent")
    return path


def _read_json(path: Path, limit: int = MAX_BUNDLE_BYTES) -> dict:
    p = Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > limit:
        raise ValueError("input unavailable, symlinked or too large")
    value = json.loads(p.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    return value


def _write_json(path: Path, value: dict) -> None:
    with path.open("xb") as output:
        output.write(_serialize(value))


def prepare_all(output_dir: Path) -> dict:
    root = _permitted_directory(output_dir)
    tasks = load_tasks()
    packets = {case["id"]: task_prompt(case["id"]) for case in tasks}
    sha = {k: _sha(_serialize(v)) for k, v in packets.items()}
    manifest = {
        "schema_version": 1,
        "kind": "public_synthetic_agent_assignment_packets",
        "public_task_dataset_sha256": _sha(TASKS.read_bytes()),
        "packet_sha256": sha,
        "real_agent_executed": False,
        "model_runner_configured_or_authorized": False,
        "holdout_included": False,
    }
    root.mkdir(mode=0o700)
    for task_id, packet in packets.items():
        _write_json(root / (task_id + ".json"), packet)
    _write_json(root / "manifest.json", manifest)
    return {
        "status": "PREPARED_NO_AGENT_INVOKED", "task_count": len(packets),
        "task_ids": sorted(packets),
        "public_task_dataset_sha256": manifest["public_task_dataset_sha256"],
        "actual_agent_runs_verified": 0,
        "actual_program_execution": False,
    }


def _verify_packets(directory: Path) -> dict[str, str]:
    base = Path(directory)
    if base.is_symlink() or not base.is_dir():
        raise ValueError("task packets directory missing or symlinked")
    manifest = _read_json(base / "manifest.json", 32768)
    if set(manifest) != {
        "schema_version", "kind", "public_task_dataset_sha256", "packet_sha256",
        "real_agent_executed", "model_runner_configured_or_authorized",
        "holdout_included",
    } or manifest["schema_version"] != 1 or (
        manifest["kind"] != "public_synthetic_agent_assignment_packets"
    ) or any(manifest[k] is not False for k in (
        "real_agent_executed", "model_runner_configured_or_authorized",
        "holdout_included",
    )):
        raise ValueError("task packet manifest is not a no-run public packet set")
    tasks = load_tasks()
    expected = {t["id"]: _sha(_serialize(task_prompt(t["id"]))) for t in tasks}
    if manifest["public_task_dataset_sha256"] != _sha(TASKS.read_bytes()) or (
        manifest["packet_sha256"] != expected
    ):
        raise ValueError("stale or altered public task manifest")
    for key, digest in expected.items():
        packet = base / (key + ".json")
        if packet.is_symlink() or not packet.is_file() or (
            _sha(packet.read_bytes()) != digest
        ):
            raise ValueError("task packet missing or altered")
    return expected


def _completed(row: dict, known: dict[str, str], reference: dict) -> tuple[dict, str]:
    if set(row) != {
        "task_id", "status", "packet_sha256", "run_id", "model_id",
        "submission", "implementation_source",
    }:
        raise ValueError("completed result must have exact public contract fields")
    if row["packet_sha256"] != known[row["task_id"]]:
        raise ValueError("task packet digest mismatch")
    if any(not isinstance(row[k], str) or not IDS.fullmatch(row[k])
           for k in ("run_id", "model_id")):
        raise ValueError("run/model identifier invalid or missing")
    item = row["submission"]
    if not isinstance(item, dict) or set(item) != SUBMISSION_FIELDS or (
        item.get("task_id") != row["task_id"]
    ):
        raise ValueError("submission schema or task identity mismatch")
    claims = item.get("claims")
    if not isinstance(claims, dict) or set(claims) != {
        "real_agent_invoked", "model_weights_trained", "system_deployed"
    } or any(value is not False for value in claims.values()):
        raise ValueError("unverified agent/training/deployment claims must be false")
    # Prevent the bundled self-authored answer from masquerading as a model result.
    if _serialize(item) == _serialize(reference[row["task_id"]]):
        raise ValueError("copied self-authored reference is not an agent submission")
    source = row["implementation_source"]
    if not isinstance(source, str) or not (
        1 <= len(source) <= MAX_SOURCE_CHARS
    ) or "\x00" in source:
        raise ValueError("candidate source missing, too large, or invalid")
    # Untrusted implementation.path supplied by the model is NOT used as a path.
    normalized = dict(item)
    normalized["implementation"] = {
        "path": "implementations/" + row["task_id"] + ".py",
        "function": item.get("implementation", {}).get("function")
        if isinstance(item.get("implementation"), dict) else None,
    }
    return normalized, source


def import_results(packets_dir: Path, bundle_path: Path,
                   output_dir: Path) -> dict:
    known = _verify_packets(packets_dir)
    bundle = _read_json(bundle_path)
    if set(bundle) != {"schema_version", "kind", "attempt_label", "results"} or (
        bundle["schema_version"] != 1 or bundle["kind"] not in (
            "externally_supplied_agent_outputs_unverified",
            "synthetic_protocol_test",
        )
    ) or not isinstance(bundle.get("attempt_label"), str) or (
        not IDS.fullmatch(bundle["attempt_label"])
    ):
        raise ValueError("external results bundle format invalid")
    rows = bundle["results"]
    if not isinstance(rows, list) or not rows or len(rows) > len(known):
        raise ValueError("invalid number of task results")
    refs = {r["task_id"]: r for r in load_submissions(REFERENCE)}
    seen_tasks, seen_runs = set(), set()
    completed: list[tuple[dict, str]] = []
    blocked = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid task result")
        task_id = row.get("task_id")
        if task_id not in known or task_id in seen_tasks:
            raise ValueError("unknown or duplicated task result")
        seen_tasks.add(task_id)
        if row.get("status") == "completed":
            normalized, source = _completed(row, known, refs)
            if row["run_id"] in seen_runs:
                raise ValueError("duplicate execution run ID")
            seen_runs.add(row["run_id"])
            completed.append((normalized, source))
        elif row.get("status") == "blocked":
            if set(row) != {"task_id", "status", "packet_sha256", "reason_code"} or (
                row["packet_sha256"] != known[task_id] or
                row["reason_code"] not in BLOCK_CODES
            ):
                raise ValueError("blocked task record must be explicit and exact")
            blocked.append({"task_id": task_id, "reason_code": row["reason_code"]})
        else:
            raise ValueError("unsupported execution status")
    target = _permitted_directory(output_dir)
    # Nothing is written until the entire untrusted bundle passes validation.
    target.mkdir(mode=0o700)
    (target / "implementations").mkdir(mode=0o700)
    for item, source in completed:
        with (target / item["implementation"]["path"]).open("x", encoding="utf-8") as f:
            f.write(source)
    _write_json(target / "submissions.json", {
        "schema_version": 1, "submissions": [i for i, _ in completed],
    }) if completed else None
    structural = (
        evaluate(target / "submissions.json", root=target) if completed else None
    )
    summary = {
        "status": "EXTERNAL_AGENT_OUTPUT_UNVERIFIED_REVIEW_REQUIRED"
        if bundle["kind"] == "externally_supplied_agent_outputs_unverified"
        else "SYNTHETIC_PROTOCOL_TEST_ONLY",
        "bundle_kind": bundle["kind"],
        "task_ids_expected": sorted(known),
        "task_count_completed": len(completed),
        "task_count_blocked": len(blocked) + len(known) - len(seen_tasks),
        "task_ids_missing": sorted(set(known) - seen_tasks),
        "blocked": blocked,
        "structural_assessment_kind": "public_development_AST_only_not_model_or_functional_accuracy",
        "structural_score": structural["mean_structural_score"] if structural else None,
        "cases": structural["cases"] if structural else [],
        "self_authored_reference_used_as_submission": False,
        "actual_agent_model_execution_verified": False,
        "actual_seven_agent_handoffs_verified": False,
        "code_executed_or_imported": False,
        "program_semantics_verified": False,
        "hidden_holdout_used": False,
        "real_agent_skill_gain_demonstrated": False,
        "human_review_required": True,
        "deployment_or_release_authorized": False,
    }
    _write_json(target / "report.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--output-dir", type=Path, required=True)
    consume = commands.add_parser("ingest")
    consume.add_argument("--packets-dir", type=Path, required=True)
    consume.add_argument("--bundle", type=Path, required=True)
    consume.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = prepare_all(args.output_dir) if args.command == "prepare" else (
            import_results(args.packets_dir, args.bundle, args.output_dir)
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, UnicodeError,
            json.JSONDecodeError) as exc:
        # Only a fixed status; never echo private paths or untrusted contents.
        print("CAPABILITY_EXECUTION_BLOCKED: invalid or unavailable offline input",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
