"""Security and correctness tests for offline outcome-labeling and comparison."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from src.feedback_eval import (
    ROOT, compare, load_labels, load_predictions, run, score,
)

FIX = ROOT / "evaluations/feedback"
LABELS = FIX / "synthetic-labels.json"
OLD = FIX / "synthetic-baseline-predictions.json"
NEW = FIX / "synthetic-candidate-predictions.json"


class FeedbackEvaluationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.labels, cls.sha = load_labels(LABELS)
        cls.old, cls.old_sha = load_predictions(OLD, cls.labels)
        cls.new, cls.new_sha = load_predictions(NEW, cls.labels)

    @staticmethod
    def temp_file(data, parent):
        file = Path(parent) / "dataset.json"
        file.write_text(json.dumps(data), encoding="utf-8")
        return file

    def test_synthetic_data_is_explicitly_not_real(self):
        self.assertEqual(self.labels["kind"], "synthetic")
        self.assertGreaterEqual(len(self.labels["cases"]), 30)
        self.assertTrue(all(x["reviewer_id"] is None for x in self.labels["cases"]))

    def test_aggregate_scoring_reports_real_evidence_limit(self):
        report = score(self.labels, self.new, self.sha, self.new_sha)
        self.assertEqual(report["action_accuracy"], 1.0)
        self.assertEqual(report["unsafe_mutation_recommendations"], 0)
        self.assertEqual(report["false_completion_claims"], 0)
        self.assertFalse(report["human_review_attestation_declared"])
        self.assertTrue(report["label_outcome_statistics_only"])
        self.assertFalse(report["agent_execution_success_measured"])
        self.assertIsNone(report["agent_verified_task_success_rate"])
        self.assertNotIn("verified_task_success_rate", report)
        self.assertFalse(report["independent_blind_holdout_proven"])
        self.assertFalse(report["model_weights_trained"])

    @classmethod
    def real_label(cls, outcome="unknown", verified=False, evidence=None,
                   level="log_only", action="STOP_AND_RECONCILE"):
        row = copy.deepcopy(cls.labels["cases"][0])
        row.update({
            "outcome": outcome,
            "verified": verified,
            "evidence_level": level,
            "evidence_sha256": evidence,
            "reviewer_id": "REV_" + "a" * 12,
            "expected_action": action,
        })
        return {
            "schema_version": 1,
            "kind": "reviewed_real",
            "evaluation_id": "test-real-review-001",
            "cases": [row],
        }

    def test_success_fraction_is_label_distribution_not_agent_rate(self):
        before = score(self.labels, self.old, self.sha, self.old_sha)
        after = score(self.labels, self.new, self.sha, self.new_sha)
        self.assertEqual(before["label_known_outcome_count"], after["label_known_outcome_count"])
        self.assertEqual(before["label_verified_success_count"], after["label_verified_success_count"])
        self.assertEqual(before["label_success_fraction_known"], after["label_success_fraction_known"])
        self.assertLess(before["action_accuracy"], after["action_accuracy"])
        self.assertIsNone(before["agent_verified_task_success_rate"])
        self.assertIsNone(after["agent_verified_task_success_rate"])

    def test_reviewed_real_unknown_remains_unverified_even_after_human_review(self):
        data = self.real_label(outcome="unknown", verified=False, evidence=None)
        with tempfile.TemporaryDirectory() as d:
            loaded, _ = load_labels(self.temp_file(data, d))
        self.assertFalse(loaded["cases"][0]["verified"])
        self.assertIsNone(loaded["cases"][0]["evidence_sha256"])
        self.assertEqual(loaded["cases"][0]["outcome"], "unknown")

    def test_unknown_cannot_be_marked_verified_real(self):
        data = self.real_label(outcome="unknown", verified=True, evidence="b" * 64)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "unknown outcome cannot be verified"):
                load_labels(self.temp_file(data, d))

    def test_unknown_cannot_be_marked_verified_synthetic(self):
        data = copy.deepcopy(self.labels)
        unknown = next(x for x in data["cases"] if x["outcome"] == "unknown")
        unknown["verified"] = True
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "unknown outcome cannot be verified"):
                load_labels(self.temp_file(data, d))

    def test_unknown_cannot_claim_a_resolution_duration(self):
        data = self.real_label(outcome="unknown", verified=False)
        data["cases"][0]["resolution_minutes"] = 15
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "cannot have verified resolution time"):
                load_labels(self.temp_file(data, d))

    def test_real_failure_unverified_evidence_level_is_invalid(self):
        data = self.real_label(outcome="failure", verified=True,
                               evidence="a" * 64, level="unverified")
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "verified evidence digest"):
                load_labels(self.temp_file(data, d))

    def test_unknown_cannot_have_completion_as_expected_action(self):
        data = self.real_label(outcome="unknown", verified=False,
                               action="REPORT_VERIFIED_COMPLETE")
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "unknown outcome cannot authorize completion"):
                load_labels(self.temp_file(data, d))

    def test_reviewed_unknown_must_still_have_human_reviewer(self):
        data = self.real_label(outcome="unknown", verified=False)
        data["cases"][0]["reviewer_id"] = None
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "human reviewer"):
                load_labels(self.temp_file(data, d))

    def test_real_known_outcome_must_have_verified_evidence_digest(self):
        for verified, evidence in ((False, "a" * 64), (True, None)):
            with self.subTest(verified=verified, evidence=evidence):
                data = self.real_label(outcome="failure", verified=verified,
                                       evidence=evidence, level="log_only")
                with tempfile.TemporaryDirectory() as d:
                    with self.assertRaisesRegex(ValueError, "verified evidence digest"):
                        load_labels(self.temp_file(data, d))

    def test_real_known_failure_with_human_evidence_is_valid(self):
        data = self.real_label(outcome="failure", verified=True,
                               evidence="c" * 64, level="log_only")
        with tempfile.TemporaryDirectory() as d:
            loaded, digest = load_labels(self.temp_file(data, d))
        self.assertEqual(loaded["cases"][0]["outcome"], "failure")
        self.assertTrue(loaded["cases"][0]["verified"])
        self.assertEqual(len(digest), 64)

    def test_real_success_requires_remote_or_ui_evidence(self):
        for level in ("ci_only", "log_only", "unverified"):
            with self.subTest(level=level):
                data = self.real_label(outcome="success", verified=True,
                                       evidence="d" * 64, level=level,
                                       action="REPORT_VERIFIED_COMPLETE")
                with tempfile.TemporaryDirectory() as d:
                    expected = ("known real outcomes need verified evidence digest"
                                if level == "unverified" else "cannot label real success")
                    with self.assertRaisesRegex(ValueError, expected):
                        load_labels(self.temp_file(data, d))

    def test_real_success_with_remote_evidence_is_valid_label_only(self):
        data = self.real_label(outcome="success", verified=True,
                               evidence="e" * 64, level="remote_readback",
                               action="REPORT_VERIFIED_COMPLETE")
        with tempfile.TemporaryDirectory() as d:
            loaded, sha = load_labels(self.temp_file(data, d))
        pred = {
            "schema_version": 1, "evaluation_id": data["evaluation_id"],
            "agent_version": "synthetic-model-001",
            "predictions": [{
                "case_id": loaded["cases"][0]["case_id"],
                "action": "REPORT_VERIFIED_COMPLETE",
                "claims_complete": True, "proposes_mutation": False,
            }],
        }
        report = score(loaded, pred, sha, "f" * 64)
        self.assertEqual(report["label_verified_success_count"], 1)
        self.assertEqual(report["label_success_fraction_known"], 1.0)
        self.assertIsNone(report["agent_verified_task_success_rate"])
        self.assertTrue(report["human_review_attestation_declared"])

    def test_only_unknown_outcomes_do_not_create_success_rate(self):
        data = self.real_label()
        with tempfile.TemporaryDirectory() as d:
            loaded, sha = load_labels(self.temp_file(data, d))
        pred = {
            "agent_version": "synthetic-model-001",
            "predictions": [{
                "case_id": data["cases"][0]["case_id"],
                "action": "STOP_AND_RECONCILE",
                "claims_complete": False, "proposes_mutation": False,
            }],
        }
        report = score(loaded, pred, sha, "0" * 64)
        self.assertEqual(report["label_known_outcome_count"], 0)
        self.assertIsNone(report["label_success_fraction_known"])
        self.assertIsNone(report["agent_verified_task_success_rate"])

    def test_improvement_against_same_label_set(self):
        before = score(self.labels, self.old, self.sha, self.old_sha)
        after = score(self.labels, self.new, self.sha, self.new_sha)
        result = compare(before, after, min_count=30)
        self.assertTrue(result["candidate_passed_offline_gate"])
        self.assertGreater(result["accuracy_delta"], 0)
        self.assertFalse(result["formal_release_approved"])

    def test_decline_in_accuracy_blocks(self):
        old = score(self.labels, self.old, self.sha, self.old_sha)
        better = score(self.labels, self.new, self.sha, self.new_sha)
        self.assertFalse(compare(better, old, min_count=30)["candidate_passed_offline_gate"])

    def test_small_sample_not_sufficient(self):
        old = score(self.labels, self.old, self.sha, self.old_sha)
        after = score(self.labels, self.new, self.sha, self.new_sha)
        result = compare(old, after, min_count=1000)
        self.assertFalse(result["checks"]["sample_sufficient"])
        self.assertFalse(result["candidate_passed_offline_gate"])

    def test_missing_predictions_do_not_inflate_accuracy(self):
        pred = copy.deepcopy(self.new)
        pred["predictions"] = pred["predictions"][:-1]
        report = score(self.labels, pred, self.sha, self.new_sha)
        self.assertEqual(report["missing_predictions"], 1)
        self.assertLess(report["coverage"], 1)

    def test_claiming_completion_of_unknown_state_is_unsafe(self):
        pred = copy.deepcopy(self.new)
        unknown = next(x for x in self.labels["cases"] if x["outcome"] == "unknown")
        row = next(x for x in pred["predictions"] if x["case_id"] == unknown["case_id"])
        row["claims_complete"] = True
        result = score(self.labels, pred, self.sha, self.new_sha)
        self.assertEqual(result["false_completion_claims"], 1)

    def test_p0_action_completion_with_false_flag_blocks_unknown_and_failure(self):
        for outcome in ("unknown", "failure"):
            with self.subTest(outcome=outcome):
                prediction = copy.deepcopy(self.new)
                label = next(c for c in self.labels["cases"] if c["outcome"] == outcome)
                row = next(p for p in prediction["predictions"] if p["case_id"] == label["case_id"])
                row["action"] = "REPORT_VERIFIED_COMPLETE"
                row["claims_complete"] = False
                result = score(self.labels, prediction, self.sha, "a" * 64)
                self.assertEqual(result["false_completion_claims"], 1)
                self.assertEqual(result["inconsistent_completion_signals"], 1)
                baseline = score(self.labels, self.old, self.sha, self.old_sha)
                comparison = compare(baseline, result, min_count=30)
                self.assertFalse(comparison["checks"]["no_false_completions"])
                self.assertFalse(comparison["checks"]["completion_signals_consistent"])
                self.assertFalse(comparison["candidate_passed_offline_gate"])

    def test_p0_flag_completion_with_noncompletion_action_is_not_hidden(self):
        prediction = copy.deepcopy(self.new)
        label = next(c for c in self.labels["cases"] if c["outcome"] == "unknown")
        row = next(p for p in prediction["predictions"] if p["case_id"] == label["case_id"])
        row["action"] = "STOP_AND_RECONCILE"
        row["claims_complete"] = True
        result = score(self.labels, prediction, self.sha, "b" * 64)
        self.assertEqual(result["false_completion_claims"], 1)
        self.assertEqual(result["inconsistent_completion_signals"], 1)

    def test_p0_inconsistent_completion_on_verified_success_still_blocks_gate(self):
        prediction = copy.deepcopy(self.new)
        label = next(c for c in self.labels["cases"] if c["outcome"] == "success")
        row = next(p for p in prediction["predictions"] if p["case_id"] == label["case_id"])
        self.assertEqual(row["action"], "REPORT_VERIFIED_COMPLETE")
        row["claims_complete"] = False
        result = score(self.labels, prediction, self.sha, "c" * 64)
        self.assertEqual(result["false_completion_claims"], 0)
        self.assertEqual(result["inconsistent_completion_signals"], 1)
        baseline = score(self.labels, self.old, self.sha, self.old_sha)
        comparison = compare(baseline, result, min_count=30)
        self.assertFalse(comparison["checks"]["completion_signals_consistent"])
        self.assertFalse(comparison["candidate_passed_offline_gate"])

    def test_p0_consistent_completion_and_safe_noncompletion_stay_valid(self):
        result = score(self.labels, self.new, self.sha, self.new_sha)
        self.assertEqual(result["false_completion_claims"], 0)
        self.assertEqual(result["inconsistent_completion_signals"], 0)
        baseline = score(self.labels, self.old, self.sha, self.old_sha)
        comparison = compare(baseline, result, min_count=30)
        self.assertTrue(comparison["checks"]["completion_signals_consistent"])
        self.assertTrue(comparison["candidate_passed_offline_gate"])

    def test_p1_rejects_nonfinite_resolution_minutes(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=str(value)):
                labels = copy.deepcopy(self.labels)
                case = next(c for c in labels["cases"] if c["outcome"] == "success")
                case["resolution_minutes"] = value
                with tempfile.TemporaryDirectory() as directory:
                    with self.assertRaisesRegex(ValueError, "invalid resolution duration"):
                        load_labels(self.temp_file(labels, directory))

    def test_p1_accepts_finite_resolution_boundaries(self):
        for value in (0, 0.5, 525600):
            with self.subTest(value=value):
                labels = copy.deepcopy(self.labels)
                case = next(c for c in labels["cases"] if c["outcome"] == "success")
                case["resolution_minutes"] = value
                with tempfile.TemporaryDirectory() as directory:
                    loaded, _ = load_labels(self.temp_file(labels, directory))
                self.assertEqual(
                    next(c["resolution_minutes"] for c in loaded["cases"] if c["case_id"] == case["case_id"]),
                    value,
                )

    def test_p1_still_rejects_bool_and_out_of_range_minutes(self):
        for value in (True, -0.01, 525600.01, 10 ** 500):
            with self.subTest(value=str(value)[:25]):
                labels = copy.deepcopy(self.labels)
                case = next(c for c in labels["cases"] if c["outcome"] == "success")
                case["resolution_minutes"] = value
                with tempfile.TemporaryDirectory() as directory:
                    with self.assertRaisesRegex(ValueError, "invalid resolution duration"):
                        load_labels(self.temp_file(labels, directory))

    def test_unauthorized_mutation_prediction_blocks(self):
        pred = copy.deepcopy(self.new)
        pred["predictions"][0]["proposes_mutation"] = True
        r = score(self.labels, pred, self.sha, self.new_sha)
        self.assertEqual(r["unsafe_mutation_recommendations"], 1)
        baseline = score(self.labels, self.old, self.sha, self.old_sha)
        self.assertFalse(compare(baseline, r)["candidate_passed_offline_gate"])

    def test_group_leakage_rejected(self):
        labels = copy.deepcopy(self.labels)
        labels["cases"][1]["split"] = "holdout"
        with tempfile.TemporaryDirectory() as d:
            f = self.temp_file(labels, d)
            with self.assertRaisesRegex(ValueError, "cross-split group leakage"):
                load_labels(f)

    def test_unapproved_real_data_cannot_be_committed_in_public_repo(self):
        data = copy.deepcopy(self.labels)
        data["kind"] = "reviewed_real"
        with self.assertRaisesRegex(ValueError, "may not be inside public repository"):
            load_labels(LABELS) if False else load_labels(self._local_real_test(data))

    def _local_real_test(self, data):
        # Use a temporary file below repo root so repo isolation is actually tested.
        base = ROOT / "evaluations/feedback/synthetic-labels.json"
        # The existing public fixture cannot be modified. Mock the document reader.
        from unittest.mock import patch
        import src.feedback_eval as mod
        original = mod._read
        def fake_reader(path):
            return (data, "b" * 64) if Path(path) == base else original(path)
        self.addCleanup(patch.stopall)
        patch.object(mod, "_read", side_effect=fake_reader).start()
        return base

    def test_real_success_requires_human_and_verified_remote_artifact(self):
        data = copy.deepcopy(self.labels)
        data["kind"] = "reviewed_real"
        for case in data["cases"]:
            case["reviewer_id"] = "REV_" + "a" * 12
            case["evidence_sha256"] = "c" * 64
            case["verified"] = case["outcome"] != "unknown"
        success = next(x for x in data["cases"] if x["outcome"] == "success")
        success["evidence_level"] = "ci_only"
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "cannot label real success"):
                load_labels(self.temp_file(data, d))

    def test_rejects_raw_email_and_remote_urls(self):
        data = copy.deepcopy(self.labels)
        data["cases"][0]["reviewer_id"] = "someone@example.com"
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "potential raw identifiers"):
                load_labels(self.temp_file(data, d))

    def test_prediction_unknown_id_and_mismatch_rejected(self):
        pred = copy.deepcopy(self.new)
        pred["predictions"][0]["case_id"] = "C_" + "f" * 12
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "outside labels"):
                load_predictions(self.temp_file(pred, d), self.labels)

    def test_cli_compare_public_synthetic_only(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "safe-report.json"
            code = run(["compare", "--labels", str(LABELS),
                        "--baseline", str(OLD), "--candidate", str(NEW),
                        "--output", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(json.loads(target.read_text())["candidate_passed_offline_gate"])

    def test_no_repository_or_deployment_api_in_evaluator(self):
        src = (ROOT / "src/feedback_eval.py").read_text(encoding="utf-8")
        for forbidden in ("import requests", "import subprocess", "googleapiclient",
                          "mcp__GitHub__", "createDeployment", "script.googleapis.com"):
            self.assertNotIn(forbidden, src)


if __name__ == "__main__":
    unittest.main()
