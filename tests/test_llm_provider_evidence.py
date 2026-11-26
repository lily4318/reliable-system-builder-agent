"""Synthetic provenance attacks only. Never executes an API or spends tokens."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.llm_requirements_eval import PROMPT, PUBLIC_DATASET, ROOT, load_dataset, runner_payload
from src.llm_provider_evidence import audit_evidence


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ProviderEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset, cls.dataset_sha = load_dataset()

    def fixture(self, directory):
        root = Path(directory)
        runner = root / "synthetic_runner.py"
        runner.write_text("# synthetic fake only, never contacts model\n", encoding="utf-8")
        cfg = {
            "schema_version": 1, "provider": "synthetic-provider",
            "model_id": "synthetic-model-2026",
            "runner_path": str(runner), "runner_sha256": sha(runner.read_bytes()),
            "prompt_sha256": sha(PROMPT.encode("utf-8")),
            "evaluator_sha256": sha((ROOT / "src/llm_requirements_eval.py").read_bytes()),
            "approval_scope": "public_dev", "approval_reference": "synthetic-authority",
            "data_handling_reviewed": True,
        }
        config_path = root / "private_config.json"
        config_path.write_text(json.dumps(cfg), encoding="utf-8")
        response = {
            "provider": cfg["provider"], "model": cfg["model_id"],
            "model_version": "synthetic-version-01",
            "request_id": "request_synthetic_0001",
            "response_id": "response_synthetic_0001",
            "created_at_utc": "2026-11-13T01:00:02Z", "status": "completed",
            "output": {"kind": "SYNTHETIC_DO_NOT_USE_AS_REAL_LLM_OUTPUT"},
        }
        response_path = root / "normalized_response.json"
        response_path.write_text(json.dumps(response, ensure_ascii=False), encoding="utf-8")
        case = self.dataset["cases"][0]
        canonical = json.dumps(runner_payload(case), sort_keys=True, ensure_ascii=False,
                               separators=(",", ":")).encode("utf-8")
        manifest = {
            "schema_version": 1, "split": "public_dev", "case_id": case["id"],
            "dataset_sha256": self.dataset_sha, "provider": cfg["provider"],
            "requested_model": cfg["model_id"],
            "requested_model_version": response["model_version"],
            "runner_sha256": cfg["runner_sha256"],
            "prompt_sha256": cfg["prompt_sha256"],
            "evaluator_sha256": cfg["evaluator_sha256"],
            "harness_payload_sha256": sha(canonical),
            "request_id": response["request_id"],
            "response_id": response["response_id"],
            "response_path": str(response_path),
            "response_sha256": sha(response_path.read_bytes()),
            "response_origin": "unverified_local_normalized_copy",
            "call_started_at_utc": "2026-11-13T01:00:01Z",
            "call_finished_at_utc": "2026-11-13T01:00:03Z",
            "authorization": {
                "scope": "public_dev", "approval_reference": cfg["approval_reference"],
                "approved_by_ref": "synthetic-reviewer",
                "approved_at_utc": "2026-11-12T00:00:00Z",
                "expires_at_utc": "2026-11-15T00:00:00Z",
                "data_handling_reviewed": True,
            },
        }
        path = root / "private_manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path, config_path, runner, response_path, cfg, response, manifest

    def reissue(self, manifest_path, response_path, manifest, response):
        response_path.write_text(json.dumps(response, ensure_ascii=False), encoding="utf-8")
        manifest["response_sha256"] = sha(response_path.read_bytes())
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    def test_without_private_files_blocks_and_makes_no_model_claim(self):
        result = audit_evidence()
        self.assertEqual(result["status"], "BLOCKED_MISSING_PRIVATE_EVIDENCE_OR_CONFIG")
        self.assertFalse(result["actual_model_accuracy_measured"])
        self.assertFalse(result["actual_llm_executed_by_this_audit"])

    def test_synthetic_consistency_never_authenticates_fake_provider(self):
        with tempfile.TemporaryDirectory() as d:
            path, config, _, _, _, response, _ = self.fixture(d)
            result = audit_evidence(path, config)
            self.assertTrue(result["local_integrity_consistent"])
            self.assertEqual(result["status"], "MATCHED_LOCAL_EVIDENCE_PROVIDER_AND_APPROVAL_UNVERIFIED")
            for field in ("provider_origin_independently_verified",
                          "model_version_provider_authenticated",
                          "provider_response_id_independently_checked",
                          "authorization_independently_verified",
                          "live_inference_authorized_by_this_audit",
                          "actual_model_accuracy_measured"):
                self.assertFalse(result[field])
            dump = json.dumps(result)
            self.assertNotIn(response["request_id"], dump)
            self.assertNotIn(response["response_id"], dump)
            self.assertNotIn("synthetic-authority", dump)
            self.assertNotIn(str(path), dump)
            self.assertEqual(len(result["request_id_sha256"]), 64)

    def test_response_id_spoof_fails_despite_recomputed_sha(self):
        with tempfile.TemporaryDirectory() as d:
            path, cfg, _, response_path, _, response, manifest = self.fixture(d)
            response["request_id"] = "request_forged_000000"
            self.reissue(path, response_path, manifest, response)
            self.assertEqual(audit_evidence(path, cfg)["status"],
                             "BLOCKED_REQUEST_RESPONSE_ID_MISMATCH")

    def test_version_and_model_mismatch_negative(self):
        for key, wrong in (("model_version", "not-the-declared-version"),
                           ("model", "different-unverified-model"),
                           ("provider", "some-other-provider")):
            with tempfile.TemporaryDirectory() as d:
                path, cfg, _, response_path, _, response, manifest = self.fixture(d)
                response[key] = wrong
                self.reissue(path, response_path, manifest, response)
                self.assertEqual(audit_evidence(path, cfg)["status"],
                                 "BLOCKED_RESPONSE_MODEL_OR_VERSION_MISMATCH")

    def test_modified_response_bytes_fail_without_matching_sha(self):
        with tempfile.TemporaryDirectory() as d:
            path, cfg, _, response_path, _, response, _ = self.fixture(d)
            response["response_id"] = "response_forged_00001"
            response_path.write_text(json.dumps(response), encoding="utf-8")
            self.assertEqual(audit_evidence(path, cfg)["status"],
                             "BLOCKED_RESPONSE_BYTES_TAMPERED")

    def test_runner_sha_drift_blocks_before_provider_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            path, cfg, runner, _, _, _, _ = self.fixture(d)
            runner.write_text("# changed runner source\n", encoding="utf-8")
            self.assertEqual(audit_evidence(path, cfg)["status"],
                             "BLOCKED_RUNNER_CONFIG_OR_SOURCE_INTEGRITY")

    def test_prompt_payload_and_dataset_hash_conflicts(self):
        for key, expected in (
            ("prompt_sha256", "BLOCKED_SOURCE_HASH_MISMATCH"),
            ("evaluator_sha256", "BLOCKED_SOURCE_HASH_MISMATCH"),
            ("harness_payload_sha256", "BLOCKED_HARNESS_TO_RUNNER_PAYLOAD_SHA"),
            ("dataset_sha256", "BLOCKED_DATASET_SHA_MISMATCH"),
        ):
            with tempfile.TemporaryDirectory() as d:
                path, cfg, _, _, _, _, manifest = self.fixture(d)
                manifest[key] = "0" * 64
                path.write_text(json.dumps(manifest), encoding="utf-8")
                self.assertEqual(audit_evidence(path, cfg)["status"], expected)

    def test_wrong_case_and_holdout_usage_fail(self):
        for mutation, expected in (
            ({"case_id": "L999"}, "BLOCKED_UNKNOWN_PUBLIC_CASE"),
            ({"split": "holdout"}, "BLOCKED_EVIDENCE_SCHEMA_OR_SCOPE"),
        ):
            with tempfile.TemporaryDirectory() as d:
                path, cfg, _, _, _, _, manifest = self.fixture(d)
                manifest.update(mutation)
                path.write_text(json.dumps(manifest), encoding="utf-8")
                self.assertEqual(audit_evidence(path, cfg)["status"], expected)

    def test_expired_approval_and_out_of_order_response_fail(self):
        for key, val in (("expires_at_utc", "2026-11-13T00:00:00Z"),
                         ("approved_at_utc", "2026-11-13T01:00:04Z")):
            with tempfile.TemporaryDirectory() as d:
                path, cfg, _, _, _, _, manifest = self.fixture(d)
                manifest["authorization"][key] = val
                path.write_text(json.dumps(manifest), encoding="utf-8")
                self.assertEqual(audit_evidence(path, cfg)["status"],
                                 "BLOCKED_AUTHORIZATION_WINDOW_OR_CALL_ORDER")
        with tempfile.TemporaryDirectory() as d:
            path, cfg, _, response_path, _, response, manifest = self.fixture(d)
            response["created_at_utc"] = "2026-11-13T01:00:09Z"
            self.reissue(path, response_path, manifest, response)
            self.assertEqual(audit_evidence(path, cfg)["status"],
                             "BLOCKED_RESPONSE_CHRONOLOGY")

    def test_claims_of_authenticity_or_extra_credentials_rejected(self):
        for key, value in (
            ("response_origin", "independently_verified_by_provider"),
            ("provider_signature_verified", True),
            ("api_key", "NEVER_LOG_SENSITIVE_VALUE"),
        ):
            with tempfile.TemporaryDirectory() as d:
                path, cfg, _, _, _, _, manifest = self.fixture(d)
                manifest[key] = value
                path.write_text(json.dumps(manifest), encoding="utf-8")
                result = audit_evidence(path, cfg)
                self.assertTrue(result["status"].startswith("BLOCKED_"))
                self.assertNotIn("NEVER_LOG_SENSITIVE_VALUE", json.dumps(result))

    def test_wrong_approval_scope_reference_or_data_handling(self):
        for key, value in (("scope", "holdout"), ("approval_reference", "different"),
                           ("data_handling_reviewed", False)):
            with tempfile.TemporaryDirectory() as d:
                path, cfg, _, _, _, _, manifest = self.fixture(d)
                manifest["authorization"][key] = value
                path.write_text(json.dumps(manifest), encoding="utf-8")
                self.assertEqual(audit_evidence(path, cfg)["status"],
                                 "BLOCKED_AUTHORIZATION_SCOPE_OR_REFERENCE")

    def test_public_file_and_missing_response_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path, cfg, _, _, _, _, manifest = self.fixture(d)
            manifest["response_path"] = str(ROOT / "evaluations/llm/public_dev_cases.json")
            path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(audit_evidence(path, cfg)["status"],
                             "BLOCKED_RESPONSE_UNAVAILABLE_OR_PUBLIC")
            self.assertEqual(audit_evidence(ROOT / "AGENTS.md", cfg)["status"],
                             "BLOCKED_PRIVATE_EVIDENCE_UNAVAILABLE")

    def test_fake_completed_response_without_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path, cfg, _, response_path, _, response, manifest = self.fixture(d)
            response["output"] = "invalid"
            self.reissue(path, response_path, manifest, response)
            self.assertEqual(audit_evidence(path, cfg)["status"],
                             "BLOCKED_NORMALIZED_RESPONSE_OUTPUT")


if __name__ == "__main__":
    unittest.main()
