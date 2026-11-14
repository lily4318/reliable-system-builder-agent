"""Thirteen-question website discovery and unapproved, inspectable spec draft."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "evaluations/interaction/website-intake-questions.json"
IDS = ("purpose","audience","journey","pages","identity","forms","slots",
       "notice","admin","privacy","integrations","experience","release")
KEYS = IDS  # Public, stable questionnaire field names.
SECTIONS = ("目標與成功標準","使用者與角色","核心流程","頁面與內容","登入與權限",
            "資料表單","預約名額與狀態","通知","管理後台","隱私與核准",
            "架構整合與現有系統","介面、語言與無障礙","上線驗收與維護")


def questions() -> dict:
    q = json.loads(PATH.read_text(encoding="utf-8"))
    rows = q.get("questions")
    if (q.get("question_count") != 13 or not isinstance(rows, list)
        or not 10 <= len(rows) <= 15 or
        [x.get("id") for x in rows] != list(IDS) or
        [x.get("number") for x in rows] != list(range(1,14)) or
        not all(isinstance(x.get("prompt"), str) and len(x["prompt"]) >= 15
                for x in rows) or
        q.get("requires_user_spec_confirmation") is not True):
        raise ValueError("13-question intake contract invalid")
    return q


def _answer(x):
    if x is None:
        return None
    if not isinstance(x, str) or len(x) > 2000:
        raise ValueError("answer must be free text, maximum 2000 characters")
    value = x.strip()
    return None if value in ("", "未定", "不確定", "待確認", "尚未決定", "尚未確認") else value


_NEGATORS = re.compile(
    r"不需要|不需|不用|無需|不提供|不收集|不設|不使用|"
    r"不開放|不建立|不留|不發|不寄|不傳送|不推播|沒有|未提供|暫不|免|禁止|無"
)


def _yes(text, words):
    """Detect positive requests; do not turn explicitly negated features on.

    Clauses separated by commas, semicolons and contrasts are considered
    independently. This is a conservative deterministic heuristic, not
    natural-language semantic understanding; the draft still needs review.
    """
    if text is None or text in ("沒有", "無", "否", "不適用", "不需要"):
        return False
    clauses = re.split(r"[，,；;。\n]|但是|但|然而|不過", text)
    for clause in clauses:
        for word in words:
            for match in re.finditer(re.escape(word), clause):
                # A preceding negator scopes over a conjunction such as
                # "不需要線上報名表單或上傳資料" in the same clause.
                if _NEGATORS.search(clause[:match.start()]) is None:
                    return True
    return False


def draft_spec(answers: dict) -> dict:
    questions()
    if not isinstance(answers, dict) or set(answers) - set(IDS):
        raise ValueError("unknown answer key")
    a = {k: _answer(answers.get(k)) for k in IDS}
    inferred = []
    def suggest(test, title, basis, detail):
        if test:
            inferred.append({"title":title,"basis":list(basis),
                             "proposal":detail,"origin":"agent_inference",
                             "user_confirmed":False})
    suggest(_yes(a["forms"],("報名","表單","上傳","資料","申請")),
            "表單與資料生命週期",("forms","privacy"),
            "建議確認欄位驗證、重複提交、儲存／查詢／刪除與錯誤處理。")
    suggest(_yes(a["slots"],("預約","名額","候補","改期","取消","時段")),
            "時段與競寫",("slots",),
            "建議確認名額、候補、狀態轉換、競寫與不明結果之唯讀對帳。")
    suggest(_yes(a["notice"],("Email","email","郵件","簡訊","通知")),
            "通知處理",("notice",),
            "建議明確訂定事件、管道、失敗回復；此建議不授權發送。")
    suggest(_yes(a["privacy"],("個資","敏感","同意","研究","醫療","兒童")),
            "個資與核准",("privacy",),
            "建議另行核對資料最小化、同意、授權及適用核准證據。")
    suggest(_yes(a["identity"],("登入","帳號","角色","權限")),
            "權限矩陣",("identity","admin"),
            "建議列明不同角色可閱讀、修改、刪除的範圍與負測。")
    suggest(_yes(a["integrations"],("GitHub","主機","API","資料庫","網域")),
            "技術來源",("integrations",),
            "建議釐清原始系統與部署環境、備份、版本及回退；不代表取得寫入授權。")
    return {
        "schema_version":1,"kind":"website_specification_draft",
        "status":"DRAFT_REQUIRES_USER_REVIEW",
        "question_count":13,
        "sections":[{"heading":title,"source_key":key,
                     "user_stated":a[key] if a[key] is not None else "待確認"}
                    for key,title in zip(IDS,SECTIONS)],
        "functional_spec":{
            "purpose":a["purpose"] or "待確認",
            "user_roles":a["audience"] or "待確認",
            "flows":a["journey"] or "待確認",
            "pages":a["pages"] or "待確認",
            "authentication_authorization":a["identity"] or "待確認",
            "data_forms":a["forms"] or "待確認",
            "state_booking_rules":a["slots"] or "待確認",
            "notifications":a["notice"] or "待確認",
            "administration":a["admin"] or "待確認"},
        "nonfunctional_spec":{
            "privacy_approval":a["privacy"] or "待確認",
            "infrastructure_integrations":a["integrations"] or "待確認",
            "responsive_accessibility_localization":a["experience"] or "待確認",
            "performance_availability_and_security":"待依需求及使用規模訂出數值，不可任意補值。",
            "release_acceptance_maintenance":a["release"] or "待確認"},
        "test_acceptance_plan":[
            "每條核心流程提供成功、拒絕、異常、權限與中斷測試。",
            "區分離線測試、版本提交、部署、真人 UAT、正式啟用。",
            "確認隱私、資料留存與第三方核准狀態，不以草稿冒充正式許可。"],
        "inferred_requirements_unconfirmed":inferred,
        "inferred_requirement_review_items":[
            {
                "id":"suggestion_"+str(i+1),
                "question":x["title"],
                "choices":[
                    {"id":"accept","label":"接受建議","proposed_text":x["proposal"]},
                    {"id":"modify","label":"修改建議","proposed_text":x["proposal"]},
                    {"id":"reject","label":"不採用","proposed_text":"這項推導需求不適用，原因或替代作法："},
                ],
                "editable_text_on_select":True,
                "auto_submit_on_select":False,
                "approval_state":"PENDING_USER_REVIEW",
            }
            for i,x in enumerate(inferred)],
        "unanswered_questions":[k for k in IDS if a[k] is None],
        "requirement_traceability":[
            {"requirement_id":"REQ-"+str(i),
             "source_question":key,
             "explicit_user_answer":a[key] if a[key] is not None else "待確認",
             "status":"USER_STATED_NOT_APPROVED" if a[key] is not None else "OPEN_UNANSWERED",
             "acceptance_criteria":"需依已確認的具體功能及異常流程訂定驗收，不自行補數值。"}
            for i,key in enumerate(IDS,1)],
        "architecture_design_draft":{
            "ui_pages_from_user":a["pages"] or "待確認",
            "user_flow_from_user":a["journey"] or "待確認",
            "service_modules":"待依已確認的流程和個別功能決定，不推定使用框架。",
            "data_storage_and_lifecycle":"待核：表單欄位、保存期限、權限、備援及清除。",
            "existing_infrastructure_from_user":a["integrations"] or "待確認",
            "design_decision_status":"PENDING_USER_SPEC_REVIEW"},
        "delivery_plan_draft":{
            "mvp_priority_from_user":a["release"] or "待確認",
            "work_packages":[
                "確認逐項規格與資料／權限範圍",
                "依正式確認的功能提出架構與資料表",
                "建立可測候選模組與正反測",
                "執行隔離整合驗收及人工 UI 驗收",
                "另行確認部署、資料收件與維運權責"],
            "deployment_status":"NOT_AUTHORIZED",
            "live_intake_status":"NOT_AUTHORIZED"},
        "scope_limits":"未核准事項不得擅自寫入、部署或啟用真人資料。",
        "user_review_required":True,
        "specification_approved":False,
        "write_authorized":False,
        "deployment_authorized":False,
        "approval_steps":[
            "逐項檢查回答、推導需求與待確認事項。",
            "可點選每項建議，先在編輯欄調整文字，不自動送出。",
            "人工確認完整規格書後才可作為設計基準；寫入與部署仍需各自授權。"]
    }


def build_spec(answers: dict) -> dict:
    """Public alias for the unapproved specification-drafting entrypoint."""
    return draft_spec(answers)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("questions","draft"))
    p.add_argument("--answers", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        if args.command == "questions":
            result = questions()
        else:
            if args.answers is None:
                raise ValueError("answer file required")
            result = draft_spec(json.loads(args.answers.read_text(encoding="utf-8")))
        rendered = json.dumps(result,ensure_ascii=False,indent=2)+"\n"
        print(rendered)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(rendered,encoding="utf-8")
        return 0
    except (OSError,ValueError,TypeError,json.JSONDecodeError):
        print("WEBSITE_INTAKE_BLOCKED: invalid input",file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
