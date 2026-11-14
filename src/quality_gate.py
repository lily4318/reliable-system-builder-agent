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
from src.website_holdout_compare import protocol_contract
from src.task_scope import evaluate as evaluate_task_scope
from src.engineering_workflow import evaluate as evaluate_workflow
from src.llm_requirements_eval import load_dataset as validate_llm_protocol

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "evaluations/baselines/v0.1.0-initial.json"
TARGETS = ROOT / "evaluations/quality-targets.json"

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def assess(policy: dict, recovery: dict, baseline: dict, targets: dict,
           capability: dict | None = None,
           website: dict | None = None, scope: dict | None = None,
           workflow: dict | None = None) -> dict:
    if scope is None:
        scope = evaluate_task_scope()
    if workflow is None:
        workflow = evaluate_workflow()
    llm_dev, llm_dev_sha = validate_llm_protocol()
    llm_critical = sum(case['critical'] for case in llm_dev['cases'])
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
        "agent_vs_project_scope_cases": scope.get("total", 0) >= targets["min_task_scope_cases"]
            and scope.get("critical_total", 0) >= targets["min_task_scope_critical_cases"],
        "agent_vs_project_scope_correct": scope.get("failed") == 0
            and scope.get("critical_passed") == scope.get("critical_total")
            and scope.get("natural_language_intent_accuracy_measured") is False,
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
        "llm_eval_protocol_and_dev_labels_valid":
            len(llm_dev["cases"]) >= targets["min_llm_public_dev_cases"]
            and llm_critical >= targets["min_llm_public_dev_critical_cases"]
            and llm_dev["independent_blind_holdout"] is False
            and llm_dev["label_status"] == "provisional_synthetic_author_labels_pending_independent_review",
        "llm_real_model_claims_disabled":
            targets.get("llm_model_accuracy_without_runner_allowed") is False
            and targets.get("llm_public_dev_as_blind_holdout_allowed") is False,
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
        "private_holdout_protocol_no_false_skill_or_release_claim":
            protocol_contract().get("required_independent_raters_per_artifact")==2
            and protocol_contract().get("minimum_private_unseen_case_count")>=5
            and len(protocol_contract().get("dimensions", []))>=5
            and protocol_contract().get("third_rater_required_if_score_gap_at_least")==2
            and protocol_contract().get("before_after_same_model_runner_and_budget") is True
            and protocol_contract().get("case_text_not_in_public_repository") is True
            and protocol_contract().get("case_independence_independently_verified") is False
            and protocol_contract().get("real_model_or_agent_run_verified") is False
            and protocol_contract().get("automatic_release_allowed") is False
            and protocol_contract().get("synthetic_tests_measure_real_skill") is False
            and targets.get("private_holdout_synthetic_tests_can_claim_skill") is False,
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
        "private_holdout_actual_model_run_verified": False,
        "private_holdout_real_improvement_verified": False,
        "actual_autonomous_agent_performance_verified": False,
        "task_scope_public_cases": scope["total"],
        "task_scope_public_critical": scope["critical_total"],
        "task_scope_intent_accuracy_measured": False,
        "engineering_handoff_public_cases": workflow["total"],
        "engineering_handoff_critical": workflow["critical_total"],
        "engineering_real_execution_verified": False,
        "llm_dev_protocol_cases": len(llm_dev["cases"]),
        "llm_dev_protocol_critical": llm_critical,
        "llm_dev_dataset_sha256": llm_dev_sha,
        "actual_llm_model_accuracy_measured": False,
        "independent_llm_holdout_executed": False,
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
