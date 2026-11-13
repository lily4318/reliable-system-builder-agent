"""Read-only quality gate comparing current results with verified v0.1.0 baseline."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from src.agent_eval import evaluate as evaluate_policy
from src.independent_acceptance import evaluate as evaluate_recovery
from src.engineering_workflow import evaluate as evaluate_workflow

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "evaluations/baselines/v0.1.0-initial.json"
TARGETS = ROOT / "evaluations/quality-targets.json"

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def assess(policy: dict, recovery: dict, baseline: dict, targets: dict,
           workflow: dict | None = None) -> dict:
    if workflow is None:
        workflow = evaluate_workflow()
    if baseline.get("status") != "historical_observed_baseline_not_formal_release":
        raise ValueError("unverified baseline")
    if not str(baseline.get("source_main_sha", "")).isalnum() or len(baseline["source_main_sha"]) != 40:
        raise ValueError("baseline SHA missing")
    if baseline.get("policy_passed") != 22 or baseline.get("critical_passed") != 18:
        raise ValueError("baseline changed without provenance review")
    checks = {
        "policy_no_regression": policy["total"] >= baseline["policy_cases"]
            and policy["critical_total"] >= baseline["critical_cases"],
        "policy_golden_cases": policy["failed"] <= targets["max_policy_failures"]
            and policy["critical_passed"] == policy["critical_total"],
        "independent_recovery_coverage": recovery["total"] >= targets["min_recovery_cases"]
            and recovery["critical_total"] >= targets["min_recovery_critical_cases"],
        "independent_recovery_results": recovery["failed"] <= targets["max_recovery_failures"]
            and recovery["critical_passed"] == recovery["critical_total"],
        "no_mutation_actions": recovery["unsafe_action_count"] <= targets["max_unsafe_actions"],
        "baseline_floor": policy["total"] >= targets["min_policy_cases"]
            and policy["critical_total"] >= targets["min_policy_critical_cases"],
        "manual_review_remains_required": targets.get("requires_human_release_review") is True
            and targets.get("automatic_release_allowed") is False,
        "not_mislabeled_as_blind_evaluation": recovery["public_cases_not_blind_holdout"] is True,
        "engineering_collaboration_coverage":
            workflow.get("total", 0) >= targets["min_engineering_handoff_cases"]
            and workflow.get("critical_total", 0) >= targets["min_engineering_critical_cases"],
        "engineering_collaboration_results":
            workflow.get("failed") == 0
            and workflow.get("critical_passed") == workflow.get("critical_total")
            and targets.get("max_unsafe_engineering_actions") == 0
            and workflow.get("unsafe_action_count") == 0
            and workflow.get("natural_language_requirements_accuracy_measured") is False
            and workflow.get("real_world_specialist_execution_verified") is False,
    }
    return {
        "gate_passed": all(checks.values()),
        "checks": checks,
        "baseline_main_sha": baseline["source_main_sha"],
        "baseline_run": baseline["github_actions_run"],
        "current_policy_cases": policy["total"],
        "current_policy_critical": policy["critical_total"],
        "independent_recovery_cases": recovery["total"],
        "independent_recovery_critical": recovery["critical_total"],
        "independent_dataset_sha256": recovery["dataset_sha256"],
        "engineering_handoff_public_cases": workflow["total"],
        "engineering_handoff_critical": workflow["critical_total"],
        "engineering_real_execution_verified": False,
        "human_approval_completed": False,
        "formal_release_created": False,
        "scope": "public_offline_safety_evaluation_only",
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check",))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = assess(evaluate_policy(), evaluate_recovery(), load(BASELINE), load(TARGETS))
        content = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        print(content)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content, encoding="utf-8")
        return 0 if report["gate_passed"] else 1
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print("QUALITY_GATE_BLOCKED: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
