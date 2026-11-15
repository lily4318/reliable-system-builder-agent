"""Public synthetic structural controls; no external course content."""
import copy
import tempfile
import unittest
from pathlib import Path

from src.curriculum_coverage import CATALOG, MATRIX, load_json, validate

PIN = "a" * 64
URL = "https://example.invalid/synthetic-training"


def unit(uid, owner="developer", skill="implement-feature", prerequisites=None):
    return {"id": uid, "source_url": URL, "source_sha256": PIN,
            "access": "READABLE", "owner": owner, "collaborators": ["qa-uat"],
            "skill": skill, "prerequisites": prerequisites or [],
            "maturity": 0, "evidence": {}}


def inventory(*units):
    return {"schema_version": 1, "source_links": [URL],
            "inventory_status": "COMPLETE_DECLARED", "inventory_sha256": PIN,
            "expected_ids": [u["id"] for u in units], "units": list(units)}


class CurriculumCoverageTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_json(CATALOG)

    def check(self, data):
        return validate(data, self.catalog)

    def test_actual_blocked_matrix_has_no_completion(self):
        report = self.check(load_json(MATRIX))
        self.assertEqual(report["inventory_status"], "BLOCKED_SOURCE")
        self.assertTrue(report["unknown_total"])
        self.assertIsNone(report["coverage_percent"])
        self.assertEqual(report["review_candidates"], [])
        self.assertFalse(report["curriculum_completed"])

    def test_complete_declared_not_verified(self):
        report = self.check(inventory(unit("one")))
        self.assertEqual(report["review_candidates"], ["one"])
        for key in ("source_verified", "evidence_verified", "curriculum_completed",
                    "model_improvement_verified"):
            self.assertFalse(report[key])

    def test_missing_and_duplicate_rejected(self):
        data = inventory(unit("one"), unit("two"))
        data["units"].pop()
        with self.assertRaisesRegex(ValueError, "missing inventory"):
            self.check(data)
        data["units"].append(copy.deepcopy(data["units"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate/unknown"):
            self.check(data)

    def test_specialist_and_collaborator_rejections(self):
        for key, value in (("owner", ["developer", "architect"]),
                           ("owner", "architect"), ("collaborators", ["developer"]),
                           ("collaborators", ["qa-uat", "qa-uat"]),
                           ("skill", "not-a-skill")):
            with self.subTest(key=key, value=value):
                data = inventory(unit("one"))
                data["units"][0][key] = value
                with self.assertRaises(ValueError):
                    self.check(data)

    def test_maturity_requires_evidence_and_readability(self):
        for change in ({"maturity": True}, {"maturity": 3}, {"source_sha256": None},
                       {"access": "UNREAD", "maturity": 1, "source_sha256": None,
                        "evidence": {"principles": "ref"}}):
            with self.subTest(change=change):
                data = inventory(unit("one"))
                data["units"][0].update(change)
                with self.assertRaises(ValueError):
                    self.check(data)

    def test_prerequisite_review_candidate_not_approval(self):
        first = unit("one")
        second = unit("two", prerequisites=["one"])
        data = inventory(first, second)
        self.assertEqual(self.check(data)["review_candidates"], ["one"])
        first.update(maturity=2, evidence={"principles": "ref1", "analysis": "ref2"})
        self.assertEqual(self.check(data)["review_candidates"], ["one", "two"])
        self.assertFalse(self.check(data)["evidence_verified"])

    def test_cycle_unknown_and_self_dependency(self):
        for a, b in ((["two"], ["one"]), (["missing"], []), (["one"], [])):
            with self.subTest(a=a, b=b):
                with self.assertRaises(ValueError):
                    self.check(inventory(unit("one", prerequisites=a),
                                         unit("two", prerequisites=b)))

    def test_partial_missing_dependency_not_ready(self):
        data = inventory(unit("two", prerequisites=["one"]))
        data["inventory_status"] = "PARTIAL"
        data["expected_ids"].insert(0, "one")
        report = self.check(data)
        self.assertTrue(report["unknown_total"])
        self.assertEqual(report["review_candidates"], [])

    def test_blocked_source_cannot_invent_chapters(self):
        data = inventory(unit("one"))
        data["inventory_status"] = "BLOCKED_SOURCE"
        with self.assertRaises(ValueError):
            self.check(data)

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "matrix.json"
            path.write_text('{"owner":"architect","owner":"developer"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                load_json(path)
