"""Synthetic regression against structured task-scope decisions, not LLM IQ."""
import json
import tempfile
import unittest
from pathlib import Path

from src.task_scope import decide_scope, evaluate, load_cases

AGENT = "example/system-builder-agent"
PROJECT = "example/other-project"
BASE = {"intent_confirmed_from_latest_user": True, "agent_repo": AGENT}


class TaskScopeTest(unittest.TestCase):
    def test_agent_improvement_does_not_write_previous_project(self):
        s = {**BASE, "intent": "improve_agent", "target_repo": AGENT,
             "proposed_write_repo": PROJECT, "write_authorized": True}
        self.assertEqual(decide_scope(s), "BLOCK_CROSS_PROJECT_WRITE")

    def test_latest_explicit_correction_overrides_prior_context(self):
        s = {**BASE, "intent": "improve_agent", "target_repo": AGENT,
             "proposed_write_repo": AGENT, "write_authorized": True}
        self.assertEqual(decide_scope(s), "AGENT_CANDIDATE_PR_ONLY")
        self.assertEqual(decide_scope({**s, "intent_confirmed_from_latest_user": False}),
                         "HOLD_INTENT")

    def test_agent_review_vs_authorized_candidate_pr(self):
        s = {**BASE, "intent": "improve_agent", "target_repo": AGENT}
        self.assertEqual(decide_scope({**s, "write_authorized": False}), "AGENT_READ_ONLY")
        self.assertEqual(decide_scope({**s, "write_authorized": True,
                                       "proposed_write_repo": AGENT}), "AGENT_CANDIDATE_PR_ONLY")
        self.assertEqual(decide_scope({**s, "write_authorized": True}), "HOLD_TARGET")

    def test_application_is_separate_target_and_authorization(self):
        s = {**BASE, "intent": "apply_agent", "target_repo": PROJECT}
        self.assertEqual(decide_scope(s), "PROJECT_READ_ONLY")
        self.assertEqual(decide_scope({**s, "write_authorized": True,
                                       "proposed_write_repo": PROJECT}), "PROJECT_PATCH_ONLY")
        self.assertEqual(decide_scope({**s, "write_authorized": True,
                                       "proposed_write_repo": AGENT}), "BLOCK_CROSS_PROJECT_WRITE")

    def test_github_case_alias_is_not_a_separate_project(self):
        for target in (AGENT.upper(), "Example/system-builder-agent"):
            for authorized in (False, True):
                with self.subTest(target=target, authorized=authorized):
                    s = {**BASE, "intent": "apply_agent", "target_repo": target,
                         "proposed_write_repo": target if authorized else None,
                         "write_authorized": authorized}
                    self.assertEqual(decide_scope(s), "HOLD_TARGET")

    def test_github_case_alias_preserves_scoped_authorization(self):
        s = {**BASE, "intent": "improve_agent", "target_repo": AGENT.upper(),
             "proposed_write_repo": "Example/system-builder-agent", "write_authorized": True}
        cases = [
            (s, "AGENT_CANDIDATE_PR_ONLY"),
            ({**s, "write_authorized": False}, "AGENT_READ_ONLY"),
            ({**s, "proposed_write_repo": PROJECT.upper()}, "BLOCK_CROSS_PROJECT_WRITE"),
            ({**s, "requests_weight_training": True}, "HOLD_WEIGHT_TRAINING"),
            ({**s, "intent_confirmed_from_latest_user": "true"}, "HOLD_INTENT"),
            ({**s, "target_repo": " " + AGENT}, "HOLD_TARGET"),
            ({**s, "proposed_write_repo": None}, "HOLD_TARGET"),
            ({**s, "intent": "apply_agent", "target_repo": PROJECT.upper(),
              "proposed_write_repo": PROJECT}, "PROJECT_PATCH_ONLY"),
            ({**s, "intent": "apply_agent", "target_repo": PROJECT,
              "proposed_write_repo": AGENT.upper()}, "BLOCK_CROSS_PROJECT_WRITE"),
        ]
        for scenario, expected in cases:
            with self.subTest(expected=expected, scenario=scenario):
                self.assertEqual(decide_scope(scenario), expected)

    def test_weight_training_needs_separate_evidence(self):
        self.assertEqual(decide_scope({**BASE, "intent": "improve_agent",
                                       "target_repo": AGENT, "proposed_write_repo": AGENT,
                                       "write_authorized": True, "requests_weight_training": True}),
                         "HOLD_WEIGHT_TRAINING")

    def test_missing_or_ambiguous_target_never_fabricates_authorization(self):
        self.assertEqual(decide_scope({**BASE, "intent": "improve_agent",
                                       "target_repo": "not-a-repo"}), "HOLD_TARGET")
        self.assertEqual(decide_scope({**BASE, "intent": "unknown",
                                       "target_repo": AGENT}), "HOLD_INTENT")
        self.assertEqual(decide_scope(None), "HOLD_INTENT")

    def test_public_cases_pass_and_reject_corrupted_dataset(self):
        cases = load_cases()
        self.assertGreaterEqual(len(cases), 12)
        self.assertGreaterEqual(sum(c["critical"] for c in cases), 8)
        report = evaluate()
        self.assertEqual(report["failed"], 0)
        self.assertFalse(report["natural_language_intent_accuracy_measured"])
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "cases.json"
            p.write_text(json.dumps({"schema_version": 1, "synthetic_or_sanitized": True,
                                     "cases": [cases[0]] * 12}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicated"):
                load_cases(p)


if __name__ == "__main__":
    unittest.main()
