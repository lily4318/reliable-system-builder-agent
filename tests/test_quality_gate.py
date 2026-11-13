"""Independent quality thresholds must detect regressions and keep review manual."""
import copy
import unittest
from src.agent_eval import evaluate as evaluate_policy
from src.independent_acceptance import evaluate as evaluate_recovery
from src.quality_gate import assess, load, BASELINE, TARGETS
from src.engineering_workflow import evaluate as evaluate_workflow


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

    def test_engineering_handoff_regression_blocks_candidate(self):
        report = evaluate_workflow()
        self.assertFalse(assess(self.policy, self.recovery, self.baseline,
                                self.targets, workflow={**report, "failed": 1})["gate_passed"])
        self.assertFalse(assess(self.policy, self.recovery, self.baseline,
                                self.targets, workflow={**report, "critical_passed": 0})["gate_passed"])
        self.assertFalse(assess(self.policy, self.recovery, self.baseline,
                                self.targets, workflow={**report, "unsafe_action_count": 1})["gate_passed"])
        self.assertFalse(assess(self.policy, self.recovery, self.baseline,
                                self.targets, workflow={**report, "total": 0})["gate_passed"])

    def test_permissive_engineering_safety_threshold_is_rejected(self):
        bad = {**self.targets, "max_unsafe_engineering_actions": 1}
        self.assertFalse(assess(self.policy, self.recovery,
                                self.baseline, bad)["gate_passed"])

    def test_missing_human_review_blocks(self):
        bad = {**self.targets, "requires_human_release_review": False}
        self.assertFalse(assess(self.policy, self.recovery, self.baseline, bad)["gate_passed"])

    def test_initial_historical_baseline_is_not_formal_release(self):
        self.assertEqual(self.baseline["unit_tests"], 10)
        self.assertIsNone(self.baseline["independent_recovery_cases"])
        self.assertEqual(self.baseline["status"], "historical_observed_baseline_not_formal_release")


if __name__ == "__main__":
    unittest.main()
