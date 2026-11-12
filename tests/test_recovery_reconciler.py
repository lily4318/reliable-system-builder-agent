"""Failure-injection and invariants for read-only recovery decisions."""
import copy
import unittest

from src.recovery_reconciler import GET_ACTIONS, reconcile
from src.independent_acceptance import evaluate, load_cases

HEAD = {"id": "synthetic-head", "kind": "HEAD", "version": None,
        "access": "MYSELF", "execute_as": "USER_DEPLOYING"}
BEFORE = {"head_sha": "simulated-sha", "versions": [], "deployments": [HEAD]}
BASE = {"target_isolated": True, "source_verified": True,
        "intake_closed": True, "before": BEFORE, "after": BEFORE, "post_stage": "none"}


class RecoveryReconcilerTest(unittest.TestCase):
    def test_held_cases_independent_acceptance(self):
        report = evaluate()
        self.assertGreaterEqual(report["total"], 20)
        self.assertEqual(report["failed"], 0, report)
        self.assertEqual(report["unsafe_action_count"], 0)
        self.assertTrue(report["release_gate_passed"])

    def test_no_mutation_can_ever_be_recommended(self):
        cases, _ = load_cases()
        for c in cases:
            with self.subTest(c["id"]):
                result = reconcile(c["evidence"])
                self.assertIs(result["mutation_allowed"], False)
                self.assertIs(result["formal_launch_allowed"], False)
                self.assertIs(result["requires_human_review"], True)
                self.assertTrue(set(result["allowed_next_actions"]) <= set(GET_ACTIONS) | {"HUMAN_REVIEW"})

    def test_version_success_with_stale_list_is_not_no_write(self):
        trace = {**BASE, "post_stage": "create_version_success",
                 "returned_version": 1, "immutable_sha_verified": True}
        self.assertEqual(reconcile(trace)["classification"], "VERSION_LIST_LAG")

    def test_version_success_and_present_is_orphan_not_deployed(self):
        later = {**BEFORE, "versions": [1]}
        trace = {**BASE, "post_stage": "create_version_success",
                 "returned_version": 1, "immutable_sha_verified": True, "after": later}
        self.assertEqual(reconcile(trace)["classification"], "ORPHAN_VERSION_CONFIRMED")
        self.assertFalse(reconcile(trace)["mutation_allowed"])

    def test_network_timeout_after_post_unknown(self):
        for stage in ("create_version_unknown", "create_deployment_unknown"):
            self.assertEqual(reconcile({**BASE, "post_stage": stage})["classification"],
                             "UNKNOWN_POST_RESULT")

    def test_unsafe_access_and_identity_block(self):
        for field, value in (("access", "ANYONE_ANONYMOUS"), ("execute_as", "USER_ACCESSING")):
            later = copy.deepcopy(BEFORE)
            later["deployments"][0][field] = value
            self.assertEqual(reconcile({**BASE, "after": later})["classification"], "BLOCK_UNSAFE_ACL")

    def test_duplicate_head_never_treated_as_safe(self):
        later = copy.deepcopy(BEFORE)
        later["deployments"].append({**HEAD, "id": "second-synthetic-head"})
        with self.assertRaisesRegex(ValueError, "head_count"):
            reconcile({**BASE, "after": later})

    def test_missing_or_duplicate_version_data_rejected(self):
        for versions in ([1, 1], [0], ["1"], [-1], [True]):
            later = {**BEFORE, "versions": versions}
            with self.assertRaisesRegex(ValueError, "versions"):
                reconcile({**BASE, "after": later})

    def test_external_mutation_is_not_attributed_to_this_run(self):
        later = {**BEFORE, "versions": [1]}
        self.assertEqual(reconcile({**BASE, "after": later})["classification"],
                         "UNATTRIBUTED_REMOTE_CHANGE")

    def test_missing_readback_is_unknown_not_zero(self):
        self.assertEqual(reconcile({**BASE, "after": None})["classification"], "READBACK_MISSING")

    def test_head_sha_drift_blocks_even_if_version_exists(self):
        later = {**BEFORE, "head_sha": "different-simulated-sha"}
        self.assertEqual(reconcile({**BASE, "after": later})["classification"], "BLOCK_HEAD_DRIFT")

    def test_intake_must_be_closed(self):
        self.assertEqual(reconcile({**BASE, "intake_closed": False})["classification"], "BLOCK_LIVE_INTAKE")

    def test_no_actual_post_or_api_client_implemented(self):
        from pathlib import Path
        code = Path("src/recovery_reconciler.py").read_text(encoding="utf-8")
        for forbidden in ("import requests", "import urllib", "http.client",
                          "googleapiclient", "subprocess", "os.system", "client_secret"):
            self.assertNotIn(forbidden, code)


if __name__ == "__main__":
    unittest.main()
