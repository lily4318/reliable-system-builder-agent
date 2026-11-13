"""No provider calls: audit private runner configuration using synthetic local files."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.llm_requirements_eval import PROMPT, ROOT
from src.llm_runner_preflight import audit


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class RunnerPreflightTest(unittest.TestCase):
    def config(self, directory: str) -> tuple[Path, Path, dict]:
        folder = Path(directory)
        runner = folder / "fake_script.py"
        runner.write_text("print('protocol test only; no real LLM')\n", encoding="utf-8")
        cfg = {
            "schema_version": 1, "provider": "synthetic_provider_not_real",
            "model_id": "synthetic_model_not_real",
            "runner_path": str(runner),
            "runner_sha256": digest(runner.read_bytes()),
            "prompt_sha256": digest(PROMPT.encode("utf-8")),
            "evaluator_sha256": digest((ROOT / "src/llm_requirements_eval.py").read_bytes()),
            "approval_scope": "public_dev", "approval_reference": "synthetic_example_only",
            "data_handling_reviewed": True,
        }
        path = folder / "private_runner_manifest.json"
        path.write_text(json.dumps(cfg), encoding="utf-8")
        return path, runner, cfg

    def test_missing_config_blocks_inference_without_claiming_any_model_run(self):
        result = audit()
        self.assertEqual(result["status"], "BLOCKED_NO_PRIVATE_RUNNER_CONFIG")
        self.assertFalse(result["live_inference_authorized_by_this_audit"])
        self.assertFalse(result["real_llm_executed"])
        self.assertFalse(result["model_accuracy_measured"])

    def test_matching_local_hashes_never_authenticate_provider_or_human_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _, cfg = self.config(directory)
            report = audit(path)
            self.assertTrue(report["runner_script_sha256_verified"])
            self.assertTrue(report["prompt_sha256_verified"])
            self.assertTrue(report["evaluator_sha256_verified"])
            self.assertEqual(report["status"],
                "CONFIG_HASHES_MATCH_PROVIDER_AND_APPROVAL_STILL_UNVERIFIED")
            self.assertFalse(report["model_id_provider_authenticated"])
            self.assertFalse(report["approval_independently_verified"])
            self.assertFalse(report["provider_response_origin_verified"])
            self.assertFalse(report["live_inference_authorized_by_this_audit"])
            self.assertFalse(report["real_llm_executed"])
            self.assertNotIn(cfg["model_id"], json.dumps(report))
            self.assertNotIn(cfg["runner_path"], json.dumps(report))
            self.assertNotIn(cfg["approval_reference"], json.dumps(report))

    def test_runner_change_after_manifest_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            path, script, _ = self.config(directory)
            script.write_text("print('different script')\n", encoding="utf-8")
            report = audit(path)
            self.assertEqual(report["status"], "BLOCKED_INTEGRITY_MISMATCH")
            self.assertFalse(report["runner_script_sha256_verified"])

    def test_prompt_or_evaluator_sha_drift_blocks(self):
        for key in ("prompt_sha256", "evaluator_sha256"):
            with tempfile.TemporaryDirectory() as directory:
                path, _, cfg = self.config(directory)
                cfg[key] = "0" * 64
                path.write_text(json.dumps(cfg), encoding="utf-8")
                report = audit(path)
                self.assertEqual(report["status"], "BLOCKED_INTEGRITY_MISMATCH")
                self.assertFalse(report[key + "_verified"])

    def test_unknown_key_may_hold_a_secret_and_must_be_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _, cfg = self.config(directory)
            cfg["api_key"] = "secret_must_not_appear_in_output"
            path.write_text(json.dumps(cfg), encoding="utf-8")
            report = audit(path)
            self.assertEqual(report["status"], "BLOCKED_CONFIG_SCHEMA_OR_SCOPE")
            self.assertNotIn(cfg["api_key"], json.dumps(report))

    def test_missing_approval_or_disallowed_holdout_scope_blocks(self):
        for mutation in (
            {"approval_scope": "holdout"},
            {"approval_reference": ""},
            {"data_handling_reviewed": False},
            {"model_id": ""},
        ):
            with tempfile.TemporaryDirectory() as directory:
                path, _, cfg = self.config(directory)
                cfg.update(mutation)
                path.write_text(json.dumps(cfg), encoding="utf-8")
                report = audit(path)
                self.assertTrue(report["status"].startswith("BLOCKED_"))

    def test_private_config_and_runner_cannot_reside_in_public_repo(self):
        self.assertEqual(audit(ROOT / ".github/workflows/agent-ci.yml")["status"],
                         "BLOCKED_CONFIG_MISSING_OR_PUBLIC")
        with tempfile.TemporaryDirectory() as directory:
            path, _, cfg = self.config(directory)
            cfg["runner_path"] = str(ROOT / "src/llm_requirements_eval.py")
            path.write_text(json.dumps(cfg), encoding="utf-8")
            self.assertEqual(audit(path)["status"], "BLOCKED_RUNNER_MISSING_OR_PUBLIC")

    def test_runner_not_absolute_and_invalid_hash_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _, cfg = self.config(directory)
            cfg["runner_path"] = "some-relative-file.py"
            path.write_text(json.dumps(cfg), encoding="utf-8")
            self.assertEqual(audit(path)["status"], "BLOCKED_RUNNER_NOT_ABSOLUTE")
            cfg["runner_path"] = str(Path(directory) / "fake_script.py")
            cfg["runner_sha256"] = "not_a_hash"
            path.write_text(json.dumps(cfg), encoding="utf-8")
            self.assertEqual(audit(path)["status"], "BLOCKED_INTEGRITY_HASH_FORMAT")

    def test_fake_provider_receipt_never_changes_audit_to_live_permission(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _, cfg = self.config(directory)
            for name in ("provider_request_id", "provider_response_origin_verified",
                         "live_inference_authorized_by_this_audit"):
                cfg[name] = "fabricated"
                path.write_text(json.dumps(cfg), encoding="utf-8")
                result = audit(path)
                self.assertEqual(result["status"], "BLOCKED_CONFIG_SCHEMA_OR_SCOPE")
                del cfg[name]


if __name__ == "__main__":
    unittest.main()
