"""Read-only quality gate comparing current results with verified v0.1.0 baseline."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from src.agent_eval import evaluate as evaluate_policy
from src.independent_acceptance import evaluate as evaluate_recovery
from src.capability_workbench import evaluate as evaluate_capability
from src.website_scenario_eval import evaluate as evaluate_website

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "evaluations/baselines/v0.1.0-initial.json"
TARGETS = ROOT / "evaluations/quality-targets.json"

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def assess(policy: dict, recovery: dict, baseline: dict, targets: dict,
           capability: dict | None = None,
           website: dict | None = None) -> dict:
    if capability is None:
        capability = evaluate_capability()
    if website is None:
        website = evaluate_website()
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
        "capability_public_reference_contract":
            capability.get("task_count", 0) >= 5
            and capability.get("tasks_full_structural_score") == capability.get("task_count")
            and capability.get("mean_structural_score") == 100
            and targets.get("min_capability_reference_score") == 100
            and capability.get("unsafe_unverified_claim_count") == 0,
        "website_public_scenario_accuracy_gate":
            website.get("scenario_count",0) >= targets.get("min_website_scenario_types",6)
            and website.get("passed") == website.get("scenario_count")
            and website.get("failed") == 0
            and website.get("execution_kind") == "local_deterministic_generator_not_LLM",
        "website_no_false_model_or_release_claim":
            website.get("actual_LLM_execution_verified") is False
            and website.get("model_skill_improvement_demonstrated") is False
            and website.get("independent_blind_holdout") is False
            and website.get("formal_website_approval_granted") is False
            and targets.get("website_synthetic_tests_can_claim_model_skill") is False,
        "capability_no_false_real_agent_claim":
            capability.get("submission_kind") == "self_authored_reference_fixture_not_agent_result"
            and capability.get("independent_holdout_evaluated") is False
            and capability.get("real_llm_or_seven_agents_invoked") is False
            and capability.get("actual_program_correctness_evaluated") is False
            and capability.get("architecture_semantics_human_reviewed") is False
            and targets.get("self_authored_reference_may_claim_agent_skill") is False,
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
        "public_capability_tasks": capability["task_count"],
        "self_authored_reference_structural_score": capability["mean_structural_score"],
        "website_public_scenario_count": website["scenario_count"],
        "website_public_scenarios_passed": website["passed"],
        "website_actual_llm_performance_verified": False,
        "actual_autonomous_agent_performance_verified": False,
        "human_approval_completed": False,
        "formal_release_created": False,
        "scope": "public_offline_policy_recovery_and_structural_capability_reference_only",
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
