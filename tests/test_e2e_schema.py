"""Draft 2020-12 schema conformance tests, public synthetic cases only."""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

from src.e2e_eval import ROOT

SCHEMA = ROOT / "schemas/e2e-execution-bundle.schema.json"
BASE = ROOT / "evaluations/e2e/synthetic-baseline.json"
CANDIDATE = ROOT / "evaluations/e2e/synthetic-candidate.json"


class E2ESchemaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)
        cls.baseline = json.loads(BASE.read_text(encoding="utf-8"))

    def test_schemas_valid_and_both_public_fixtures_conform(self):
        for path in (BASE, CANDIDATE):
            with self.subTest(path=path.name):
                self.validator.validate(json.loads(path.read_text()))

    def test_unknown_private_payload_field_rejected(self):
        bad = copy.deepcopy(self.baseline)
        bad["episodes"][0]["raw_log"] = "private user email"
        with self.assertRaises(ValidationError):
            self.validator.validate(bad)

    def test_missing_environment_snapshot_rejected(self):
        bad = copy.deepcopy(self.baseline)
        del bad["tasks"][0]["environment_snapshot_sha256"]
        with self.assertRaises(ValidationError):
            self.validator.validate(bad)

    def test_evidence_target_is_required(self):
        bad = copy.deepcopy(self.baseline)
        successful = next(e for e in bad["episodes"] if e["receipts"])
        del successful["receipts"][0]["target_id"]
        with self.assertRaises(ValidationError):
            self.validator.validate(bad)

    def test_wrong_sha_format_and_float_cost_rejected(self):
        bad = copy.deepcopy(self.baseline)
        bad["build"]["runner_commit_sha"] = "short"
        with self.assertRaises(ValidationError):
            self.validator.validate(bad)
        bad = copy.deepcopy(self.baseline)
        bad["episodes"][0]["cost"]["items"][0]["amount_microusd"] = 0.25
        with self.assertRaises(ValidationError):
            self.validator.validate(bad)

    def test_schema_rejects_unlisted_operation_and_receipt_kind(self):
        for field,value in (("operation", "UPLOAD_SECRET"), ("write_state", "MAGIC")):
            bad = copy.deepcopy(self.baseline)
            bad["episodes"][0]["attempts"][0]["operations"][0][field] = value
            with self.subTest(field=field):
                with self.assertRaises(ValidationError):
                    self.validator.validate(bad)


if __name__ == "__main__":
    unittest.main()
