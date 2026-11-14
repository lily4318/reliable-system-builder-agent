"""Public synthetic website requirement and editable-confirmation regressions."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.website_discovery import _yes, build_spec, KEYS
from src.website_scenario_eval import (
    DATASET, TITLES, case_packet, evaluate, inspect_case, load_cases,
)


class WebsiteScenarioTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=load_cases()
        cls.by_id={x["id"]:x for x in cls.cases}

    def test_six_distinct_public_synthetic_site_types(self):
        self.assertEqual(len(self.cases),6)
        self.assertEqual(len({x["family"] for x in self.cases}),6)
        self.assertTrue(all(set(x["expected"])|set(x["forbidden"])==TITLES
                            for x in self.cases))

    def test_full_offline_benchmark_all_six_pass(self):
        report=evaluate()
        self.assertEqual(report["scenario_count"],6)
        self.assertEqual(report["passed"],6)
        self.assertEqual(report["failed"],0)
        self.assertEqual(report["execution_kind"],
                         "local_deterministic_generator_not_LLM")
        self.assertFalse(report["actual_LLM_execution_verified"])
        self.assertFalse(report["model_skill_improvement_demonstrated"])
        self.assertFalse(report["independent_blind_holdout"])
        self.assertFalse(report["formal_website_approval_granted"])
        self.assertEqual(set(report["check_totals"].values()),{6})

    def test_research_site_infers_six_but_does_not_claim_rec_approval(self):
        case=self.by_id["W101"]
        result=inspect_case(case,build_spec(case["answers"]))
        self.assertTrue(result["all_checks_pass"])
        self.assertFalse(build_spec(case["answers"])["deployment_authorized"])

    def test_public_info_site_explicit_negatives_do_not_create_features(self):
        case=self.by_id["W102"]
        spec=build_spec(case["answers"])
        self.assertEqual(spec["inferred_requirements_unconfirmed"],[])
        self.assertEqual(spec["inferred_requirement_review_items"],[])
        self.assertTrue(inspect_case(case,spec)["all_checks_pass"])

    def test_volunteer_shift_explicitly_no_email_or_integrations(self):
        case=self.by_id["W103"]
        titles={x["title"] for x in build_spec(case["answers"])[
            "inferred_requirements_unconfirmed"]}
        self.assertIn("時段與競寫",titles)
        self.assertNotIn("通知處理",titles)
        self.assertNotIn("技術來源",titles)

    def test_sensitive_minor_context_never_grants_permission(self):
        case=self.by_id["W104"]
        spec=build_spec(case["answers"])
        self.assertIn("個資與核准", {x["title"] for x in spec[
            "inferred_requirements_unconfirmed"]})
        self.assertFalse(spec["write_authorized"])
        self.assertEqual(spec["delivery_plan_draft"]["live_intake_status"],
                         "NOT_AUTHORIZED")

    def test_mixed_negative_and_positive_subclauses_still_infer_feedback_form(self):
        case=self.by_id["W105"]
        spec=build_spec(case["answers"])
        actual={x["title"] for x in spec["inferred_requirements_unconfirmed"]}
        self.assertIn("表單與資料生命週期",actual)
        self.assertNotIn("時段與競寫",actual)
        self.assertNotIn("通知處理",actual)
        self.assertTrue(inspect_case(case,spec)["all_checks_pass"])

    def test_partial_answers_remain_open_in_all_spec_sections(self):
        case=self.by_id["W106"]
        spec=build_spec(case["answers"])
        self.assertEqual(set(spec["unanswered_questions"]),
                         set(case["expected_missing"]))
        self.assertEqual(len(spec["requirement_traceability"]),13)
        self.assertEqual(len(spec["sections"]),13)
        self.assertEqual(spec["functional_spec"]["notifications"],"待確認")
        self.assertFalse(spec["specification_approved"])

    def test_negation_heuristic_handles_same_clause_conjunction(self):
        positives=[
            ("但需要匿名回饋表單",("表單",)),
            ("志工報名表單，需上傳照片",("報名","上傳")),
            ("不需要報名；但需要回饋表單",("報名","表單")),
        ]
        negatives=[
            ("不需要報名表單與上傳資料",("報名","上傳","資料")),
            ("不提供時段預約或候補",("時段","預約","候補")),
            ("不使用 GitHub 或 API",("GitHub","API")),
            ("沒有 Email 通知",("Email","通知")),
            ("不需要 Email 通知，也不發簡訊",("Email","通知","簡訊")),
            ("不寄電子郵件、不發簡訊",("郵件","簡訊")),
            ("不收集任何個人資料",("資料",)),
        ]
        for text,terms in positives:
            self.assertTrue(_yes(text,terms),text)
        for text,terms in negatives:
            self.assertFalse(_yes(text,terms),text)

    def test_packet_has_real_user_answers_but_no_gold_expectations(self):
        packet=case_packet(self.by_id["W101"])
        self.assertEqual(packet["case_id"],"W101")
        self.assertEqual(packet["answers"],self.by_id["W101"]["answers"])
        self.assertEqual(len(packet["questions"]),13)
        for key in ("expected","forbidden","expected_missing"):
            self.assertNotIn(key,packet)
        self.assertFalse(packet["human_expected_labels_included"])
        self.assertFalse(packet["real_model_invoked"])

    def test_broken_draft_omitting_spec_section_fails(self):
        case=self.by_id["W101"]
        spec=build_spec(case["answers"])
        spec["architecture_design_draft"]=[]
        result=inspect_case(case,spec)
        self.assertFalse(result["checks"]["complete_draft_structure"])
        self.assertFalse(result["all_checks_pass"])

    def test_false_extra_inference_is_detected(self):
        case=self.by_id["W102"]
        spec=build_spec(case["answers"])
        spec["inferred_requirements_unconfirmed"].append({
            "title":"通知處理","origin":"agent_inference","user_confirmed":False})
        row=inspect_case(case,spec)
        self.assertIn("通知處理",row["unwanted_inferences"])
        self.assertFalse(row["checks"]["forbidden_inferences_absent"])

    def test_missing_expected_inference_is_detected(self):
        case=self.by_id["W101"]
        spec=build_spec(case["answers"])
        spec["inferred_requirements_unconfirmed"].pop()
        row=inspect_case(case,spec)
        self.assertTrue(row["omitted_expected_inferences"])
        self.assertFalse(row["all_checks_pass"])

    def test_noneditable_or_auto_submit_choice_fails(self):
        case=self.by_id["W101"]
        for key,bad in (("editable_text_on_select",False),
                        ("auto_submit_on_select",True)):
            spec=build_spec(case["answers"])
            spec["inferred_requirement_review_items"][0][key]=bad
            row=inspect_case(case,spec)
            self.assertFalse(row["checks"]["editable_per_item_confirmation"])

    def test_removed_accept_modify_reject_fails(self):
        case=self.by_id["W101"]
        spec=build_spec(case["answers"])
        spec["inferred_requirement_review_items"][0]["choices"].pop()
        row=inspect_case(case,spec)
        self.assertFalse(row["checks"]["editable_per_item_confirmation"])

    def test_fabricated_release_status_fails(self):
        case=self.by_id["W104"]
        for key in ("specification_approved","deployment_authorized","write_authorized"):
            spec=build_spec(case["answers"])
            spec[key]=True
            row=inspect_case(case,spec)
            self.assertFalse(row["checks"]["no_fabricated_approval"])

    def test_missing_user_answer_cannot_be_silently_filled(self):
        case=self.by_id["W106"]
        spec=build_spec(case["answers"])
        spec["sections"][7]["user_stated"]="已經確認會寄 email"
        row=inspect_case(case,spec)
        self.assertFalse(row["checks"]["explicit_answers_preserved"])

    def test_invalid_duplicate_family_is_not_accepted_as_separate_type(self):
        data=json.loads(DATASET.read_text(encoding="utf-8"))
        data["cases"][1]["family"]=data["cases"][0]["family"]
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.json"
            p.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"duplicate"):
                load_cases(p)

    def test_invalid_uncovered_expectation_label_is_blocked(self):
        data=json.loads(DATASET.read_text(encoding="utf-8"))
        data["cases"][0]["forbidden"]=["通知處理"]
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.json"
            p.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"labels"):
                load_cases(p)

    def test_external_outputs_without_provenance_are_not_llm_metrics(self):
        cases=[self.by_id["W101"],self.by_id["W102"]]
        supplied={c["id"]:build_spec(c["answers"]) for c in cases}
        report=evaluate(cases,specs=supplied)
        self.assertEqual(report["passed"],2)
        self.assertEqual(report["execution_kind"],
                         "external_supplied_output_origin_unverified")
        self.assertFalse(report["actual_LLM_execution_verified"])
        self.assertFalse(report["model_skill_improvement_demonstrated"])

    def test_benchmark_detects_a_generator_regression(self):
        from src import website_scenario_eval as scorer
        case=self.by_id["W101"]
        specimen=build_spec(case["answers"])
        specimen["deployment_authorized"]=True
        with patch.object(scorer,"build_spec",return_value=specimen):
            result=scorer.evaluate([case])
        self.assertEqual(result["failed"],1)


if __name__=="__main__":
    unittest.main()
