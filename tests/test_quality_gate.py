"""Independent quality thresholds must detect regressions and keep review manual."""
import copy
import unittest
from src.agent_eval import evaluate as evaluate_policy
from src.independent_acceptance import evaluate as evaluate_recovery
from src.quality_gate import assess, load, BASELINE, TARGETS
from src.capability_workbench import evaluate as evaluate_capability
from src.website_scenario_eval import evaluate as evaluate_website
from src.website_holdout_compare import protocol_contract


class QualityGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load(BASELINE)
        cls.targets = load(TARGETS)
        cls.policy = evaluate_policy()
        cls.recovery = evaluate_recovery()

    def test_candidate_passes_all_objective_offline_gates(self):
        result = assess(self.policy, self.recovery, self.baseline, self.targets)
        self.assertTrue(result["gate_passed"], result)
        self.assertFalse(result["human_approval_completed"])
        self.assertFalse(result["formal_release_created"])

    def test_fewer_regression_cases_blocks(self):
        weak = copy.deepcopy(self.policy)
        weak["total"] = self.baseline["policy_cases"] - 1
        self.assertFalse(assess(weak, self.recovery, self.baseline, self.targets)["gate_passed"])

    def test_independent_failure_blocks(self):
        bad = {**self.recovery, "failed": 1}
        self.assertFalse(assess(self.policy, bad, self.baseline, self.targets)["gate_passed"])

    def test_unsafe_recommendation_blocks(self):
        bad = {**self.recovery, "unsafe_action_count": 1}
        self.assertFalse(assess(self.policy, bad, self.baseline, self.targets)["gate_passed"])

    def test_critical_recovery_regression_blocks(self):
        bad = {**self.recovery, "critical_passed": self.recovery["critical_total"] - 1}
        self.assertFalse(assess(self.policy, bad, self.baseline, self.targets)["gate_passed"])

    def test_structural_capability_reference_cannot_be_weakened(self):
        cap = evaluate_capability()
        self.assertTrue(assess(self.policy, self.recovery, self.baseline,
                               self.targets, capability=cap)["gate_passed"])
        self.assertFalse(assess(self.policy, self.recovery, self.baseline,
                                self.targets, capability={**cap, "mean_structural_score": 80})["gate_passed"])
        self.assertFalse(assess(self.policy, self.recovery, self.baseline,
                                {**self.targets, "min_capability_reference_score": 50})["gate_passed"])
        self.assertFalse(assess(self.policy, self.recovery, self.baseline,
                                {**self.targets, "self_authored_reference_may_claim_agent_skill": True})["gate_passed"])
        self.assertFalse(assess(self.policy, self.recovery, self.baseline,
                                self.targets, capability={**cap, "real_llm_or_seven_agents_invoked": True})["gate_passed"])

    def test_website_scenario_gate_rejects_missing_and_failed_cases(self):
        website=evaluate_website()
        self.assertTrue(assess(self.policy,self.recovery,self.baseline,
                               self.targets,website=website)["gate_passed"])
        for change in ({"failed":1}, {"passed":website["passed"]-1},
                       {"scenario_count":4},
                       {"execution_kind":"real_model_proven"}):
            altered={**website,**change}
            self.assertFalse(assess(self.policy,self.recovery,self.baseline,
                                    self.targets,website=altered)["gate_passed"])

    def test_website_synthetic_test_cannot_claim_real_model_skill(self):
        website=evaluate_website()
        for key in ("actual_LLM_execution_verified",
                    "model_skill_improvement_demonstrated",
                    "formal_website_approval_granted","independent_blind_holdout"):
            altered={**website,key:True}
            self.assertFalse(assess(self.policy,self.recovery,self.baseline,
                                    self.targets,website=altered)["gate_passed"])
        weak={**self.targets,"website_synthetic_tests_can_claim_model_skill":True}
        self.assertFalse(assess(self.policy,self.recovery,self.baseline,
                                weak,website=website)["gate_passed"])

    def test_offline_holdout_protocol_must_not_be_treated_as_model_skill(self):
        p=protocol_contract()
        self.assertEqual(p["minimum_private_unseen_case_count"],5)
        self.assertEqual(p["required_independent_raters_per_artifact"],2)
        self.assertFalse(p["real_model_or_agent_run_verified"])
        self.assertFalse(p["case_independence_independently_verified"])
        self.assertFalse(p["synthetic_tests_measure_real_skill"])
        self.assertTrue(assess(self.policy,self.recovery,self.baseline,
                               self.targets)["gate_passed"])
        weak={**self.targets,"private_holdout_synthetic_tests_can_claim_skill":True}
        self.assertFalse(assess(self.policy,self.recovery,self.baseline,
                                weak)["gate_passed"])

    def test_missing_human_review_blocks(self):
        bad = {**self.targets, "requires_human_release_review": False}
        self.assertFalse(assess(self.policy, self.recovery, self.baseline, bad)["gate_passed"])

    def test_initial_historical_baseline_is_not_formal_release(self):
        self.assertEqual(self.baseline["unit_tests"], 10)
        self.assertIsNone(self.baseline["independent_recovery_cases"])
        self.assertEqual(self.baseline["status"], "historical_observed_baseline_not_formal_release")


if __name__ == "__main__":
    unittest.main()
