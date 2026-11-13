"""Offline product-discovery, human handoff and editable confirmation tests."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from src.website_discovery import KEYS, build_spec, questions
from src.human_confirmation import new_review, select, edit, confirm, response_protocol
from src.human_walkthrough import workflows, walkthrough

ROOT = Path(__file__).resolve().parents[1]


class WebsiteIntakeRulesTest(unittest.TestCase):
    def test_website_first_contact_is_13_questions_not_an_unbounded_form(self):
        data=questions()
        self.assertEqual(data["question_count"],13)
        self.assertEqual(len(data["questions"]),13)
        self.assertTrue(10<=len(data["questions"])<=15)
        self.assertEqual(tuple(x["id"] for x in data["questions"]),KEYS)

    def test_unanswered_questions_yield_an_unapproved_full_spec(self):
        s=build_spec({})
        self.assertEqual(len(s["sections"]),13)
        self.assertEqual(len(s["unanswered_questions"]),13)
        self.assertEqual(s["status"],"DRAFT_REQUIRES_USER_REVIEW")
        self.assertFalse(s["specification_approved"])
        self.assertFalse(s["write_authorized"])
        self.assertFalse(s["deployment_authorized"])
        self.assertTrue(s["user_review_required"])
        self.assertEqual(len(s["functional_spec"]),9)
        self.assertEqual(len(s["nonfunctional_spec"]),5)
        self.assertEqual(len(s["test_acceptance_plan"]),3)

    def test_actual_answers_are_preserved_and_different_from_inferences(self):
        spec=build_spec({"purpose":"協會線上報名","audience":"民眾與管理員",
                         "forms":"需要線上報名表單與資料查詢",
                         "slots":"使用者可以預約時段、報名候補或取消",
                         "notice":"需要 Email 通知","privacy":"涉及個資與同意"})
        self.assertEqual(spec["functional_spec"]["purpose"],"協會線上報名")
        self.assertGreaterEqual(len(spec["inferred_requirements_unconfirmed"]),4)
        self.assertTrue(all(x["origin"]=="agent_inference" and
                            x["user_confirmed"] is False
                            for x in spec["inferred_requirements_unconfirmed"]))
        self.assertFalse(spec["specification_approved"])
        self.assertEqual(len(spec["inferred_requirement_review_items"]),
                         len(spec["inferred_requirements_unconfirmed"]))
        self.assertTrue(all(
            [c["id"] for c in item["choices"]] == ["accept","modify","reject"]
            and c["editable_text_on_select"] and not c["auto_submit_on_select"]
            and item["approval_state"]=="PENDING_USER_REVIEW"
            for item in spec["inferred_requirement_review_items"]))

    def test_no_inference_from_explicit_not_applicable_or_negative(self):
        spec=build_spec({"slots":"不需要","notice":"沒有","forms":"不適用"})
        self.assertFalse(any(x["title"] in ("時段與競寫","通知處理","表單與資料生命週期")
                             for x in spec["inferred_requirements_unconfirmed"]))

    def test_freeform_unknown_answers_supported_not_forced_final_approval(self):
        spec=build_spec({"purpose":"待確認","audience":"未定","journey":"不確定"})
        self.assertIn("purpose",spec["unanswered_questions"])
        self.assertIn("audience",spec["unanswered_questions"])
        self.assertFalse(spec["user_review_required"] is False)

    def test_unknown_keys_and_overlong_text_fail(self):
        for value in ({"new_14th_question":"other"},{"purpose":"x"*2001}):
            with self.assertRaises(ValueError):
                build_spec(value)

    def test_no_secret_in_default_questionnaire(self):
        contents=json.dumps(questions(),ensure_ascii=False)
        self.assertNotIn("請提供密碼",contents)
        self.assertNotIn("API Key",contents)


class EditableDecisionTest(unittest.TestCase):
    def setUp(self):
        self.choices=[
            {"id":"A","label":"採用此方向","proposed_text":"使用者先確認網站需求，再進行候選方案設計。"},
            {"id":"B","label":"調整方向","proposed_text":"只保留首版必要功能，額外需求列待確認。"},
        ]

    def test_selection_only_fills_editable_text_without_send(self):
        state=select(new_review(self.choices),"A")
        self.assertEqual(state["status"],"DRAFT_EDITABLE_NOT_SENT")
        self.assertEqual(state["editable_text"],self.choices[0]["proposed_text"])
        self.assertFalse(state["sent"])
        self.assertFalse(state["approval_granted"])
        self.assertFalse(state["explicit_confirmation_received"])

    def test_after_selection_user_can_edit_then_confirm_without_auto_transmit(self):
        state=select(new_review(self.choices),"B")
        edited=edit(state,"我想先處理報名功能，其他的請列為規格草稿。")
        self.assertEqual(edited["editable_text"],"我想先處理報名功能，其他的請列為規格草稿。")
        self.assertFalse(edited["sent"])
        with self.assertRaisesRegex(ValueError,"explicit"):
            confirm(edited,False)
        confirmed=confirm(edited,True)
        self.assertEqual(confirmed["confirmed_text"],edited["editable_text"])
        self.assertFalse(confirmed["sent"])
        self.assertFalse(confirmed["approval_granted"])

    def test_cannot_confirm_before_choice_or_blank_draft(self):
        with self.assertRaises(ValueError):
            confirm(new_review(self.choices),True)
        with self.assertRaises(ValueError):
            confirm(edit(select(new_review(self.choices),"A"),""),True)

    def test_changing_choice_clears_previous_confirmation(self):
        state=confirm(select(new_review(self.choices),"A"),True)
        state=select(state,"B")
        self.assertFalse(state["explicit_confirmation_received"])
        self.assertEqual(state["editable_text"],self.choices[1]["proposed_text"])

    def test_duplicate_choice_or_unknown_selection_rejected(self):
        with self.assertRaises(ValueError):
            new_review([self.choices[0],self.choices[0]])
        with self.assertRaises(ValueError):
            select(new_review(self.choices),"missing")

    def test_protocol_requires_editing_and_separate_confirmation(self):
        protocol=response_protocol()
        self.assertEqual(protocol["control_order"],
                         ["select_choice","edit_text","review","explicit_confirm"])
        self.assertFalse(protocol["on_select_auto_send"])
        self.assertFalse(protocol["on_select_auto_approve"])
        self.assertTrue(protocol["editable_after_selection"])

    def test_html_example_has_working_select_edit_confirm_but_no_network_send(self):
        html=(ROOT/"examples/editable-decision-review.html").read_text(encoding="utf-8")
        self.assertIn('type="radio"',html)
        self.assertIn('<textarea',html)
        self.assertIn('id="confirm"',html)
        self.assertIn('addEventListener("change"',html)
        self.assertIn('addEventListener("click"',html)
        self.assertIn('input.value=el.dataset.draft',html)
        self.assertNotIn("fetch(",html)
        self.assertNotIn("XMLHttpRequest",html)
        self.assertNotIn("form.submit(",html)


class ManualHandoffTest(unittest.TestCase):
    def test_step_by_step_workflows_are_actionable(self):
        data=workflows()
        self.assertEqual(len(data["workflows"]),3)
        for recipe in data["workflows"]:
            self.assertGreaterEqual(len(recipe["steps"]),5)
            self.assertEqual([v["number"] for v in recipe["steps"]],
                             list(range(1,len(recipe["steps"])+1)))
            self.assertTrue(all(v.get("action") and v.get("verification")
                                for v in recipe["steps"]))

    def test_user_secrets_must_never_be_shared_as_completion_proof(self):
        for task in ("github_signup","github_repository","github_actions_secret"):
            guide=walkthrough(task)
            self.assertTrue(guide["human_performs_actions"])
            self.assertTrue(guide["never_share_password_token_or_recovery_code"])
            self.assertTrue(guide["stop_and_report_if_ui_or_permission_differs"])

    def test_unknown_manual_workflow_not_misrepresented_as_completed(self):
        with self.assertRaisesRegex(ValueError,"unknown"):
            walkthrough("setup_magic_cloud_invisibly")

    def test_essential_documents_contain_three_rules(self):
        docs=(ROOT/"AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("10–15",docs)
        self.assertIn("逐步",docs)
        self.assertIn("可編輯",docs)
        self.assertIn("不自動送出",docs)


if __name__ == "__main__":
    unittest.main()
