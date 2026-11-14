"""Public synthetic website discovery benchmark, not real LLM training.

Independent, manually authored expected inference labels are compared against
the current deterministic specification generator. A structural pass is NOT
semantic LLM understanding or independent blind-holdout performance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from src.human_confirmation import new_review, select, edit, confirm
from src.website_discovery import build_spec, questions, KEYS

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluations/interaction/website-scenarios.json"
TITLES = frozenset((
    "表單與資料生命週期", "時段與競寫", "通知處理", "個資與核准",
    "權限矩陣", "技術來源",
))


def load_cases(path: Path = DATASET) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or (
        data.get("schema_version") != 1 or
        data.get("kind") != "public_synthetic_website_discovery_development" or
        data.get("human_authored_expectations") is not True or
        data.get("blind_holdout") is not False or
        data.get("real_agent_model_executed") is not False or
        data.get("requirement_questions") != 13
    ):
        raise ValueError("unsupported or misrepresented website benchmark")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 5:
        raise ValueError("at least five independent synthetic website types required")
    ids, families = set(), set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("case must be object")
        cid = case.get("id")
        fam = case.get("family")
        answers = case.get("answers")
        if (not isinstance(cid,str) or not re.fullmatch(r"W[0-9]{3}",cid)
            or cid in ids or not isinstance(fam,str) or not fam
            or fam in families or not isinstance(answers,dict)
            or set(answers) - set(KEYS) or
            any(not isinstance(a,str) or len(a)>2000 for a in answers.values())):
            raise ValueError("duplicate, unsafe or invalid website case")
        ids.add(cid)
        families.add(fam)
        if any(not isinstance(case.get(k),str) or len(case[k])<12
               for k in ("title","objective")):
            raise ValueError("missing case objective")
        expected = case.get("expected")
        forbidden = case.get("forbidden")
        missing = case.get("expected_missing")
        if (not isinstance(expected,list) or not isinstance(forbidden,list)
            or not isinstance(missing,list)
            or len(expected)!=len(set(expected))
            or len(forbidden)!=len(set(forbidden))
            or set(expected)|set(forbidden)!=TITLES
            or set(expected)&set(forbidden)
            or len(missing)!=len(set(missing))
            or not set(missing).issubset(KEYS)):
            raise ValueError("expected and forbidden inference labels must cover all six")
    return cases


def case_packet(case: dict) -> dict:
    """Visible scenario inputs only; holds out manually annotated labels."""
    q = questions()
    return {
        "case_id": case["id"],
        "family": case["family"],
        "scenario": case["title"],
        "brief": case["objective"],
        "questions": q["questions"],
        "answers": case["answers"],
        "instructions": [
            "完整保留使用者明確需求；缺漏一律列待確認。",
            "根據十三題答案推導必要的合理隱含需求，逐項標待核。",
            "提出完整、可逐項編輯的功能、資料、權限、非功能、架構、測試及維運規格草稿。",
            "未獲具體獨立授權不得寫正式系統、送信、部署或收件。",
        ],
        "human_expected_labels_included": False,
        "self_authored_reference_included": False,
        "real_model_invoked": False,
    }


def _review_contract(items: object, inferred: list) -> bool:
    if not isinstance(items,list) or len(items)!=len(inferred):
        return False
    seen = set()
    for record in items:
        if not isinstance(record,dict):
            return False
        rid = record.get("id")
        if not isinstance(rid,str) or rid in seen:
            return False
        seen.add(rid)
        choices = record.get("choices")
        if (record.get("approval_state")!="PENDING_USER_REVIEW"
            or record.get("editable_text_on_select") is not True
            or record.get("auto_submit_on_select") is not False
            or not isinstance(choices,list)
            or [x.get("id") for x in choices if isinstance(x,dict)]!=[
                "accept", "modify", "reject"
            ]):
            return False
        try:
            state = new_review(choices)
            selected = select(state,"modify")
            if (selected["sent"] or selected["approval_granted"]
                or selected["editable_text"]!=choices[1]["proposed_text"]):
                return False
            changed = edit(selected,"使用者修改內容：暫列待核的需求描述。")
            if changed["sent"] or changed["approval_granted"]:
                return False
            confirmed = confirm(changed,True)
            if (confirmed["sent"] or confirmed["approval_granted"]
                or confirmed["confirmed_text"]!=changed["editable_text"]):
                return False
        except (ValueError,TypeError,KeyError):
            return False
    return True


def inspect_case(case: dict, spec: dict) -> dict:
    inferred = spec.get("inferred_requirements_unconfirmed")
    inferred = inferred if isinstance(inferred,list) else []
    actual = {x.get("title") for x in inferred if isinstance(x,dict)}
    expected = set(case["expected"])
    forbidden = set(case["forbidden"])
    omitted = sorted(expected-actual)
    false_positives = sorted(forbidden&actual)
    sections = spec.get("sections")
    sections = sections if isinstance(sections,list) else []
    trace = spec.get("requirement_traceability")
    trace = trace if isinstance(trace,list) else []
    answers = case["answers"]
    normalized_missing = set(case["expected_missing"])
    open_keys = spec.get("unanswered_questions")
    open_keys = set(open_keys) if isinstance(open_keys,list) else set()
    preserved = (
        len(sections)==13 and
        len({x.get("source_key") for x in sections if isinstance(x,dict)})==13
        and all(
            any(s.get("source_key")==key and
                (s.get("user_stated")==answers.get(key)
                 or (key in normalized_missing and s.get("user_stated")=="待確認"))
                for s in sections if isinstance(s,dict))
            for key in KEYS
        )
    )
    trace_ok = (len(trace)==13 and
        {x.get("source_question") for x in trace if isinstance(x,dict)}==set(KEYS)
        and all(isinstance(x,dict) and x.get("status") in (
            "USER_STATED_NOT_APPROVED","OPEN_UNANSWERED") for x in trace))
    complete = (
        isinstance(spec.get("functional_spec"),dict) and
        len(spec["functional_spec"])>=9 and
        isinstance(spec.get("nonfunctional_spec"),dict) and
        len(spec["nonfunctional_spec"])>=5 and
        isinstance(spec.get("architecture_design_draft"),dict) and
        isinstance(spec.get("delivery_plan_draft"),dict) and
        isinstance(spec.get("test_acceptance_plan"),list)
        and len(spec["test_acceptance_plan"])>=3 and trace_ok
    )
    no_fabricated_approval = (
        spec.get("status")=="DRAFT_REQUIRES_USER_REVIEW"
        and spec.get("user_review_required") is True
        and spec.get("specification_approved") is False
        and spec.get("write_authorized") is False
        and spec.get("deployment_authorized") is False
        and spec.get("delivery_plan_draft",{}).get("deployment_status")=="NOT_AUTHORIZED"
        and spec.get("delivery_plan_draft",{}).get("live_intake_status")=="NOT_AUTHORIZED"
        and all(x.get("origin")=="agent_inference" and
                x.get("user_confirmed") is False
                for x in inferred if isinstance(x,dict))
    )
    checks = {
        "explicit_answers_preserved":preserved,
        "complete_draft_structure":complete,
        "expected_inferences_present":not omitted,
        "forbidden_inferences_absent":not false_positives,
        "missing_answers_open":open_keys==normalized_missing,
        "editable_per_item_confirmation":_review_contract(
            spec.get("inferred_requirement_review_items"), inferred),
        "no_fabricated_approval":no_fabricated_approval,
    }
    return {
        "id":case["id"],"family":case["family"],"checks":checks,
        "omitted_expected_inferences":omitted,
        "unwanted_inferences":false_positives,
        "all_checks_pass":all(checks.values()),
    }


def evaluate(cases: list[dict] | None = None,
             specs: dict[str,dict] | None = None) -> dict:
    rows = load_cases() if cases is None else cases
    is_external = specs is not None
    results = []
    for case in rows:
        actual = (specs.get(case["id"],{}) if specs is not None
                  else build_spec(case["answers"]))
        results.append(inspect_case(case,actual))
    return {
        "evaluation_kind":"public_synthetic_website_specification_contract",
        "execution_kind":("external_supplied_output_origin_unverified"
                          if is_external else
                          "local_deterministic_generator_not_LLM"),
        "scenario_count":len(results),
        "scenario_types":sorted({x["family"] for x in results}),
        "passed":sum(x["all_checks_pass"] for x in results),
        "failed":sum(not x["all_checks_pass"] for x in results),
        "check_totals":{key:sum(x["checks"][key] for x in results)
            for key in results[0]["checks"]} if results else {},
        "cases":results,
        "actual_LLM_execution_verified":False,
        "seven_agent_collaboration_measured":False,
        "independent_blind_holdout":False,
        "model_skill_improvement_demonstrated":False,
        "formal_website_approval_granted":False,
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=("evaluate","packets","validate"))
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        cases=load_cases()
        if args.command=="packets":
            output={"kind":"public_training_tasks_without_expected_labels",
                    "cases":[case_packet(c) for c in cases],
                    "real_model_invoked":False}
        elif args.command=="validate":
            output={"valid":True,"scenario_count":len(cases),
                    "different_types":len({x["family"] for x in cases}),
                    "blind_holdout":False}
        else:
            output=evaluate(cases)
        body=json.dumps(output,ensure_ascii=False,indent=2)+"\n"
        print(body)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(body,encoding="utf-8")
        return 1 if args.command=="evaluate" and output["failed"] else 0
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError):
        print("WEBSITE_SCENARIO_BENCHMARK_BLOCKED: invalid public benchmark",
              file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
