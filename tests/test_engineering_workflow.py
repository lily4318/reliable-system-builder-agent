"""Offline workflow handoff regression; synthetic evidence, no tool execution."""
import json
import tempfile
import unittest
from pathlib import Path

from src.engineering_workflow import ROUTES, SAFE_ACTIONS, evaluate, load_cases, route

SHA = "a" * 40
READY = {
    "stage": "verify",
    "target_confirmed": True,
    "source_sha": SHA,
    "current_head_sha": SHA,
    "write_outcome": "NONE",
    "requirements_confirmed": True,
    "acceptance_criteria": True,
    "dependencies_mapped": True,
    "rollback_reviewed": True,
    "data_classified": True,
    "acl_reviewed": True,
    "candidate_patch_authorized": True,
    "changed_files_readback": True,
    "patch_commit_sha": SHA,
    "positive_tests_passed": True,
    "negative_tests_passed": True,
    "ci_passed": True,
    "ci_run_id": 123,
    "ci_head_sha": SHA,
    "tested_sha": SHA,
    "real_ui_uat_verified": True,
}


class EngineeringWorkflowTest(unittest.TestCase):
    def decision(self, change=None):
        return route({**READY, **(change or {})})["decision"]

    def test_requirements_and_acceptance_before_architecture(self):
        for change in ({"requirements_confirmed": False}, {"acceptance_criteria": False}):
            self.assertEqual(self.decision(change), "HOLD_REQUIREMENTS")
        self.assertEqual(route({**READY, "acceptance_criteria": False})["owner_role"], "architect")

    def test_architecture_dependency_and_rollback_before_code(self):
        for change in ({"dependencies_mapped": False}, {"rollback_reviewed": False}):
            self.assertEqual(self.decision(change), "HOLD_ARCHITECTURE")
        self.assertEqual(self.decision({"stage": "design"}), "READY_FOR_DESIGN_REVIEW_ONLY")

    def test_security_data_and_acl_hard_gate(self):
        for change in ({"data_classified": False}, {"acl_reviewed": False}):
            self.assertEqual(self.decision(change), "HOLD_SECURITY")
            self.assertEqual(route({**READY, **change})["owner_role"], "security")

    def test_unknown_and_partial_write_override_every_other_green_signal(self):
        for status in ("UNKNOWN", "PARTIAL", "UNCLASSIFIED"):
            answer = route({**READY, "stage": "release", "write_outcome": status})
            self.assertEqual(answer["decision"], "READ_ONLY_RECONCILE")
            self.assertEqual(answer["owner_role"], "devops-sre")
            self.assertEqual(answer["next_safe_action"], "RECONCILE_WITH_READ_ONLY_EVIDENCE")

    def test_wrong_repo_or_sha_stops_before_patch(self):
        self.assertEqual(self.decision({"target_confirmed": False}), "HOLD_TARGET")
        self.assertEqual(self.decision({"current_head_sha": "b" * 40}), "HOLD_SOURCE")
        self.assertEqual(self.decision({"source_sha": "invalid"}), "HOLD_SOURCE")

    def test_authorized_candidate_only_not_auto_execute(self):
        self.assertEqual(self.decision({"stage": "patch", "candidate_patch_authorized": False}),
                         "HOLD_PATCH_AUTHORIZATION")
        result = route({**READY, "stage": "patch"})
        self.assertEqual(result["decision"], "READY_FOR_CANDIDATE_PATCH")
        self.assertEqual(result["owner_role"], "developer")
        self.assertFalse(result["mutation_permitted"])

    def test_code_readback_and_qa_handoffs(self):
        self.assertEqual(self.decision({"changed_files_readback": False}),
                         "HOLD_IMPLEMENTATION")
        self.assertEqual(self.decision({"patch_commit_sha": "b" * 40}),
                         "HOLD_IMPLEMENTATION")
        for missing in ("positive_tests_passed", "negative_tests_passed"):
            self.assertEqual(self.decision({missing: False}), "HOLD_QA")

    def test_ci_must_match_exact_code_and_test_sha(self):
        for change in ({"ci_passed": False}, {"ci_run_id": 0},
                       {"ci_run_id": True}, {"ci_run_id": None},
                       {"ci_head_sha": "b" * 40}, {"tested_sha": "b" * 40}):
            self.assertEqual(self.decision(change), "HOLD_CI")
        result = route(READY)
        self.assertEqual(result["decision"], "READY_FOR_HUMAN_PR_REVIEW")
        self.assertEqual(result["owner_role"], "learning-evaluator")
        self.assertFalse(result["mutation_permitted"])

    def test_release_with_all_green_still_requires_real_uat_and_human(self):
        self.assertEqual(self.decision({"stage": "release",
                                        "real_ui_uat_verified": False}), "HOLD_REAL_UAT")
        self.assertEqual(self.decision({"stage": "release"}), "HOLD_HUMAN_RELEASE")
        self.assertFalse(route({**READY, "stage": "release"})["mutation_permitted"])

    def test_unsupported_and_missing_structured_evidence_fail_closed(self):
        self.assertEqual(route(None)["decision"], "HOLD_TARGET")
        self.assertEqual(self.decision({"stage": "unknown"}), "HOLD_UNSUPPORTED")
        self.assertEqual(self.decision({"stage": "read_only"}), "READ_ONLY_AUDIT")
        self.assertEqual(self.decision({"write_outcome": "untrusted"}) ,
                         "READ_ONLY_RECONCILE")

    def test_all_roles_routed_by_public_human_labelled_cases(self):
        cases = load_cases()
        self.assertGreaterEqual(len(cases), 20)
        expected_roles = {c["expected_owner"] for c in cases}
        self.assertEqual(expected_roles, {
            "system-lead", "architect", "developer", "devops-sre",
            "qa-uat", "security", "learning-evaluator",
        })
        result = evaluate()
        self.assertEqual(result["failed"], 0)
        self.assertTrue(result["gate_passed"])
        self.assertFalse(result["real_world_specialist_execution_verified"])
        self.assertFalse(result["natural_language_requirements_accuracy_measured"])

    def test_dataset_duplicate_and_bad_handoff_labels_rejected(self):
        cases = load_cases()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "cases.json"
            data = {"schema_version": 1, "synthetic_or_sanitized": True,
                    "cases": [*cases, cases[0]]}
            p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicated"):
                load_cases(p)
            corrupted = json.loads(json.dumps(cases))
            corrupted[0]["expected_owner"] = "developer"
            p.write_text(json.dumps({**data, "cases": corrupted}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "owner label"):
                load_cases(p)

    def test_safety_actions_are_advisory_only(self):
        for case in load_cases():
            result = route(case["scenario"])
            self.assertIn(result["next_safe_action"], SAFE_ACTIONS)
            self.assertFalse(result["mutation_permitted"])
            self.assertNotIn(result["next_safe_action"],
                             {"SEND_POST", "MERGE", "DEPLOY", "LAUNCH", "RETRY_POST"})


if __name__ == "__main__":
    unittest.main()
