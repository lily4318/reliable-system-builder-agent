"""Synthetic offline dual-source, spoofing, duplicate and replay regressions.

Fixtures are generated locally and are NOT official provider receipts.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import test_llm_provider_evidence as local_fixture
from src.llm_provider_dual_source import audit_two_sources


def canonical_sha(obj):
    return hashlib.sha256(json.dumps(
        obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def save(path, val):
    path.write_text(json.dumps(val, ensure_ascii=False), encoding="utf-8")


class TwoSourceReconciliationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        local_fixture.ProviderEvidenceTest.setUpClass()

    def fixture(self, directory):
        root = Path(directory)
        local_dir, export_dir, ledger_dir = (
            root / "runner-local", root / "out-of-band-export", root / "ledger"
        )
        for folder in (local_dir, export_dir, ledger_dir):
            folder.mkdir()
        f = local_fixture.ProviderEvidenceTest()
        local, config, runner, resp_path, cfg, resp, manifest = f.fixture(local_dir)
        official = {
            "schema_version": 1,
            "source_kind": "claimed_provider_readonly_export",
            "acquisition_channel": "out_of_band_readonly",
            "retrieved_by_ref": "independent_reviewer_ref",
            "runner_operator_ref": "runner_operator_ref",
            "official_account_ref": "synthetic_account_ref",
            "collected_at_utc": "2026-11-13T01:10:00Z",
            "records": [{
                "provider": cfg["provider"],
                "request_id": resp["request_id"],
                "response_id": resp["response_id"],
                "model": resp["model"],
                "model_version": resp["model_version"],
                "status": "completed",
                "created_at_utc": resp["created_at_utc"],
                "output_sha256": canonical_sha(resp["output"]),
            }],
        }
        ledger = {
            "schema_version": 1, "scope": "public_dev",
            "snapshot_at_utc": "2026-11-13T00:55:00Z",
            "prior_requests": [{
                "request_id": "previous_request_000001",
                "response_id": "previous_response_000001",
            }],
        }
        official_path = export_dir / "provider_readonly_export.json"
        ledger_path = ledger_dir / "previous_ids.json"
        save(official_path, official)
        save(ledger_path, ledger)
        return [local, config, official_path, ledger_path], (
            manifest, resp, official, ledger, resp_path
        )

    def audit(self, paths):
        return audit_two_sources(*paths)

    def test_no_private_provider_source_fails_closed(self):
        r = audit_two_sources()
        self.assertEqual(r["status"], "BLOCKED_DUAL_SOURCE_AND_LEDGER_REQUIRED")
        self.assertFalse(r["official_api_response_authenticated"])
        self.assertFalse(r["human_authorization_independently_verified"])

    def test_independent_copies_locally_match_but_not_provider_authenticated(self):
        with tempfile.TemporaryDirectory() as d:
            paths, data = self.fixture(d)
            result = self.audit(paths)
            self.assertTrue(result["two_source_fields_consistent"])
            self.assertTrue(result["local_integrity_consistent"])
            self.assertEqual(result["status"],
                             "TWO_SOURCE_FIELDS_MATCH_ORIGIN_AND_AUTHORIZATION_UNVERIFIED")
            for field in ("official_api_response_authenticated",
                          "external_export_origin_authenticated",
                          "human_authorization_independently_verified",
                          "replay_free_globally_verified",
                          "model_version_provider_authenticated",
                          "real_llm_performance_measured"):
                self.assertFalse(result[field])
            report = json.dumps(result)
            self.assertNotIn(data[1]["request_id"], report)
            self.assertNotIn(data[1]["response_id"], report)
            self.assertEqual(result["provider_calls_by_audit"], 0)
            self.assertEqual(result["registry_mutations_by_audit"], 0)

    def test_forged_both_matching_copies_still_never_becomes_authenticated(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (manifest, response, official, ledger, resp_path) = self.fixture(d)
            manifest["requested_model_version"] = "entirely_forged_version"
            response["model_version"] = "entirely_forged_version"
            official["records"][0]["model_version"] = "entirely_forged_version"
            save(resp_path, response)
            manifest["response_sha256"] = hashlib.sha256(resp_path.read_bytes()).hexdigest()
            save(paths[0], manifest)
            save(paths[2], official)
            report = self.audit(paths)
            self.assertTrue(report["two_source_fields_consistent"])
            self.assertFalse(report["official_api_response_authenticated"])
            self.assertFalse(report["human_authorization_independently_verified"])

    def test_request_id_replayed_from_previous_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, response, official, ledger, _) = self.fixture(d)
            ledger["prior_requests"].append({
                "request_id": response["request_id"],
                "response_id": "unrelated_response_9999",
            })
            save(paths[3], ledger)
            self.assertEqual(self.audit(paths)["status"],
                             "BLOCKED_REPLAYED_REQUEST_OR_RESPONSE_ID")

    def test_response_id_replayed_from_previous_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, response, _, ledger, _) = self.fixture(d)
            ledger["prior_requests"].append({
                "request_id": "different_request_9999",
                "response_id": response["response_id"],
            })
            save(paths[3], ledger)
            self.assertEqual(self.audit(paths)["status"],
                             "BLOCKED_REPLAYED_REQUEST_OR_RESPONSE_ID")

    def test_duplicate_provider_request_id_rejected_even_if_both_claim_same_model(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, _, official, _, _) = self.fixture(d)
            official["records"].append({
                **official["records"][0], "response_id": "other_response_9999"
            })
            save(paths[2], official)
            self.assertEqual(self.audit(paths)["status"],
                             "BLOCKED_DUPLICATE_EXPORT_REQUEST_OR_RESPONSE_ID")

    def test_duplicate_response_id_in_provider_export_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, _, official, _, _) = self.fixture(d)
            official["records"].append({
                **official["records"][0], "request_id": "other_request_9999"
            })
            save(paths[2], official)
            self.assertEqual(self.audit(paths)["status"],
                             "BLOCKED_DUPLICATE_EXPORT_REQUEST_OR_RESPONSE_ID")

    def test_duplicate_prior_ledger_rows_fail_safe(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, _, _, ledger, _) = self.fixture(d)
            ledger["prior_requests"].append(dict(ledger["prior_requests"][0]))
            save(paths[3], ledger)
            self.assertEqual(self.audit(paths)["status"],
                             "BLOCKED_DUPLICATE_LEDGER_RECORD")

    def test_wrong_official_model_version_or_model_or_response(self):
        for field, val in (("model_version", "stale_model_version"),
                           ("model", "different_model_identifier"),
                           ("response_id", "different_response_identifier")):
            with tempfile.TemporaryDirectory() as d:
                paths, (_, _, official, _, _) = self.fixture(d)
                official["records"][0][field] = val
                save(paths[2], official)
                self.assertEqual(self.audit(paths)["status"],
                                 "BLOCKED_PROVIDER_RECORD_MISMATCH")

    def test_official_output_differs_even_with_self_consistent_local_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, _, official, _, _) = self.fixture(d)
            official["records"][0]["output_sha256"] = "0" * 64
            save(paths[2], official)
            self.assertEqual(self.audit(paths)["status"],
                             "BLOCKED_PROVIDER_OUTPUT_SHA_MISMATCH")

    def test_provider_receipt_timestamp_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, _, official, _, _) = self.fixture(d)
            official["records"][0]["created_at_utc"] = "2026-11-13T01:00:03Z"
            save(paths[2], official)
            self.assertEqual(self.audit(paths)["status"],
                             "BLOCKED_PROVIDER_RESPONSE_TIME_MISMATCH")

    def test_provider_export_before_call_end_fails(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, _, official, _, _) = self.fixture(d)
            official["collected_at_utc"] = "2026-11-13T01:00:00Z"
            save(paths[2], official)
            self.assertEqual(self.audit(paths)["status"], "BLOCKED_EXPORT_CHRONOLOGY")

    def test_ledger_snapshot_later_than_call_start_fails(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, _, _, ledger, _) = self.fixture(d)
            ledger["snapshot_at_utc"] = "2026-11-13T02:00:00Z"
            save(paths[3], ledger)
            self.assertEqual(self.audit(paths)["status"],
                             "BLOCKED_LEDGER_SNAPSHOT_AFTER_REQUEST")

    def test_missing_or_reused_ledger_is_not_replay_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            paths, _ = self.fixture(d)
            p = paths.copy()
            p[3] = None
            self.assertEqual(self.audit(p)["status"],
                             "BLOCKED_DUAL_SOURCE_AND_LEDGER_REQUIRED")
            p[3] = p[2]
            self.assertEqual(self.audit(p)["status"],
                             "BLOCKED_SOURCE_PATH_NOT_INDEPENDENT")

    def test_runner_and_official_source_same_directory_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, _, official, _, _) = self.fixture(d)
            cloned = paths[0].parent / "claimed_export.json"
            save(cloned, official)
            paths[2] = cloned
            self.assertEqual(self.audit(paths)["status"],
                             "BLOCKED_EXPORT_NOT_SEPARATELY_STORED")

    def test_source_custody_not_independent_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, _, official, _, _) = self.fixture(d)
            official["retrieved_by_ref"] = official["runner_operator_ref"]
            save(paths[2], official)
            self.assertEqual(self.audit(paths)["status"],
                             "BLOCKED_SOURCE_CUSTODY_CONFLICT")

    def test_extra_api_key_in_external_export_blocks_without_leaking(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, _, official, _, _) = self.fixture(d)
            official["api_key"] = "TEST_SECRET_NEVER_PRINT"
            save(paths[2], official)
            report = self.audit(paths)
            self.assertEqual(report["status"], "BLOCKED_EXTERNAL_EXPORT_SCHEMA")
            self.assertNotIn(official["api_key"], json.dumps(report))

    def test_no_matching_provider_request_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (_, _, official, _, _) = self.fixture(d)
            official["records"][0]["request_id"] = "different_request_997"
            save(paths[2], official)
            self.assertEqual(self.audit(paths)["status"],
                             "BLOCKED_NO_PROVIDER_SOURCE_MATCH")

    def test_local_manifest_invalid_blocks_without_trusting_official_copy(self):
        with tempfile.TemporaryDirectory() as d:
            paths, (manifest, _, _, _, _) = self.fixture(d)
            manifest["prompt_sha256"] = "0" * 64
            save(paths[0], manifest)
            self.assertEqual(self.audit(paths)["status"], "BLOCKED_LOCAL_SOURCE_INVALID")


if __name__ == "__main__":
    unittest.main()
