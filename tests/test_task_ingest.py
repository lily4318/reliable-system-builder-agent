"""Offline synthetic tests: source never mutated, privacy & authorization fail closed."""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.task_ingest import (
    REPO_ROOT, ingest, load_authorization, main, safe_summary,
    verify_evidence_bytes, write_queue_private,
)

FIX = REPO_ROOT / "evaluations/ingestion"
SOURCE = FIX / "synthetic-events.json"
AUTH = FIX / "synthetic-authorization.json"
NOW = datetime(2026, 11, 12, tzinfo=timezone.utc)


def dump(root, name, obj):
    path = Path(root) / name
    path.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return path


class TaskIngestTest(unittest.TestCase):
    def setUp(self):
        self.events = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.auth = json.loads(AUTH.read_text(encoding="utf-8"))

    def test_synthetic_fixture_read_only_and_pending(self):
        before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        out = ingest(SOURCE, AUTH, "synthetic", NOW)
        self.assertEqual(out["source_sha256"], before)
        self.assertEqual(len(out["records"]), 2)
        self.assertEqual(out["redacted_free_text_count"], 2)
        self.assertFalse(out["source_was_modified"])
        self.assertFalse(out["formal_review_completed"])
        self.assertFalse(out["authorization_externally_verified"])
        self.assertTrue(all(x["status"] == "PENDING_HUMAN_REVIEW" for x in out["records"]))
        self.assertTrue(all(x["outcome"] == "unknown" and not x["verified"] for x in out["records"]))
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), before)

    def test_human_queue_contains_structured_timeline_only(self):
        queue = ingest(SOURCE, AUTH, "synthetic", NOW)
        first = queue["records"][0]
        self.assertEqual(len(first["events"]), 2)
        self.assertEqual([x["operation"] for x in first["events"]],
                         ["CREATE_VERSION", "GET_INVENTORY"])
        self.assertEqual([x["result"] for x in first["events"]],
                         ["partial", "unknown"])
        self.assertEqual(first["expected_action"], None)
        self.assertFalse(first["human_review_required"] is False)
        self.assertNotIn("note", json.dumps(first))

    def test_summary_safe_and_source_digest(self):
        q = ingest(SOURCE, AUTH, "synthetic", NOW)
        summary = safe_summary(q)
        self.assertEqual(summary["events"], 3)
        self.assertEqual(summary["pending_cases"], 2)
        self.assertEqual(summary["approved_cases"], 0)
        self.assertFalse(summary["remote_action_performed"])

    def test_privacy_drops_entire_free_text_and_secret(self):
        self.events["events"][0]["note"] = "internal endpoint and email user@example.com token ghp_" + "a" * 35
        with tempfile.TemporaryDirectory() as td:
            source = dump(td, "source.json", self.events)
            auth = dump(td, "auth.json", self.auth)
            data = ingest(source, auth, "synthetic", NOW)
            result = json.dumps(data, ensure_ascii=False)
            self.assertNotIn("user@example.com", result)
            self.assertNotIn("internal endpoint", result)
            self.assertNotIn("ghp_", result)
            self.assertNotIn("note", result)

    def test_unknown_raw_log_field_rejected(self):
        self.events["events"][0]["raw_log"] = "PRIVATE RAW LOG"
        with tempfile.TemporaryDirectory() as td:
            source = dump(td, "src.json", self.events)
            auth = dump(td, "auth.json", self.auth)
            with self.assertRaisesRegex(ValueError, "raw content not accepted"):
                ingest(source, auth, "synthetic", NOW)

    def test_wrong_scope_rejected_before_source_read(self):
        with self.assertRaisesRegex(ValueError, "real authorization must remain outside"):
            ingest(SOURCE, AUTH, "reviewed_real", NOW)

    def test_unapproved_manifest_rejected(self):
        self.auth["approved"] = False
        with tempfile.TemporaryDirectory() as td:
            auth = dump(td, "authorization.json", self.auth)
            with self.assertRaisesRegex(ValueError, "explicit human"):
                ingest(SOURCE, auth, "synthetic", NOW)

    def test_expired_authorization_rejected(self):
        self.auth["expires_at_utc"] = "2024-01-01T00:00:00Z"
        with tempfile.TemporaryDirectory() as td:
            auth = dump(td, "authorization.json", self.auth)
            with self.assertRaisesRegex(ValueError, "expired"):
                ingest(SOURCE, auth, "synthetic", NOW)

    def test_authorized_source_sha_tampering_rejected(self):
        self.auth["source_sha256"] = "a" * 64
        with tempfile.TemporaryDirectory() as td:
            auth = dump(td, "authorization.json", self.auth)
            with self.assertRaisesRegex(ValueError, "source digest differs"):
                ingest(SOURCE, auth, "synthetic", NOW)

    def test_unauthorized_project_rejected(self):
        self.events["events"][0]["project_id"] = "P_" + "f" * 12
        with tempfile.TemporaryDirectory() as td:
            source = dump(td, "source.json", self.events)
            auth = dump(td, "auth.json", self.auth)
            with self.assertRaisesRegex(ValueError, "project not authorized"):
                ingest(source, auth, "synthetic", NOW)

    def test_unauthorized_operation_rejected(self):
        self.events["events"][0]["operation"] = "CREATE_DEPLOYMENT"
        with tempfile.TemporaryDirectory() as td:
            source = dump(td, "source.json", self.events)
            auth = dump(td, "auth.json", self.auth)
            with self.assertRaisesRegex(ValueError, "operation not authorized"):
                ingest(source, auth, "synthetic", NOW)

    def test_duplicate_events_rejected(self):
        self.events["events"].append(copy.deepcopy(self.events["events"][0]))
        with tempfile.TemporaryDirectory() as td:
            source = dump(td, "source.json", self.events)
            auth = dump(td, "auth.json", self.auth)
            with self.assertRaisesRegex(ValueError, "duplicate event"):
                ingest(source, auth, "synthetic", NOW)

    def test_inconsistent_case_identity_rejected(self):
        self.events["events"][1]["group_id"] = "G_" + "f" * 12
        with tempfile.TemporaryDirectory() as td:
            source = dump(td, "source.json", self.events)
            auth = dump(td, "auth.json", self.auth)
            with self.assertRaisesRegex(ValueError, "case identity changed"):
                ingest(source, auth, "synthetic", NOW)

    def test_invalid_http_code_bool_rejected(self):
        self.events["events"][0]["http_status"] = True
        with tempfile.TemporaryDirectory() as td:
            source = dump(td, "source.json", self.events)
            auth = dump(td, "auth.json", self.auth)
            with self.assertRaisesRegex(ValueError, "invalid HTTP status"):
                ingest(source, auth, "synthetic", NOW)

    def test_missing_digest_for_real_rejected(self):
        self.events["scope"] = "reviewed_real"
        self.events["events"][0]["evidence_sha256"] = None
        with tempfile.TemporaryDirectory() as td:
            source = dump(td, "source.json", self.events)
            self.auth.update({
                "scope": "reviewed_real",
                "approved_by": "REV_" + "e" * 12,
                "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            })
            auth = dump(td, "auth.json", self.auth)
            with self.assertRaisesRegex(ValueError, "evidence digest"):
                ingest(source, auth, "reviewed_real", NOW)

    def test_real_private_sanitized_offline_only(self):
        self.events["scope"] = "reviewed_real"
        with tempfile.TemporaryDirectory() as td:
            source = dump(td, "source.json", self.events)
            self.auth.update({
                "scope": "reviewed_real",
                "approved_by": "REV_" + "e" * 12,
                "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            })
            auth = dump(td, "auth.json", self.auth)
            queue = ingest(source, auth, "reviewed_real", NOW)
            self.assertFalse(queue["formal_review_completed"])
            self.assertFalse(queue["authorization_externally_verified"])
            output = Path(td) / "review_queue.json"
            write_queue_private(queue, output)
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertTrue(output.is_file())
            self.assertNotIn("note", output.read_text())
            self.assertTrue(all(x["human_review_required"] for x in queue["records"]))

    def test_output_does_not_overwrite_existing(self):
        data = ingest(SOURCE, AUTH, "synthetic", NOW)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "queue.json"
            write_queue_private(data, path)
            before = path.read_bytes()
            with self.assertRaisesRegex(ValueError, "refuse to replace"):
                write_queue_private(data, path)
            self.assertEqual(before, path.read_bytes())

    def test_output_does_not_allow_source_path(self):
        data = ingest(SOURCE, AUTH, "synthetic", NOW)
        with self.assertRaisesRegex(ValueError, "refuse to replace"):
            write_queue_private(data, SOURCE)

    def test_deterministic_queue_for_same_input(self):
        a = ingest(SOURCE, AUTH, "synthetic", NOW)
        b = ingest(SOURCE, AUTH, "synthetic", NOW)
        self.assertEqual(
            json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True)
        )

    def test_local_evidence_sha_matches_without_export(self):
        with tempfile.TemporaryDirectory() as td:
            content = b"SYNTHETIC OFFLINE EVIDENCE ONLY"
            f = Path(td) / "evidence.txt"
            f.write_bytes(content)
            result = verify_evidence_bytes(
                f, hashlib.sha256(content).hexdigest(), Path(td)
            )
            self.assertTrue(result["matches_expected_sha256"])
            self.assertFalse(result["raw_evidence_exported"])
            self.assertFalse(result["truth_of_source_verified"])
            self.assertEqual(result["bytes_read"], len(content))

    def test_evidence_mismatch_is_not_trusted(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "evidence.txt"
            f.write_bytes(b"SYNTHETIC")
            result = verify_evidence_bytes(f, "f" * 64, Path(td))
            self.assertFalse(result["matches_expected_sha256"])

    def test_evidence_outside_root_blocked(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent) / "approved"
            root.mkdir()
            outside = Path(parent) / "outside.txt"
            outside.write_text("synthetic")
            with self.assertRaisesRegex(ValueError, "outside approved"):
                verify_evidence_bytes(outside, "f" * 64, root)

    def test_evidence_symlink_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            actual = Path(td) / "actual.txt"
            actual.write_text("test")
            linked = Path(td) / "link.txt"
            linked.symlink_to(actual)
            with self.assertRaisesRegex(ValueError, "non-symlink"):
                verify_evidence_bytes(linked, "f" * 64, Path(td))

    def test_no_source_write_on_preview(self):
        with tempfile.TemporaryDirectory() as td:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main([
                    "preview", "--scope", "synthetic",
                    "--input", str(SOURCE),
                    "--authorization", str(AUTH),
                ])
            self.assertEqual(code, 0)
            r = json.loads(out.getvalue())
            self.assertEqual(r["pending_cases"], 2)
            self.assertFalse(r["queue_written"])
            self.assertEqual(list(Path(td).iterdir()), [])

    def test_prepare_only_writes_explicit_queue(self):
        with tempfile.TemporaryDirectory() as td:
            q = Path(td) / "newqueue.json"
            with contextlib.redirect_stdout(io.StringIO()):
                code = main([
                    "prepare", "--scope", "synthetic",
                    "--input", str(SOURCE),
                    "--authorization", str(AUTH),
                    "--output", str(q),
                ])
            self.assertEqual(code, 0)
            self.assertTrue(q.exists())
            self.assertTrue(all(not c["verified"] for c in json.loads(q.read_text())["records"]))

    def test_no_network_or_remote_mutation_client(self):
        source = (REPO_ROOT / "src/task_ingest.py").read_text(encoding="utf-8")
        for banned in ("import requests", "urllib.request", "googleapiclient",
                       "mcp__GitHub__", "createDeployment", "subprocess.run",
                       "script.googleapis.com"):
            self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main()
