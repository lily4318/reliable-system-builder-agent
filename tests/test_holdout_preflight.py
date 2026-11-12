"""Offline tests for sealed, external, independently annotated holdout contract."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.feedback_eval import load_labels, run, verify_sealed_holdout


def write_json(directory, name, obj):
    path = Path(directory) / name
    payload = json.dumps(obj, sort_keys=True, ensure_ascii=False) + "\n"
    path.write_text(payload, encoding="utf-8")
    return path, hashlib.sha256(payload.encode()).hexdigest()


def row(index, group, split, reviewer):
    return {
        "case_id": "C_" + format(index, "012x"),
        "group_id": "G_" + format(group, "012x"),
        "split": split,
        "outcome": "failure",
        "expected_action": "STOP_AND_RECONCILE",
        "evidence_level": "remote_readback",
        "verified": True,
        "reviewer_id": "REV_" + reviewer * 12,
        "evidence_sha256": "c" * 64,
        "write_authorized": False,
        "resolution_minutes": 12,
        "task_family": "gas",
    }


def prepare(directory):
    dev = {"schema_version": 1, "kind": "reviewed_real",
           "evaluation_id": "private-dev-001",
           "cases": [row(1, 1, "development", "a"), row(2, 2, "validation", "a")]}
    labels = {"schema_version": 1, "kind": "sealed_holdout",
              "evaluation_id": "private-holdout-001",
              "cases": [row(3, 3, "holdout", "b"), row(4, 4, "holdout", "b")]}
    dev_path, dev_sha = write_json(directory, "development.json", dev)
    label_path, label_sha = write_json(directory, "sealed.json", labels)
    manifest = {
        "schema_version": 1, "kind": "holdout_freeze_attestation",
        "evaluation_id": labels["evaluation_id"],
        "labels_sha256": label_sha, "development_sha256": dev_sha,
        "independent_reviewer_id": "REV_" + "d" * 12,
        "candidate_commit_sha": "a" * 40,
        "human_approved": True, "frozen_before_candidate": True,
    }
    manifest_path, _ = write_json(directory, "manifest.json", manifest)
    sample = [{"case_id": x["case_id"], "action": "STOP_AND_RECONCILE",
               "claims_complete": False, "proposes_mutation": False}
              for x in labels["cases"]]
    baseline, _ = write_json(directory, "baseline.json",
                             {"schema_version": 1, "evaluation_id": labels["evaluation_id"],
                              "agent_version": "b" * 40, "predictions": sample})
    candidate, _ = write_json(directory, "candidate.json",
                              {"schema_version": 1, "evaluation_id": labels["evaluation_id"],
                               "agent_version": "a" * 40, "predictions": sample})
    return label_path, dev_path, manifest_path, baseline, candidate


class SealedHoldoutTest(unittest.TestCase):
    def test_manifest_and_separate_groups_pass_offline_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            label, dev, manifest, baseline, candidate = prepare(directory)
            labels, sha = load_labels(label)
            result = verify_sealed_holdout(labels, sha, manifest, dev, "a" * 40)
            self.assertTrue(result["holdout_digest_verified"])
            self.assertTrue(result["development_group_separation_verified"])
            self.assertFalse(result["cryptographic_or_external_blinding_proven"])
            self.assertEqual(
                run(["compare", "--labels", str(label),
                     "--baseline", str(baseline), "--candidate", str(candidate),
                     "--development-labels", str(dev),
                     "--holdout-manifest", str(manifest),
                     "--min-sample", "1"]), 0)

    def test_missing_attestation_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            label, _, _, baseline, candidate = prepare(d)
            self.assertEqual(run(["compare", "--labels", str(label), "--baseline", str(baseline),
                                  "--candidate", str(candidate), "--min-sample", "1"]), 2)

    def test_digest_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            label, dev, manifest, _, _ = prepare(d)
            m = json.loads(manifest.read_text())
            m["labels_sha256"] = "f" * 64
            write_json(d, "manifest.json", m)
            data, sha = load_labels(label)
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                verify_sealed_holdout(data, sha, manifest, dev, "a" * 40)

    def test_group_leak_across_datasets_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            label, dev, manifest, _, _ = prepare(d)
            data = json.loads(dev.read_text())
            data["cases"][0]["group_id"] = "G_" + format(3, "012x")
            _, dev_sha = write_json(d, "development.json", data)
            m = json.loads(manifest.read_text())
            m["development_sha256"] = dev_sha
            write_json(d, "manifest.json", m)
            result, sha = load_labels(label)
            with self.assertRaisesRegex(ValueError, "group leakage"):
                verify_sealed_holdout(result, sha, manifest, dev, "a" * 40)

    def test_independent_attester_must_not_be_label_reviewer(self):
        with tempfile.TemporaryDirectory() as d:
            label, dev, manifest, _, _ = prepare(d)
            m = json.loads(manifest.read_text())
            m["independent_reviewer_id"] = "REV_" + "b" * 12
            write_json(d, "manifest.json", m)
            result, sha = load_labels(label)
            with self.assertRaisesRegex(ValueError, "cannot be task label reviewer"):
                verify_sealed_holdout(result, sha, manifest, dev, "a" * 40)

    def test_commit_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            label, dev, manifest, _, _ = prepare(d)
            result, sha = load_labels(label)
            with self.assertRaisesRegex(ValueError, "candidate commit mismatch"):
                verify_sealed_holdout(result, sha, manifest, dev, "e" * 40)

    def test_missing_verified_evidence_blocks_real_success(self):
        with tempfile.TemporaryDirectory() as d:
            label, _, _, _, _ = prepare(d)
            data = json.loads(label.read_text())
            data["cases"][0]["outcome"] = "success"
            data["cases"][0]["evidence_level"] = "ci_only"
            write_json(d, "sealed.json", data)
            with self.assertRaisesRegex(ValueError, "cannot label real success"):
                load_labels(label)


if __name__ == "__main__":
    unittest.main()
