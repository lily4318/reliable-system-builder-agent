"""Synthetic sandbox policy replay tests; no live Agent, no external service."""
import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

from src.e2e_eval import ROOT, load_bundle, score
from src.e2e_sandbox import _load_plan, main, replay

E2E = ROOT / "evaluations/e2e"
TASKSET = E2E / "synthetic-candidate.json"
PLAN = E2E / "sandbox-plan.json"
PLAN_SCHEMA = ROOT / "schemas/e2e-sandbox-plan.schema.json"
BUNDLE_SCHEMA = ROOT / "schemas/e2e-execution-bundle.schema.json"


class E2ESandboxTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.taskset, _ = load_bundle(TASKSET)
        cls.plan = _load_plan(PLAN)

    def mutate(self, fn):
        plan = copy.deepcopy(self.plan)
        fn(plan)
        return replay(self.taskset, plan)

    @staticmethod
    def case(bundle, number):
        tid = "C_" + format(number, "012x")
        return next(e for e in bundle["episodes"] if e["task_id"] == tid)

    def test_deterministic_replay_produces_executable_evidence_bundle(self):
        a = replay(self.taskset, self.plan)
        b = replay(self.taskset, self.plan)
        self.assertEqual(a, b)
        self.assertEqual(a["kind"], "synthetic")
        self.assertEqual(a["tasks"], self.taskset["tasks"])
        self.assertEqual(a["build"], self.taskset["build"])
        self.assertNotEqual(a["episodes"], self.taskset["episodes"])
        report = score(a, "f"*64)
        self.assertEqual(report["summary"]["eligible_tasks"], 7)
        self.assertEqual(report["summary"]["verified_success"], 3)
        self.assertEqual(report["summary"]["duplicate_nonidempotent_writes"], 1)
        self.assertEqual(report["summary"]["unresolved_partial_write"], 1)
        self.assertEqual(report["summary"]["false_completion"], 1)
        self.assertFalse(report["human_attestation_external_verification"])

    def test_replayed_bundle_conforms_to_e2e_schema_and_semantic_validator(self):
        data = replay(self.taskset, self.plan)
        validator = Draft202012Validator(json.loads(BUNDLE_SCHEMA.read_text()))
        validator.validate(data)
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / "generated.json"
            dest.write_text(json.dumps(data))
            loaded, digest = load_bundle(dest)
        self.assertEqual(loaded, data)
        self.assertEqual(len(digest), 64)

    def test_sandbox_plan_schema_accepts_only_public_synthetic_case(self):
        schema = json.loads(PLAN_SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        validator.validate(self.plan)
        bad = copy.deepcopy(self.plan)
        bad["cases"][0]["private_raw_log"] = "should not leak"
        with self.assertRaises(ValidationError):
            validator.validate(bad)
        bad = copy.deepcopy(self.plan)
        bad["kind"] = "reviewed_real"
        with self.assertRaises(ValidationError):
            validator.validate(bad)

    def test_timeout_applied_is_reconciled_to_same_target(self):
        out = replay(self.taskset, self.plan)
        ops = self.case(out, 1)["attempts"][0]["operations"]
        self.assertEqual(ops[0]["write_state"], "UNKNOWN")
        self.assertEqual(ops[1]["operation"], "GET_READBACK")
        self.assertEqual(ops[1]["reconciles_operation_id"], ops[0]["operation_id"])
        self.assertEqual(ops[1]["readback_state"], "APPLIED")

    def test_timeout_not_applied_generates_real_negative_synthetic_receipt(self):
        out = replay(self.taskset, self.plan)
        e = self.case(out, 7)
        op = e["attempts"][0]["operations"]
        self.assertEqual(op[1]["reconciles_operation_id"], op[0]["operation_id"])
        self.assertEqual(op[1]["readback_state"], "NOT_APPLIED")
        self.assertEqual(e["adjudication"]["outcome"], "VERIFIED_FAILURE")
        self.assertFalse(e["receipts"][0]["passed"])

    def test_partial_write_remains_unresolved_and_is_not_fabricated_failure(self):
        out = replay(self.taskset, self.plan)
        e = self.case(out, 4)
        self.assertEqual(e["adjudication"]["outcome"], "PARTIAL_WRITE_UNRESOLVED")
        self.assertFalse(e["receipts"])
        self.assertEqual(e["attempts"][0]["operations"][0]["write_state"], "PARTIAL")

    def test_duplicate_nonidempotent_write_is_unsafe_even_with_readback(self):
        out = replay(self.taskset, self.plan)
        e = self.case(out, 8)
        self.assertEqual(e["receipts"][0]["passed"], True)
        self.assertEqual(e["failure"]["agent_response"], "UNSAFE_ACTION")
        self.assertNotEqual(e["adjudication"]["outcome"], "VERIFIED_SUCCESS")

    def test_no_observation_cannot_create_passed_receipt(self):
        def change(plan):
            plan["cases"][1]["steps"] = []
        out = self.mutate(change)
        e = self.case(out, 2)
        self.assertEqual(e["receipts"], [])
        self.assertNotEqual(e["adjudication"]["outcome"], "VERIFIED_SUCCESS")

    def test_no_email_delivery_proof_from_provider_accepted_only(self):
        out = replay(self.taskset, self.plan)
        e = self.case(out, 5)
        self.assertFalse(e["receipts"][0]["passed"])
        self.assertNotEqual(e["adjudication"]["outcome"], "VERIFIED_SUCCESS")

    def test_frozen_taskset_forbids_target_outside_criterion(self):
        def change(plan):
            plan["cases"][0]["steps"][0]["target_id"] = "P_"+"f"*12
        with self.assertRaisesRegex(ValueError, "outside frozen task spec"):
            self.mutate(change)

    def test_sandbox_rejects_real_kind_and_real_taskset(self):
        bad = copy.deepcopy(self.plan)
        bad["kind"] = "reviewed_real"
        with self.assertRaisesRegex(ValueError, "only synthetic"):
            replay(self.taskset, bad)
        tasks = copy.deepcopy(self.taskset)
        tasks["kind"] = "reviewed_real"
        with self.assertRaisesRegex(ValueError, "only synthetic"):
            replay(tasks, self.plan)

    def test_sandbox_rejects_readonly_and_ineligible_execution(self):
        def change(plan):
            plan["cases"].append({
                **copy.deepcopy(plan["cases"][0]),
                "task_id": "C_" + format(6, "012x"),
            })
        with self.assertRaisesRegex(ValueError, "readonly/ineligible"):
            self.mutate(change)

    def test_sandbox_rejects_duplicate_tasks(self):
        bad = copy.deepcopy(self.plan)
        bad["cases"].append(copy.deepcopy(bad["cases"][0]))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, "duplicate sandbox task"):
                _load_plan(p)

    def test_sandbox_rejects_private_free_text(self):
        bad = copy.deepcopy(self.plan)
        bad["cases"][0]["notes"] = "private"
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, "invalid fields"):
                _load_plan(p)

    def test_sandbox_rejects_fault_on_read(self):
        bad = copy.deepcopy(self.plan)
        bad["cases"][0]["steps"][1]["fault"] = "TIMEOUT_APPLIED"
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, "read actions cannot inject"):
                _load_plan(p)

    def test_sandbox_rejects_malformed_cost_and_claim(self):
        for case_field, val, text in (
            ("cost_microusd", -1, "invalid nonnegative"),
            ("cost_microusd", True, "invalid nonnegative"),
            ("claim_complete", "yes", "invalid claim"),
        ):
            bad = copy.deepcopy(self.plan)
            bad["cases"][0][case_field] = val
            with self.subTest(field=case_field, value=val):
                with tempfile.TemporaryDirectory() as d:
                    p = Path(d) / "bad.json"
                    p.write_text(json.dumps(bad))
                    with self.assertRaisesRegex(ValueError, text):
                        _load_plan(p)

    def test_sandbox_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text('{"schema_version":1,"schema_version":1,"kind":"synthetic","cases":[]}')
            with self.assertRaisesRegex(ValueError, "duplicate plan JSON key"):
                _load_plan(p)

    def test_sandbox_rejects_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text('{"schema_version":1,"kind":"synthetic","cases":[NaN]}')
            with self.assertRaisesRegex(ValueError, "nonfinite plan number"):
                _load_plan(p)

    def test_cli_creates_valid_new_bundle_without_touching_source(self):
        source_bytes = PLAN.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "new.json"
            with contextlib.redirect_stdout(io.StringIO()) as stream:
                result = main(["--taskset", str(TASKSET), "--plan", str(PLAN), "--output", str(output)])
            self.assertEqual(result, 0)
            summary = json.loads(stream.getvalue())
            self.assertTrue(summary["synthetic_only"])
            self.assertFalse(summary["external_agent_executed"])
            self.assertFalse(summary["real_world_e2e_certified"])
            self.assertEqual(summary["verified_synthetic_success"], 3)
            loaded, _ = load_bundle(output)
            self.assertEqual(len(loaded["episodes"]), 7)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["--taskset", str(TASKSET), "--plan", str(PLAN),
                                       "--output", str(output)]), 2)
        self.assertEqual(PLAN.read_bytes(), source_bytes)

    def test_no_live_connectors_or_network_execution(self):
        code = (ROOT / "src/e2e_sandbox.py").read_text(encoding="utf-8")
        for forbidden in ("import requests", "urllib.request", "googleapiclient",
                          "subprocess", "mcp__GitHub__", "script.googleapis.com",
                          "socket.create_connection", "httpx"):
            self.assertNotIn(forbidden, code)


if __name__ == "__main__":
    unittest.main()
