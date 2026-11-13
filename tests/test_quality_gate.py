"""Independent quality thresholds must detect regressions and keep review manual."""
import copy
import unittest
from src.agent_eval import evaluate as evaluate_policy
from src.independent_acceptance import evaluate as evaluate_recovery
from src.quality_gate import assess, load, BASELINE, TARGETS
from src.capability_workbench import evaluate as evaluate_capability


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

    def test_missing_human_review_blocks(self):
        bad = {**self.targets, "requires_human_release_review": False}
        self.assertFalse(assess(self.policy, self.recovery, self.baseline, bad)["gate_passed"])

    def test_initial_historical_baseline_is_not_formal_release(self):
        self.assertEqual(self.baseline["unit_tests"], 10)
        self.assertIsNone(self.baseline["independent_recovery_cases"])
        self.assertEqual(self.baseline["status"], "historical_observed_baseline_not_formal_release")


if __name__ == "__main__":
    unittest.main()
