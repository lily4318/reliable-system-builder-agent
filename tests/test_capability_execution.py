"""Synthetic offline Agent-execution protocol tests: never run a model or candidate code."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from src.capability_execution import prepare_all, import_results
from src.capability_workbench import REFERENCE, ROOT, load_submissions, load_tasks


class OfflineAgentExecutionTest(unittest.TestCase):
    def fixture(self, directory, kind="synthetic_protocol_test", n=5):
        root = Path(directory)
        packets = root / "task-packets"
        prep = prepare_all(packets)
        manifest = json.loads((packets / "manifest.json").read_text(encoding="utf-8"))
        refs = load_submissions(REFERENCE)
        tasks = load_tasks()
        rows = []
        for i, (item, task) in enumerate(zip(refs, tasks)):
            sub = copy.deepcopy(item)
            sub["requirements"][0]["acceptance"] += "此處僅是合成協定負測／正測，並非真正模型產生的規格。"
            # Deliberately functionally wrong; structural full score is not correctness.
            implementation = (
                f"def {task['implementation_function']}(*args, **kwargs):\n"
                "    return 'SYNTHETIC_INCORRECT_RESULT'\n"
            )
            rows.append({
                "task_id": task["id"], "status": "completed",
                "packet_sha256": manifest["packet_sha256"][task["id"]],
                "run_id": f"SYNTHETIC_PROTOCOL_RUN_{i+1:03d}",
                "model_id": "SYNTHETIC_MODEL_NOT_INVOKED",
                "submission": sub, "implementation_source": implementation,
            })
        bundle = {
            "schema_version": 1, "kind": kind,
            "attempt_label": "SYNTHETIC_ATTEMPT_0001", "results": rows[:n],
        }
        p = root / "bundle.json"
        self.write(p, bundle)
        return packets, p, bundle, prep

    @staticmethod
    def write(path, value):
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def test_all_five_task_packets_are_prepared_without_gold_or_agent_run(self):
        with tempfile.TemporaryDirectory() as d:
            result = prepare_all(Path(d) / "packets")
            self.assertEqual(result["status"], "PREPARED_NO_AGENT_INVOKED")
            self.assertEqual(result["task_count"], 5)
            self.assertEqual(result["actual_agent_runs_verified"], 0)
            self.assertEqual(result["task_ids"], ["B001","B002","B003","B004","B005"])
            for tid in result["task_ids"]:
                text = (Path(d) / "packets" / (tid + ".json")).read_text()
                self.assertNotIn("required_components", text)
                self.assertNotIn("self_authored_reference", text)
                self.assertIn("submission_shape", text)

    def test_offline_synthetic_full_roundtrip_scores_only_structure(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, _, _ = self.fixture(d)
            out = Path(d) / "reviewed"
            result = import_results(packets, bundle, out)
            self.assertEqual(result["task_count_completed"], 5)
            self.assertEqual(result["task_count_blocked"], 0)
            self.assertEqual(result["structural_score"], 100.0)
            self.assertEqual(result["status"], "SYNTHETIC_PROTOCOL_TEST_ONLY")
            for key in ("actual_agent_model_execution_verified",
                        "actual_seven_agent_handoffs_verified",
                        "code_executed_or_imported",
                        "program_semantics_verified",
                        "real_agent_skill_gain_demonstrated",
                        "self_authored_reference_used_as_submission"):
                self.assertFalse(result[key])
            self.assertEqual(len(list((out / "implementations").glob("B*.py"))),5)
            self.assertTrue((out / "submissions.json").is_file())
            self.assertTrue((out / "report.json").is_file())
            self.assertIn("SYNTHETIC_INCORRECT_RESULT",
                          (out / "implementations/B001.py").read_text())

    def test_external_bundle_cannot_claim_real_model_accuracy(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(
                d, kind="externally_supplied_agent_outputs_unverified")
            result = import_results(packets, bundle, Path(d) / "review")
            self.assertEqual(result["status"],
                             "EXTERNAL_AGENT_OUTPUT_UNVERIFIED_REVIEW_REQUIRED")
            self.assertFalse(result["actual_agent_model_execution_verified"])
            self.assertFalse(result["program_semantics_verified"])
            self.assertTrue(result["human_review_required"])

    def test_partial_four_with_one_explicitly_blocked_is_not_full_run(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(d)
            last = data["results"][-1]
            data["results"][-1] = {
                "task_id": last["task_id"], "status": "blocked",
                "packet_sha256": last["packet_sha256"],
                "reason_code": "NO_AUTHORIZED_RUNNER",
            }
            self.write(bundle, data)
            result = import_results(packets, bundle, Path(d) / "review")
            self.assertEqual(result["task_count_completed"], 4)
            self.assertEqual(result["task_count_blocked"], 1)
            self.assertEqual(len(result["cases"]), 5)
            self.assertLess(result["structural_score"], 100)

    def test_all_blocked_and_no_scores_do_not_fake_performance(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(d, n=1)
            first = data["results"][0]
            data["results"][0] = {
                "task_id": first["task_id"], "status":"blocked",
                "packet_sha256":first["packet_sha256"],
                "reason_code":"NO_AUTHORIZED_RUNNER",
            }
            self.write(bundle, data)
            report = import_results(packets, bundle, Path(d) / "review")
            self.assertEqual(report["task_count_completed"],0)
            self.assertIsNone(report["structural_score"])
            self.assertEqual(report["task_count_blocked"],5)

    def test_duplicate_task_id_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(d)
            data["results"][1]["task_id"] = data["results"][0]["task_id"]
            self.write(bundle, data)
            with self.assertRaisesRegex(ValueError, "duplicated task"):
                import_results(packets, bundle, Path(d) / "review")
            self.assertFalse((Path(d) / "review").exists())

    def test_duplicate_run_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(d)
            data["results"][1]["run_id"] = data["results"][0]["run_id"]
            self.write(bundle, data)
            with self.assertRaisesRegex(ValueError, "duplicate execution"):
                import_results(packets, bundle, Path(d) / "review")

    def test_packet_tamper_detected(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, _, _ = self.fixture(d)
            with (packets / "B001.json").open("ab") as f:
                f.write(b" ")
            with self.assertRaisesRegex(ValueError, "altered"):
                import_results(packets, bundle, Path(d) / "review")

    def test_bundle_wrong_packet_digest_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(d)
            data["results"][0]["packet_sha256"] = "0" * 64
            self.write(bundle, data)
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                import_results(packets, bundle, Path(d) / "review")

    def test_exact_public_self_authored_reference_copy_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(d)
            data["results"][0]["submission"] = load_submissions(REFERENCE)[0]
            self.write(bundle, data)
            with self.assertRaisesRegex(ValueError, "copied self-authored"):
                import_results(packets, bundle, Path(d) / "review")

    def test_false_agent_execution_claim_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(d)
            data["results"][0]["submission"]["claims"]["real_agent_invoked"] = True
            self.write(bundle, data)
            with self.assertRaisesRegex(ValueError, "claims must be false"):
                import_results(packets, bundle, Path(d) / "review")

    def test_untrusted_implementation_path_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(d)
            data["results"][0]["submission"]["implementation"]["path"] = "../../escape.py"
            self.write(bundle, data)
            report = import_results(packets, bundle, Path(d) / "review")
            self.assertEqual(report["task_count_completed"],5)
            self.assertFalse((Path(d) / "escape.py").exists())
            self.assertTrue((Path(d) / "review/implementations/B001.py").exists())

    def test_untrusted_code_is_never_imported_or_executed(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(d)
            signal = Path(d) / "SHOULD_NOT_EXIST"
            data["results"][0]["implementation_source"] = (
                "from pathlib import Path\n"
                f"Path({str(signal)!r}).write_text('BAD')\n"
                "def enrollment_status(*args):\n    return 'FAKE'\n"
            )
            self.write(bundle, data)
            report = import_results(packets, bundle, Path(d) / "review")
            self.assertFalse(signal.exists())
            self.assertFalse(report["program_semantics_verified"])

    def test_injected_secret_or_response_fields_fail_strict_contract(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(d)
            data["results"][0]["api_key"] = "DO_NOT_LEAK_SECRET"
            self.write(bundle, data)
            with self.assertRaisesRegex(ValueError, "exact public contract"):
                import_results(packets, bundle, Path(d) / "review")

    def test_missing_model_id_or_execution_id_fails(self):
        for field in ("model_id", "run_id"):
            with tempfile.TemporaryDirectory() as d:
                packets, bundle, data, _ = self.fixture(d)
                data["results"][0][field] = ""
                self.write(bundle, data)
                with self.assertRaisesRegex(ValueError, "identifier"):
                    import_results(packets, bundle, Path(d) / "review")

    def test_missing_or_invalid_code_does_not_block_static_scoring(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(d)
            data["results"][0]["implementation_source"] = (
                "def enrollment_status(:\n  return 4\n"
            )
            self.write(bundle, data)
            report = import_results(packets, bundle, Path(d) / "review")
            self.assertFalse(report["cases"][0]["checks"]["implementation_static"])
            self.assertFalse(report["code_executed_or_imported"])

    def test_oversized_or_empty_source_rejected(self):
        for source in ("", "x" * 65537):
            with tempfile.TemporaryDirectory() as d:
                packets, bundle, data, _ = self.fixture(d)
                data["results"][0]["implementation_source"] = source
                self.write(bundle, data)
                with self.assertRaisesRegex(ValueError, "source missing"):
                    import_results(packets, bundle, Path(d) / "review")

    def test_reusing_output_path_never_overwrites_existing_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, _, _ = self.fixture(d)
            target = Path(d) / "review"
            target.mkdir()
            (target / "keep.txt").write_text("NO_REPLACE")
            with self.assertRaisesRegex(ValueError, "output directory"):
                import_results(packets, bundle, target)
            self.assertEqual((target / "keep.txt").read_text(),"NO_REPLACE")

    def test_unknown_task_or_unsupported_kind_rejected(self):
        for mutation in ("unknown_id", "wrong_kind"):
            with tempfile.TemporaryDirectory() as d:
                packets, bundle, data, _ = self.fixture(d)
                if mutation == "unknown_id":
                    data["results"][0]["task_id"] = "B999"
                else:
                    data["kind"] = "official_provider_verified"
                self.write(bundle, data)
                with self.assertRaises(ValueError):
                    import_results(packets, bundle, Path(d) / "review")

    def test_blocked_result_must_have_reason_and_no_model_output(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, data, _ = self.fixture(d)
            data["results"][0]["status"]="blocked"
            self.write(bundle, data)
            with self.assertRaisesRegex(ValueError, "blocked task"):
                import_results(packets,bundle,Path(d) / "review")

    def test_prepare_cannot_replace_existing_packets(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "packets"
            prepare_all(folder)
            with self.assertRaisesRegex(ValueError, "output directory"):
                prepare_all(folder)

    def test_bundle_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            packets, bundle, _, _ = self.fixture(d)
            proxy = Path(d) / "bundle-link.json"
            proxy.symlink_to(bundle)
            with self.assertRaisesRegex(ValueError, "symlinked"):
                import_results(packets, proxy, Path(d) / "review")


if __name__ == "__main__":
    unittest.main()
