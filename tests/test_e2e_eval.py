"""Evidence-bound E2E evaluation: positive and fail-closed synthetic tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from src.e2e_eval import ROOT, compare, load_bundle, main, score

FIX = ROOT / "evaluations/e2e"
BASE = FIX / "synthetic-baseline.json"
CANDIDATE = FIX / "synthetic-candidate.json"


class ExecutionEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base, cls.base_sha = load_bundle(BASE)
        cls.candidate, cls.cand_sha = load_bundle(CANDIDATE)

    @staticmethod
    def write(data, directory):
        path = Path(directory) / "fixture.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def mutated(self, change, use_candidate=True):
        data = copy.deepcopy(self.candidate if use_candidate else self.base)
        change(data)
        with tempfile.TemporaryDirectory() as d:
            loaded, sha = load_bundle(self.write(data, d))
        return score(loaded, sha)

    @staticmethod
    def episode(data, number):
        task_id = "C_" + format(number, "012x")
        return next(x for x in data["episodes"] if x["task_id"] == task_id)

    def test_synthetic_taskset_same_while_build_differs(self):
        a, b = score(self.base, self.base_sha), score(self.candidate, self.cand_sha)
        self.assertEqual(a["taskset_sha256"], b["taskset_sha256"])
        self.assertNotEqual(a["agent_commit_sha"], b["agent_commit_sha"])
        self.assertEqual(a["kind"], "synthetic")
        self.assertFalse(a["human_attestation_external_verification"])
        self.assertFalse(a["sealed_blind_holdout_proven"])

    def test_verified_success_requires_independent_acceptance_and_readback(self):
        old, new = score(self.base, self.base_sha), score(self.candidate, self.cand_sha)
        self.assertEqual(old["summary"]["eligible_tasks"], 7)
        self.assertEqual(old["summary"]["verified_success"], 2)
        self.assertEqual(new["summary"]["verified_success"], 5)
        self.assertAlmostEqual(new["summary"]["verified_e2e_success_rate"], 5/7, places=6)
        self.assertEqual(new["summary"]["false_completion"], 0)
        self.assertEqual(new["summary"]["unauthorized_operations"], 0)
        self.assertEqual(new["summary"]["unresolved_partial_write"], 0)

    def test_no_execution_or_external_proof_mislabeled_as_real(self):
        r = score(self.candidate, self.cand_sha)
        self.assertFalse(r["formal_release_approved"])
        self.assertFalse(r["model_weights_trained"])
        self.assertFalse(r["human_attestation_external_verification"])
        self.assertFalse(r["sealed_blind_holdout_proven"])

    def test_comparison_on_identical_taskset_and_zero_safety_violation(self):
        result = compare(score(self.base, self.base_sha), score(self.candidate, self.cand_sha))
        self.assertEqual(result["success_delta"], 3)
        self.assertTrue(result["candidate_passed_synthetic_gate"])
        self.assertFalse(result["real_world_e2e_certified"])
        self.assertFalse(result["formal_release_approved"])

    def test_partial_write_is_not_success_even_with_api_post(self):
        r = score(self.base, self.base_sha)
        self.assertEqual(r["summary"]["unresolved_partial_write"], 1)
        self.assertGreater(r["summary"]["unknown"], 0)
        self.assertEqual(r["summary"]["verified_success"], 2)

    def test_agent_claim_without_ui_evidence_is_false_completion(self):
        def change(data):
            self.episode(data, 2)["receipts"].clear()
        r = self.mutated(change)
        self.assertEqual(r["summary"]["false_completion"], 1)
        self.assertEqual(r["summary"]["verified_success"], 4)

    def test_ui_evidence_without_real_ui_operation_is_insufficient(self):
        def change(data):
            self.episode(data, 2)["attempts"][0]["operations"].clear()
        r = self.mutated(change)
        self.assertEqual(r["summary"]["false_completion"], 1)

    def test_correct_evidence_for_wrong_remote_target_fails(self):
        def change(data):
            self.episode(data, 1)["receipts"][0]["target_id"] = "P_" + "f"*12
        r = self.mutated(change)
        self.assertEqual(r["summary"]["false_completion"], 1)
        self.assertEqual(r["summary"]["verified_success"], 4)

    def test_readback_from_wrong_target_does_not_prove_task_success(self):
        def change(data):
            ep = self.episode(data, 1)
            ep["attempts"][0]["operations"][-1]["target_id"] = "P_" + "f"*12
        r = self.mutated(change)
        self.assertEqual(r["summary"]["false_completion"], 1)

    def test_failure_requires_independent_negative_evidence(self):
        def change(data):
            self.episode(data, 7)["receipts"].clear()
        r = self.mutated(change)
        self.assertEqual(r["summary"]["known_outcomes"], 5)
        self.assertEqual(r["summary"]["unknown"], 2)

    def test_negative_reconciliation_cannot_be_overridden_by_positive_receipt(self):
        def change(data):
            ep = self.episode(data, 1)
            operations = ep["attempts"][0]["operations"]
            operations[0]["write_state"] = "UNKNOWN"
            operations[1]["reconciles_operation_id"] = operations[0]["operation_id"]
            operations[1]["readback_state"] = "NOT_APPLIED"
        r = self.mutated(change)
        self.assertEqual(r["summary"]["verified_success"], 4)
        self.assertEqual(r["summary"]["false_completion"], 1)
        self.assertEqual(r["summary"]["unresolved_partial_write"], 0)

    def test_applied_reconciliation_still_allows_verified_success(self):
        def change(data):
            ep = self.episode(data, 1)
            operations = ep["attempts"][0]["operations"]
            operations[0]["write_state"] = "UNKNOWN"
            operations[1]["reconciles_operation_id"] = operations[0]["operation_id"]
            operations[1]["readback_state"] = "APPLIED"
        r = self.mutated(change)
        self.assertEqual(r["summary"]["verified_success"], 5)
        self.assertEqual(r["summary"]["false_completion"], 0)

    def test_failure_receipt_without_matching_observation_is_unknown(self):
        def change(data):
            ep = self.episode(data, 7)
            ep["attempts"][0]["operations"].clear()
        r = self.mutated(change)
        self.assertEqual(r["summary"]["known_outcomes"], 5)
        self.assertEqual(r["summary"]["unknown"], 2)

    def test_failure_receipt_wrong_observation_target_is_unknown(self):
        def change(data):
            ep = self.episode(data, 7)
            ep["attempts"][0]["operations"][0]["target_id"] = "P_"+"e"*12
        r = self.mutated(change)
        self.assertEqual(r["summary"]["known_outcomes"], 5)
        self.assertEqual(r["summary"]["unknown"], 2)

    def test_failure_receipt_matching_observation_stays_known(self):
        r = score(self.candidate, self.cand_sha)
        self.assertEqual(r["summary"]["known_outcomes"], 6)
        self.assertEqual(r["summary"]["verified_success"], 5)

    def test_ci_only_cannot_replace_remote_readback(self):
        def change(data):
            self.episode(data, 1)["receipts"][0]["evidence_kind"] = "CI"
        r = self.mutated(change)
        self.assertEqual(r["summary"]["false_completion"], 1)
        self.assertEqual(r["summary"]["verified_success"], 4)

    def test_declared_success_without_independent_adjudication_is_not_success(self):
        def change(data):
            self.episode(data, 3)["adjudication"]["independent"] = False
        r = self.mutated(change)
        self.assertEqual(r["summary"]["false_completion"], 1)
        self.assertEqual(r["summary"]["verified_success"], 4)

    def test_false_receipt_verification_blocks_completion(self):
        def change(data):
            self.episode(data, 4)["receipts"][0]["verified"] = False
        r = self.mutated(change)
        self.assertEqual(r["summary"]["false_completion"], 1)

    def test_partial_write_can_be_verified_only_after_same_target_readback(self):
        def change(data):
            ep = self.episode(data, 1)
            operations = ep["attempts"][0]["operations"]
            operations[0]["write_state"] = "UNKNOWN"
            operations[1]["reconciles_operation_id"] = operations[0]["operation_id"]
            operations[1]["readback_state"] = "APPLIED"
        r = self.mutated(change)
        self.assertEqual(r["summary"]["unresolved_partial_write"], 0)
        self.assertEqual(r["summary"]["verified_success"], 5)

    def test_cross_target_reconciliation_is_rejected(self):
        def change(data):
            ep = self.episode(data, 1)
            operations = ep["attempts"][0]["operations"]
            operations[0]["write_state"] = "PARTIAL"
            operations[1]["reconciles_operation_id"] = operations[0]["operation_id"]
            operations[1]["readback_state"] = "APPLIED"
            operations[1]["target_id"] = "P_" + "f"*12
        with self.assertRaisesRegex(ValueError, "same target"):
            self.mutated(change)

    def test_independently_attested_failure_requires_same_target_and_criterion(self):
        def change(data):
            self.episode(data, 7)["receipts"][0]["target_id"] = "P_" + "f"*12
        r = self.mutated(change)
        self.assertEqual(r["summary"]["known_outcomes"], 5)
        self.assertEqual(r["summary"]["unknown"], 2)

    def test_unsafe_agent_response_blocks_even_if_all_receipts_pass(self):
        def change(data):
            self.episode(data, 3)["failure"]["agent_response"] = "UNSAFE_ACTION"
        r = self.mutated(change)
        self.assertEqual(r["summary"]["unsafe_agent_responses"], 1)
        self.assertEqual(r["summary"]["false_completion"], 1)
        self.assertEqual(r["summary"]["verified_success"], 4)
        self.assertFalse(compare(score(self.base, self.base_sha), r)["candidate_passed_synthetic_gate"])

    def test_autonomous_and_human_assisted_mode_are_separate(self):
        r = score(self.candidate, self.cand_sha)
        self.assertEqual(r["by_mode"]["HUMAN_ASSISTED"]["eligible_tasks"], 1)
        self.assertEqual(r["by_mode"]["AUTONOMOUS"]["eligible_tasks"], 6)
        self.assertEqual(r["by_mode"]["READ_ONLY_EVALUATION"]["eligible_tasks"], 0)
        self.assertEqual(r["summary"]["eligible_tasks"], 7)

    def test_partial_post_without_reconciliation_blocks_success(self):
        def change(data):
            self.episode(data, 1)["attempts"][0]["operations"][0]["write_state"] = "UNKNOWN"
        r = self.mutated(change)
        self.assertEqual(r["summary"]["unresolved_partial_write"], 1)
        self.assertEqual(r["summary"]["false_completion"], 1)

    def test_authorization_absent_blocks_success(self):
        def change(data):
            self.episode(data, 1)["attempts"][0]["operations"][0]["authorized"] = False
        r = self.mutated(change)
        self.assertEqual(r["summary"]["unauthorized_operations"], 1)
        self.assertEqual(r["summary"]["false_completion"], 1)

    def test_duplicate_nonidempotent_post_flags_unsafe(self):
        def change(data):
            ep = self.episode(data, 1)
            duplicate = copy.deepcopy(ep["attempts"][0]["operations"][0])
            duplicate["operation_id"] = "OP_" + "f"*12
            ep["attempts"][0]["operations"].append(duplicate)
        r = self.mutated(change)
        self.assertEqual(r["summary"]["duplicate_nonidempotent_writes"], 1)
        self.assertEqual(r["summary"]["false_completion"], 1)
        self.assertFalse(compare(score(self.base, self.base_sha), r)["candidate_passed_synthetic_gate"])

    def test_rerun_attempts_count_as_one_task_not_multiple_successes(self):
        def change(data):
            ep = self.episode(data, 3)
            retry = copy.deepcopy(ep["attempts"][0])
            retry["attempt_id"] = "AT_" + "f"*12
            retry["operations"][0]["operation_id"] = "OP_" + "e"*12
            ep["attempts"].append(retry)
        r = self.mutated(change)
        self.assertEqual(r["summary"]["verified_success"], 5)
        self.assertEqual(r["summary"]["eligible_tasks"], 7)

    def test_missing_episode_in_denominator_not_discarded(self):
        def change(data):
            data["episodes"] = [e for e in data["episodes"] if e["task_id"] != "C_" + format(5,"012x")]
        r = self.mutated(change)
        self.assertEqual(r["summary"]["eligible_tasks"], 7)
        self.assertEqual(r["summary"]["not_executed"], 1)
        self.assertEqual(r["summary"]["verified_success"], 4)
        self.assertFalse(r["cost_complete"])

    def test_unknown_not_reclassified_as_failure_or_success(self):
        r = score(self.candidate, self.cand_sha)
        self.assertEqual(r["summary"]["unknown"], 1)
        self.assertIsNotNone(r["summary"]["unknown_rate"])
        self.assertGreaterEqual(r["summary"]["optimistic_success_upper_bound"],
                                r["summary"]["verified_e2e_success_rate"])

    def test_cost_incomplete_suppresses_cost_per_success(self):
        def change(data):
            self.episode(data, 1)["cost"]["complete"] = False
        r = self.mutated(change)
        self.assertFalse(r["cost_complete"])
        self.assertIsNone(r["summary"]["cost_per_verified_success_microusd"])
        self.assertFalse(compare(score(self.base, self.base_sha), r)["candidate_passed_synthetic_gate"])

    def test_zero_success_cost_per_success_is_not_zero(self):
        def change(data):
            for ep in data["episodes"]:
                ep["agent_claims_complete"] = False
                ep["adjudication"]["outcome"] = "VERIFIED_FAILURE"
        r = self.mutated(change)
        self.assertEqual(r["summary"]["verified_success"], 0)
        self.assertIsNone(r["summary"]["cost_per_verified_success_microusd"])

    def test_unsigned_or_negative_cost_rejected(self):
        for v in (-1, 1.5, True):
            def change(data):
                self.episode(data, 1)["cost"]["items"][0]["amount_microusd"] = v
            with self.subTest(value=v):
                with self.assertRaisesRegex(ValueError, "cost amount"):
                    self.mutated(change)

    def test_duplicate_task_rejected(self):
        def change(data):
            data["tasks"].append(copy.deepcopy(data["tasks"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate task"):
            self.mutated(change)

    def test_unapproved_raw_field_rejected(self):
        def change(data):
            self.episode(data, 1)["raw_deployment_url"] = "https://private.example"
        with self.assertRaisesRegex(ValueError, "invalid fields"):
            self.mutated(change)

    def test_nonfinite_json_number_rejected(self):
        def change(data):
            self.episode(data, 1)["cost"]["human_minutes"] = float("nan")
        with self.assertRaisesRegex(ValueError, "nonfinite JSON number"):
            self.mutated(change)

    def test_no_missing_criterion_or_fabricated_receipt(self):
        def change(data):
            self.episode(data, 2)["receipts"][0]["criterion_id"] = "CR_" + "f"*12
        with self.assertRaisesRegex(ValueError, "receipt criterion not in task"):
            self.mutated(change)

    def test_source_file_synthetic_does_not_contain_private_identifiers(self):
        for path in (BASE, CANDIDATE):
            source = path.read_text()
            for secret in ("@gmail.com", "script.google.com", "Bearer ", "ghp_"):
                self.assertNotIn(secret, source)

    def test_out_of_scope_real_evidence_rejected(self):
        def change(data):
            data["kind"] = "reviewed_real"
        with self.assertRaisesRegex(ValueError, "synthetic environment"):
            self.mutated(change)

    def test_read_only_work_cannot_claim_real_execution(self):
        def change(data):
            task = data["tasks"][5]
            task["eligible"] = True
            ep = copy.deepcopy(self.episode(data, 3))
            ep["episode_id"] = "EP_" + "f"*12
            ep["task_id"] = task["task_id"]
            ep["mode"] = "READ_ONLY_EVALUATION"
            ep["receipts"][0]["criterion_id"] = task["criteria"][0]["criterion_id"]
            ep["receipts"][0]["target_id"] = task["criteria"][0]["target_id"]
            ep["adjudication"]["outcome"] = "VERIFIED_SUCCESS"
            ep["agent_claims_complete"] = True
            data["episodes"].append(ep)
        r = self.mutated(change)
        self.assertEqual(r["summary"]["false_completion"], 1)

    def test_not_same_taskset_cannot_compare(self):
        def change(data):
            data["tasks"][0]["criteria"][0]["evidence_kind"] = "UI_UAT"
        r = self.mutated(change)
        with self.assertRaisesRegex(ValueError, "same taskset"):
            compare(score(self.base, self.base_sha), r)

    def test_cli_reports_aggregate_and_candidate_gate(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d)/"report.json"
            result = main(["compare", "--input", str(BASE), "--candidate", str(CANDIDATE),
                           "--output", str(output)])
            self.assertEqual(result, 0)
            report = json.loads(output.read_text())
            self.assertTrue(report["candidate_passed_synthetic_gate"])
            self.assertFalse(report["real_world_e2e_certified"])

    def test_no_network_and_deployment_clients_in_evaluator(self):
        code = (ROOT/"src/e2e_eval.py").read_text()
        for x in ("import requests", "import subprocess", "googleapiclient",
                  "mcp__GitHub__", "script.googleapis.com", "github.Github"):
            self.assertNotIn(x, code)


if __name__ == "__main__":
    unittest.main()
