"""Offline public safety-policy regression tests."""
import json
import tempfile
import unittest
from pathlib import Path
from src.agent_eval import decide, evaluate, validate, load_cases

BASE = {"target_isolated": True, "source_verified": True}


class SafetyPolicyTest(unittest.TestCase):
    def test_unknown_project_blocks(self):
        self.assertEqual(decide({"operation": "private_deploy"}), "HOLD_TARGET")

    def test_unverified_sha_blocks(self):
        self.assertEqual(decide({**BASE, "source_verified": False, "operation": "code_patch"}), "HOLD_SOURCE")

    def test_partial_write_and_unknown_post_stop(self):
        self.assertEqual(decide({**BASE, "partial_write": True, "operation": "private_deploy"}), "RECONCILE_READ_ONLY")
        self.assertEqual(decide({**BASE, "unknown_write_result": True, "operation": "private_deploy"}), "RECONCILE_READ_ONLY")
        self.assertEqual(decide({**BASE, "operation": "post_retry", "http_status": 503}), "NO_POST_RETRY")

    def test_get_http_policy(self):
        for status in (429, 503):
            self.assertEqual(decide({**BASE, "operation": "read", "method": "GET", "http_status": status}), "RETRY_BOUNDED_GET")
        self.assertEqual(decide({**BASE, "operation": "read", "method": "GET", "http_status": 403}), "HOLD_HTTP")
        self.assertEqual(decide({**BASE, "operation": "read", "method": "POST", "http_status": 503}), "HOLD_METHOD")

    def test_all_private_deploy_gates(self):
        ready = {**BASE, "operation": "private_deploy", "approved": True,
                 "inventory_verified": True, "head_sha_verified": True,
                 "access_myself": True, "execute_as_deployer": True, "intake_closed": True}
        self.assertEqual(decide(ready), "READY_FOR_PRIVATE_DEPLOY_ONLY")
        for key in ("approved", "inventory_verified", "head_sha_verified",
                    "access_myself", "execute_as_deployer", "intake_closed"):
            self.assertNotEqual(decide({**ready, key: False}), "READY_FOR_PRIVATE_DEPLOY_ONLY")

    def test_formal_intake_separate(self):
        ready = {**BASE, "operation": "formal_intake", "rec_approved": True,
                 "pi_approved": True, "privacy_ready": True, "consent_ready": True,
                 "ui_verified": True, "launch_authorized": True}
        self.assertEqual(decide(ready), "READY_FOR_HUMAN_LAUNCH_REVIEW")
        for key in ("rec_approved", "pi_approved", "privacy_ready", "consent_ready", "ui_verified", "launch_authorized"):
            self.assertEqual(decide({**ready, key: False}), "HOLD_FORMAL")

    def test_ci_does_not_replace_ui(self):
        self.assertEqual(decide({**BASE, "operation": "ui_acceptance", "actual_manual_ui": False}), "REQUIRE_UI_UAT")

    def test_dataset_and_all_cases(self):
        self.assertGreaterEqual(len(load_cases()), 20)
        self.assertTrue(validate()["valid"])
        self.assertEqual(evaluate()["failed"], 0)
        self.assertTrue(evaluate()["release_gate_passed"])

    def test_duplicate_case_ids_rejected(self):
        case = {"id": "R001", "description": "test", "scenario": dict(BASE),
                "expected": "HOLD_UNSUPPORTED", "critical": True}
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / "cases.json"
            file.write_text(json.dumps({"schema_version": 1, "synthetic_or_sanitized": True,
                                        "cases": [case, case]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicated"):
                load_cases(file)

    def test_unknown_operation_fail_closed(self):
        self.assertEqual(decide({**BASE, "operation": "unknown_magic"}), "HOLD_UNSUPPORTED")


if __name__ == "__main__":
    unittest.main()
