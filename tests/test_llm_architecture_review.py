"""Two independent human architecture scorecard contract (synthetic mock reviews)."""
import json
import tempfile
import unittest
from pathlib import Path

from src.llm_architecture_review import DIMENSIONS, aggregate


class ArchitectureHumanReviewTest(unittest.TestCase):
    def _make(self, directory, bad=None):
        root = Path(directory)
        packet = {
            "schema_version": 1, "dataset_sha256": "a" * 64,
            "model_id_user_supplied": "FAKE_TEST_MODEL",
            "blind_architecture_human_review_pending": True,
            "cases": [
                {"id": "L001", "architecture_outline": "合成架構方案供評分"},
                {"id": "L002", "architecture_outline": "第二份模擬方案"},
            ],
        }
        review_a = {
            "schema_version": 1, "dataset_sha256": packet["dataset_sha256"],
            "model_id_user_supplied": packet["model_id_user_supplied"],
            "reviewer_id": "independent_a", "reviewed_without_other_scorer": True,
            "cases": [{"id": x["id"], "scores": {d: 2 for d in DIMENSIONS}}
                      for x in packet["cases"]],
        }
        review_b = json.loads(json.dumps(review_a))
        review_b["reviewer_id"] = "independent_b"
        if bad:
            bad(packet, review_a, review_b)
        paths = [root / (x + ".json") for x in ("packet", "a", "b")]
        for p, val in zip(paths, (packet, review_a, review_b)):
            p.write_text(json.dumps(val), encoding="utf-8")
        return paths

    def test_dual_review_measures_semantic_dimensions_without_certifying_model(self):
        with tempfile.TemporaryDirectory() as d:
            p, a, b = self._make(d)
            report = aggregate(p, a, b)
            self.assertEqual(report["reviewed_case_count"], 2)
            self.assertEqual(report["exact_cell_agreement"], 1.0)
            self.assertFalse(report["model_identity_verified"])
            self.assertFalse(report["independent_holdout_origin_proven"])
            self.assertFalse(report["human_adjudication_completed"])
            self.assertFalse(report["formal_release_or_deployment_authorized"])
            self.assertNotIn("architecture_outline", json.dumps(report))

    def test_conflicting_human_scores_flag_adjudication(self):
        def differing(_, __, b):
            b["cases"][1]["scores"]["failure_and_rollback"] = 0
        with tempfile.TemporaryDirectory() as d:
            p, a, b = self._make(d, differing)
            report = aggregate(p, a, b)
            self.assertEqual(report["disputed_cells_require_adjudication"], 1)
            self.assertEqual(report["exact_cell_agreement"], 0.9)
            self.assertFalse(report["semantic_review_completed"])

    def test_same_reviewer_is_not_two_independent_people(self):
        def identical(_, __, b):
            b["reviewer_id"] = "independent_a"
        with tempfile.TemporaryDirectory() as d:
            p, a, b = self._make(d, identical)
            with self.assertRaisesRegex(ValueError, "two distinct"):
                aggregate(p, a, b)

    def test_reviewer_score_values_and_dataset_drift_block(self):
        for change, pattern in (
            (lambda _, __, b: b["cases"][0]["scores"].update(
                {"requirement_coverage": 3}), "invalid review"),
            (lambda _, __, b: b.update({"dataset_sha256": "b" * 64}),
             "identity, model, dataset"),
            (lambda _, __, b: b["cases"].pop(), "case count"),
            (lambda _, __, b: b.update({"reviewed_without_other_scorer": False}),
             "identity, model, dataset"),
        ):
            with tempfile.TemporaryDirectory() as d:
                p, a, b = self._make(d, change)
                with self.assertRaisesRegex(ValueError, pattern):
                    aggregate(p, a, b)

    def test_reviews_inside_repository_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside public repo"):
            aggregate(Path(__file__), Path(__file__), Path(__file__))


if __name__ == "__main__":
    unittest.main()
