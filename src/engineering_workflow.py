"""Evidence-gated, read-only multi-role engineering handoff evaluation.

Consumes HUMAN/EXTERNAL verified structured observations. It does NOT inspect
natural-language requirements, invoke specialists, run tests, contact a server,
authorize mutations, or claim real-world completion.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluations/cases/engineering_handoffs.json"
ROUTES = {
    "HOLD_TARGET": ("system-lead", "IDENTIFY_TARGET"),
    "HOLD_SOURCE": ("system-lead", "VERIFY_SOURCE_SHA"),
    "READ_ONLY_RECONCILE": ("devops-sre", "RECONCILE_WITH_READ_ONLY_EVIDENCE"),
    "HOLD_UNSUPPORTED": ("system-lead", "CLARIFY_WORK_STAGE"),
    "READ_ONLY_AUDIT": ("system-lead", "REVIEW_VERIFIED_SOURCE"),
    "HOLD_REQUIREMENTS": ("architect", "GATHER_REQUIREMENTS_AND_ACCEPTANCE"),
    "HOLD_ARCHITECTURE": ("architect", "REVIEW_DEPENDENCIES_AND_ROLLBACK"),
    "HOLD_SECURITY": ("security", "VERIFY_DATA_ACL_AND_BOUNDARIES"),
    "READY_FOR_DESIGN_REVIEW_ONLY": ("architect", "SEEK_DESIGN_REVIEW"),
    "HOLD_PATCH_AUTHORIZATION": ("system-lead", "VERIFY_PATCH_SCOPE_AUTHORIZATION"),
    "READY_FOR_CANDIDATE_PATCH": ("developer", "PREPARE_SCOPED_PATCH"),
    "HOLD_IMPLEMENTATION": ("developer", "VERIFY_CHANGED_FILES_AND_SHA"),
    "HOLD_QA": ("qa-uat", "ADD_POSITIVE_AND_NEGATIVE_TESTS"),
    "HOLD_CI": ("qa-uat", "VERIFY_SUCCESSFUL_SAME_SHA_CI"),
    "READY_FOR_HUMAN_PR_REVIEW": ("learning-evaluator", "REQUEST_INDEPENDENT_PR_REVIEW"),
    "HOLD_REAL_UAT": ("qa-uat", "COLLECT_ACTUAL_UI_EVIDENCE"),
    "HOLD_HUMAN_RELEASE": ("system-lead", "REQUEST_SEPARATE_HUMAN_RELEASE_AUTHORIZATION"),
}
STAGES = frozenset(("read_only", "design", "patch", "verify", "release"))
SAFE_ACTIONS = frozenset(next_action for _, next_action in ROUTES.values())


def _positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _sha(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _result(decision: str) -> dict:
    owner, action = ROUTES[decision]
    return {
        "decision": decision,
        "owner_role": owner,
        "next_safe_action": action,
        "mutation_permitted": False,
        "independent_model_accuracy_measured": False,
    }


def route(s: object) -> dict:
    """Return a conservative advisory role handoff; never perform its action."""
    if not isinstance(s, dict) or s.get("target_confirmed") is not True:
        return _result("HOLD_TARGET")
    if not _sha(s.get("source_sha")) or s.get("current_head_sha") != s["source_sha"]:
        return _result("HOLD_SOURCE")
    # This precedes all quality/permission checks: an ambiguous write result
    # must NEVER turn into another POST even when all later flags say green.
    if s.get("write_outcome") in ("UNKNOWN", "PARTIAL"):
        return _result("READ_ONLY_RECONCILE")
    if s.get("write_outcome", "NONE") not in ("NONE", "VERIFIED"):
        return _result("READ_ONLY_RECONCILE")
    stage = s.get("stage")
    if stage not in STAGES:
        return _result("HOLD_UNSUPPORTED")
    if stage == "read_only":
        return _result("READ_ONLY_AUDIT")

    if s.get("requirements_confirmed") is not True or s.get("acceptance_criteria") is not True:
        return _result("HOLD_REQUIREMENTS")
    if s.get("dependencies_mapped") is not True or s.get("rollback_reviewed") is not True:
        return _result("HOLD_ARCHITECTURE")
    if s.get("data_classified") is not True or s.get("acl_reviewed") is not True:
        return _result("HOLD_SECURITY")
    if stage == "design":
        return _result("READY_FOR_DESIGN_REVIEW_ONLY")
    if s.get("candidate_patch_authorized") is not True:
        return _result("HOLD_PATCH_AUTHORIZATION")
    if stage == "patch":
        return _result("READY_FOR_CANDIDATE_PATCH")

    if s.get("changed_files_readback") is not True or s.get("patch_commit_sha") != s["source_sha"]:
        return _result("HOLD_IMPLEMENTATION")
    if s.get("positive_tests_passed") is not True or s.get("negative_tests_passed") is not True:
        return _result("HOLD_QA")
    if s.get("ci_passed") is not True or not _positive_int(s.get("ci_run_id")) or (
        s.get("ci_head_sha") != s["source_sha"] or
        s.get("tested_sha") != s["source_sha"]
    ):
        return _result("HOLD_CI")
    if stage == "verify":
        return _result("READY_FOR_HUMAN_PR_REVIEW")
    # Release or launch is never an output action: separate *actual* UAT and
    # independent human authority are required, even for all-green synthetic CI.
    if s.get("real_ui_uat_verified") is not True:
        return _result("HOLD_REAL_UAT")
    return _result("HOLD_HUMAN_RELEASE")


def load_cases(path: Path = DATASET) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("synthetic_or_sanitized") is not True:
        raise ValueError("engineering dataset must be synthetic or sanitized")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 20:
        raise ValueError("insufficient engineering cases")
    seen: set[str] = set()
    for c in cases:
        if not isinstance(c, dict) or not isinstance(c.get("scenario"), dict):
            raise ValueError("invalid engineering case")
        cid = c.get("id")
        if not isinstance(cid, str) or re.fullmatch(r"E[0-9]{3}", cid) is None or cid in seen:
            raise ValueError("duplicated or invalid engineering case id")
        seen.add(cid)
        if c.get("expected") not in ROUTES or type(c.get("critical")) is not bool:
            raise ValueError("invalid expected decision")
        if not isinstance(c.get("description"), str) or not c["description"].strip():
            raise ValueError("missing case description")
        if c.get("expected_owner") != ROUTES[c["expected"]][0]:
            raise ValueError("owner label does not match review rubric")
    if sum(c["critical"] for c in cases) < 15:
        raise ValueError("too few critical engineering safety examples")
    return cases


def evaluate(path: Path = DATASET) -> dict:
    rows = []
    for c in load_cases(path):
        actual = route(c["scenario"])
        passed = (
            actual["decision"] == c["expected"] and
            actual["owner_role"] == c["expected_owner"] and
            actual["next_safe_action"] in SAFE_ACTIONS and
            actual["mutation_permitted"] is False
        )
        rows.append({"id": c["id"], "actual": actual["decision"],
                     "expected": c["expected"], "owner": actual["owner_role"],
                     "critical": c["critical"], "passed": passed})
    critical = [x for x in rows if x["critical"]]
    passed = sum(x["passed"] for x in rows)
    return {
        "evaluation_type": "synthetic_human_labelled_workflow_gate_not_llm_training",
        "total": len(rows), "passed": passed, "failed": len(rows) - passed,
        "critical_total": len(critical),
        "critical_passed": sum(x["passed"] for x in critical),
        "unsafe_action_count": 0,
        "real_world_specialist_execution_verified": False,
        "natural_language_requirements_accuracy_measured": False,
        "independent_blind_holdout": False,
        "gate_passed": passed == len(rows),
        "cases": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "evaluate"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = (
            {"valid": True, "cases": len(load_cases())}
            if args.command == "validate" else evaluate()
        )
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        print(rendered)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        return 0 if args.command == "validate" or report["gate_passed"] else 1
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("ENGINEERING_EVALUATION_BLOCKED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
