"""Deterministic *structured* task-scope guard, NOT natural-language understanding.

The caller must label the LATEST explicit user request and verify it against
the source. This program does not infer intent from untrusted conversation text.
It never accesses another repository or performs any write.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluations/cases/task_scope.json"
DECISIONS = {
    "HOLD_INTENT", "HOLD_TARGET", "BLOCK_CROSS_PROJECT_WRITE",
    "HOLD_WEIGHT_TRAINING", "AGENT_READ_ONLY", "AGENT_CANDIDATE_PR_ONLY",
    "PROJECT_READ_ONLY", "PROJECT_PATCH_ONLY",
}
REPO_PATTERN = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")


def decide_scope(s: dict) -> str:
    """Check explicit authorization and target *after* user-intent verification."""
    if not isinstance(s, dict) or s.get("intent_confirmed_from_latest_user") is not True:
        return "HOLD_INTENT"
    intent = s.get("intent")
    if intent not in ("improve_agent", "apply_agent"):
        return "HOLD_INTENT"
    agent = s.get("agent_repo")
    target = s.get("target_repo")
    proposed = s.get("proposed_write_repo")
    if not isinstance(agent, str) or not REPO_PATTERN.fullmatch(agent):
        return "HOLD_TARGET"
    if not isinstance(target, str) or not REPO_PATTERN.fullmatch(target):
        return "HOLD_TARGET"
    if proposed is not None and (not isinstance(proposed, str) or not REPO_PATTERN.fullmatch(proposed)):
        return "HOLD_TARGET"

    if intent == "improve_agent":
        if target != agent:
            return "HOLD_TARGET"
        if proposed is not None and proposed != agent:
            return "BLOCK_CROSS_PROJECT_WRITE"
        if s.get("requests_weight_training") is True:
            # A prompt or policy change is NOT an LLM weight fine-tune.
            return "HOLD_WEIGHT_TRAINING"
        if s.get("write_authorized") is True:
            return "AGENT_CANDIDATE_PR_ONLY" if proposed == agent else "HOLD_TARGET"
        return "AGENT_READ_ONLY"

    # Application of an Agent to a different target project is a separate task.
    if target == agent:
        return "HOLD_TARGET"
    if proposed is not None and proposed != target:
        return "BLOCK_CROSS_PROJECT_WRITE"
    if s.get("write_authorized") is True:
        return "PROJECT_PATCH_ONLY" if proposed == target else "HOLD_TARGET"
    return "PROJECT_READ_ONLY"


def load_cases(path: Path = DATASET) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("synthetic_or_sanitized") is not True:
        raise ValueError("unsupported or unsanitized task-scope dataset")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 12:
        raise ValueError("insufficient task-scope cases")
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("scenario"), dict):
            raise ValueError("invalid task-scope case")
        cid = case.get("id")
        if not isinstance(cid, str) or re.fullmatch(r"S[0-9]{3}", cid) is None or cid in seen:
            raise ValueError("duplicated or invalid task-scope ID")
        seen.add(cid)
        if case.get("expected") not in DECISIONS or type(case.get("critical")) is not bool:
            raise ValueError("invalid expected task-scope decision")
        if not isinstance(case.get("example_utterance"), str) or not case["example_utterance"].strip():
            raise ValueError("missing human-readable example")
    if sum(c["critical"] for c in cases) < 8:
        raise ValueError("insufficient critical task-scope cases")
    return cases


def evaluate(path: Path = DATASET) -> dict:
    cases = load_cases(path)
    rows = []
    for case in cases:
        predicted = decide_scope(case["scenario"])
        rows.append({"id": case["id"], "expected": case["expected"],
                     "actual": predicted, "critical": case["critical"],
                     "passed": predicted == case["expected"]})
    critical = [x for x in rows if x["critical"]]
    passed = sum(x["passed"] for x in rows)
    critical_passed = sum(x["passed"] for x in critical)
    return {"evaluation_type": "structured_explicit_scope_guard_not_llm_intent_test",
            "total": len(rows), "passed": passed, "failed": len(rows) - passed,
            "critical_total": len(critical), "critical_passed": critical_passed,
            "natural_language_intent_accuracy_measured": False,
            "independent_blind_holdout": False,
            "gate_passed": passed == len(rows) and critical_passed == len(critical),
            "cases": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "evaluate"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = ({"valid": True, "cases": len(load_cases())}
                  if args.command == "validate" else evaluate())
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        print(rendered)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        return 0 if args.command == "validate" or report["gate_passed"] else 1
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("TASK_SCOPE_EVALUATION_BLOCKED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
