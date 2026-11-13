"""Actual-model evaluation protocol tests. All subprocesses are local test doubles.

No LLM is invoked by CI, no model performance claim is permitted from tests.
"""
import json
import shlex
import sys
import tempfile
import unittest
from pathlib import Path

from src.llm_requirements_eval import (
    CATEGORIES, FALLBACK, FIELDS, FLAGS, PUBLIC_DATASET, ROOT,
    check_holdout, digest, evaluate, load_dataset, parse_prediction,
    runner_payload, score_prediction,
)


class RequirementLLMEvaluationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset, cls.sha = load_dataset()
        cls.case = cls.dataset["cases"][0]

    def test_development_set_is_public_not_blind_holdout(self):
        self.assertEqual(len(self.dataset["cases"]), 20)
        self.assertEqual(self.dataset["split"], "public_dev")
        self.assertFalse(self.dataset["independent_blind_holdout"])
        self.assertIn("pending_independent_review", self.dataset["label_status"])
        self.assertEqual(len(self.sha), 64)
        all_categories = set().union(*(set(x["categories"]) for x in self.dataset["cases"]))
        self.assertEqual(all_categories, CATEGORIES)
        self.assertGreaterEqual(sum(x["critical"] for x in self.dataset["cases"]), 15)

    def test_model_receives_user_text_and_requirement_ids_but_no_gold(self):
        case = self.dataset["cases"][1]
        payload = runner_payload(case)
        self.assertNotIn("expected", payload)
        self.assertNotIn("critical", payload)
        self.assertNotIn("categories", payload)
        self.assertNotIn("id", payload)
        self.assertIn("messages", payload)
        self.assertIn("numbered_requirements", payload)
        self.assertEqual(payload["numbered_requirements"], case["numbered_requirements"])
        self.assertNotIn("independent_blind_holdout", payload)

    def test_score_perfect_output_vs_over_authorized_wrong_target(self):
        c = self.dataset["cases"][1]
        good = score_prediction({**c["expected"],
            "architecture_outline": "此案僅改 Agent 候選測試，不授權外部網站寫入；保留最新需求與人類審查。"}, c)
        self.assertTrue(good["case_exact"])
        self.assertFalse(good["unsafe_scope_action"])
        self.assertEqual(good["requirements_precision"], 1.0)
        self.assertEqual(good["requirements_recall"], 1.0)
        bad = {**c["expected"], "target_scope": "external_project",
               "architecture_outline": "此案須先安全核對目標與來源，尚未批准外部寫入及正式部署。"} 
        self.assertFalse(score_prediction(bad, c)["case_exact"])
        wrong_scope = {**c["expected"], "write_gate": "candidate_pr_only",
                       "target_scope": "external_project",
                       "architecture_outline": "尚無正式授權，必須停止外部寫入並等待權責人核對來源。"} 
        self.assertTrue(score_prediction(wrong_scope, {
            **c, "expected": {**c["expected"], "write_gate": "hold_authorization"},
        })["unsafe_scope_action"])

    def test_superseded_requirements_are_not_automatically_retained(self):
        c = self.dataset["cases"][1]
        self.assertEqual(c["expected"]["preserved_requirement_ids"], ["R2"])
        bad = {**c["expected"], "preserved_requirement_ids": ["R1", "R2"],
               "architecture_outline": "舊需求與新決策衝突，應停止套用舊來源並先核對唯一目標。"} 
        result = score_prediction(bad, c)
        self.assertFalse(result["requirements_exact"])
        self.assertAlmostEqual(result["requirements_precision"], 0.5)

    def test_json_contract_rejects_extra_keys_and_invalid_values(self):
        c = self.case
        gold = {**c["expected"], "architecture_outline":
                "應先由 Architect 核對需求與驗收條件，再確認相依系統；證據不足不進行寫入。"}
        self.assertEqual(parse_prediction(json.dumps(gold), c), gold)
        with self.assertRaisesRegex(ValueError, "exact JSON"):
            parse_prediction(json.dumps({**gold, "approved": True}), c)
        with self.assertRaisesRegex(ValueError, "invalid prediction"):
            parse_prediction(json.dumps({**gold, "next_role": "DEPLOY"}), c)
        with self.assertRaisesRegex(ValueError, "predicted requirements"):
            parse_prediction(json.dumps({**gold,
                "preserved_requirement_ids": ["R99"]}), c)
        with self.assertRaisesRegex(ValueError, "architecture outline"):
            parse_prediction(json.dumps({**gold, "architecture_outline": "太短"}), c)
        with self.assertRaises(ValueError):
            parse_prediction('{"this":"is not a complete model response"}', c)

    def test_duplicate_or_badly_structured_cases_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "development.json"
            x = json.loads(json.dumps(self.dataset))
            x["cases"][1]["id"] = x["cases"][0]["id"]
            p.write_text(json.dumps(x), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicated"):
                load_dataset(p)
            x = json.loads(json.dumps(self.dataset))
            x["cases"][0]["expected"]["write_gate"] = "DEPLOY_NOW"
            p.write_text(json.dumps(x), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid label"):
                load_dataset(p)
            x = json.loads(json.dumps(self.dataset))
            x["cases"][0]["messages"][-1] = None
            p.write_text(json.dumps(x), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "last message"):
                load_dataset(p)
            x = json.loads(json.dumps(self.dataset))
            x["cases"][0]["messages"][-1]["role"] = "assistant"
            p.write_text(json.dumps(x), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "last message"):
                load_dataset(p)

    def test_default_evaluation_requires_user_supplied_real_runner(self):
        with self.assertRaisesRegex(ValueError, "explicit real-model runner"):
            evaluate(PUBLIC_DATASET, "public_dev", "", "")
        with self.assertRaisesRegex(ValueError, "explicit real-model runner"):
            evaluate(PUBLIC_DATASET, "public_dev", "python -c pass", "")

    def _fake_runner(self, directory: str, script: str) -> str:
        p = Path(directory) / "fake_runner.py"
        p.write_text(script, encoding="utf-8")
        return shlex.quote(sys.executable) + " " + shlex.quote(str(p))

    def test_runner_protocol_invokes_subprocess_without_gold_and_sanitizes_report(self):
        with tempfile.TemporaryDirectory() as d:
            c = self._fake_runner(d, '''
import json,sys
x=json.load(sys.stdin)
assert "expected" not in x and "critical" not in x
assert "messages" in x and "numbered_requirements" in x
print(json.dumps({
"task_mode":"clarify","target_scope":"unresolved",
"write_gate":"hold_authorization","requirements_state":"needs_clarification",
"architecture_gate":"not_applicable","next_role":"system-lead",
"risk_flags":[],"preserved_requirement_ids":[],
"architecture_outline":"所有新增需求須先經架構與授權查核，未經人類批准不得寫入外部正式系統。"
}))
''')
            report = evaluate(PUBLIC_DATASET, "public_dev", c, "FAKE_CI_PROTOCOL_ONLY")
            self.assertEqual(report["case_count"], 20)
            self.assertTrue(report["runner_invoked"])
            self.assertFalse(report["independent_blind_holdout_proven"])
            self.assertFalse(report["real_deployment_or_ui_verified"])
            self.assertGreater(report["exact_case_rate"], -0.01)
            self.assertLess(report["exact_case_rate"], 1.0)
            self.assertNotIn("messages", json.dumps(report))
            self.assertNotIn("FAKE_CI_PROTOCOL_ONLY", json.dumps(report["details"]))
            self.assertNotIn("numbered_requirements", json.dumps(report))
            self.assertEqual(report["architecture_outline_valid_rate"], 1.0)
            self.assertFalse(report["architecture_semantic_accuracy_measured"])
            self.assertFalse(report["model_identity_verified"])
            self.assertFalse(report["actual_llm_model_accuracy_measured"])
            self.assertFalse(report["model_version_verified_by_provider"])
            self.assertFalse(report["provider_request_and_response_origin_verified"])
            self.assertTrue(report["provisional_subprocess_metrics_only"])
            self.assertEqual(len(report["prompt_sha256"]), 64)

    def test_runner_failure_timeout_or_bad_json_counted_as_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            for script in (
                'import sys;sys.stderr.write("PRIVATE_DO_NOT_LOG");sys.exit(2)',
                'print("NOT_JSON")',
                'import time;time.sleep(2)',
            ):
                c = self._fake_runner(d, script)
                report = evaluate(PUBLIC_DATASET, "public_dev", c, "FAKE", timeout=1)
                self.assertEqual(report["invalid_model_responses"], 20)
                self.assertEqual(report["exact_cases"], 0)
                self.assertNotIn("PRIVATE_DO_NOT_LOG", json.dumps(report))

    def test_holdout_cannot_launder_public_cases_as_independent(self):
        with self.assertRaisesRegex(ValueError, "dataset split"):
            load_dataset(PUBLIC_DATASET, split="holdout")
        with self.assertRaisesRegex(ValueError, "outside the public repo"):
            check_holdout(PUBLIC_DATASET, None, self.sha, 20)

    def test_sealed_private_holdout_validates_sha_but_does_not_prove_independence(self):
        with tempfile.TemporaryDirectory() as d:
            data = json.loads(json.dumps(self.dataset))
            data["split"] = "holdout"
            data["cases"] = data["cases"][:8]
            p = Path(d) / "sealed.json"
            p.write_text(json.dumps(data), encoding="utf-8")
            raw_sha = digest(p.read_bytes())
            manifest_path = Path(d) / "seal.json"
            m = {
                "schema_version": 1, "dataset_sha256": raw_sha,
                "case_count": 8, "independent_reviewer_attested": True,
                "no_development_leakage_attested": True,
                "reviewer_id": "independent_review_team", "developer_id": "agent_dev_team",
            }
            manifest_path.write_text(json.dumps(m), encoding="utf-8")
            _, from_file = load_dataset(p, split="holdout")
            result = check_holdout(p, manifest_path, from_file, 8)
            self.assertEqual(result["independence"],
                             "reviewer_attested_not_externally_audited")
            m["dataset_sha256"] = "0" * 64
            manifest_path.write_text(json.dumps(m), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "seal/reviewer"):
                check_holdout(p, manifest_path, from_file, 8)

    def test_private_architecture_packet_separates_model_outline_from_gold(self):
        with tempfile.TemporaryDirectory() as d:
            runner = self._fake_runner(d, '''
import json,sys
x=json.load(sys.stdin)
assert "expected" not in x
print(json.dumps({
"task_mode":"clarify","target_scope":"unresolved",
"write_gate":"hold_authorization","requirements_state":"needs_clarification",
"architecture_gate":"not_applicable","next_role":"system-lead",
"risk_flags":[],"preserved_requirement_ids":[],
"architecture_outline":"本案資訊不足，需先確認目標專案、需求驗收條件與授權來源，再請架構人員審視依賴和回退。"
}))
''')
            packet = Path(d) / "new_private_arch_review.json"
            report = evaluate(PUBLIC_DATASET, "public_dev", runner, "FAKE_PROTOCOL",
                              private_review_packet=packet)
            self.assertTrue(report["private_architecture_review_packet_created"])
            self.assertTrue(packet.is_file())
            saved = json.loads(packet.read_text(encoding="utf-8"))
            self.assertEqual(len(saved["cases"]), 20)
            self.assertEqual(len(saved["model_pseudonym"]), 16)
            self.assertNotIn("FAKE_PROTOCOL", packet.read_text(encoding="utf-8"))
            self.assertNotIn("expected", packet.read_text(encoding="utf-8"))
            self.assertNotIn("messages", packet.read_text(encoding="utf-8"))
            self.assertNotIn("architecture_outline", json.dumps(report["details"]))
            self.assertFalse(report["architecture_semantic_accuracy_measured"])
            with self.assertRaisesRegex(ValueError, "new and outside repo"):
                evaluate(PUBLIC_DATASET, "public_dev", runner, "FAKE_PROTOCOL",
                         private_review_packet=packet)
            with self.assertRaisesRegex(ValueError, "new and outside repo"):
                evaluate(PUBLIC_DATASET, "public_dev", runner, "FAKE_PROTOCOL",
                         private_review_packet=ROOT / "output/unsafe_review.json")

    def test_fake_runner_is_not_evidence_of_real_model_or_blind_holdout(self):
        self.assertFalse(self.dataset["independent_blind_holdout"])
        self.assertNotIn("actual_model_accuracy", self.dataset)
        self.assertFalse(score_prediction(None, self.case)["case_exact"])


if __name__ == "__main__":
    unittest.main()
