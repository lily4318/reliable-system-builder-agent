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
        self.assertFalse(report["human_label_attested"])
        self.assertFalse(report["independent_blind_holdout_proven"])
        self.assertFalse(report["model_weights_trained"])

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
            case["verified"] = True
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
