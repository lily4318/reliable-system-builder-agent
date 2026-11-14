"""Private holdout and two-rater before/after evaluation; offline only.

Public code and synthetic CI tests contain NO sealed holdout cases, provider
credentials, actual Agent invocation, or observed model skill results.
All external metadata are claims, not authenticated provider evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from src.human_confirmation import new_review, select, edit, confirm
from src.website_discovery import KEYS

ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = (
    "explicit_requirements", "reasonable_inferences",
    "architecture_design", "specification_completeness",
    "editable_confirmation",
)
SHA = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
CID = re.compile(r"^H[0-9]{3,5}$")
OID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{11,63}$")
PHASES = ("before", "after")
MAX_BYTES = 262144


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(path: Path) -> dict:
    p = Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_BYTES:
        raise ValueError("missing, symlinked or oversized private input")
    data = json.loads(p.read_bytes())
    if not isinstance(data, dict):
        raise ValueError("JSON object required")
    return data


def _private_path(path: Path) -> Path:
    p = Path(path).absolute()
    if p.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("sealed holdout or reviewer materials cannot be stored in repository")
    return p


def seal_private_cases(private_cases: Path) -> dict:
    """Return digests only. Never publish the input questions or answers."""
    raw = _json(_private_path(private_cases))
    cases = raw.get("cases")
    if (raw.get("schema_version") != 1 or
        raw.get("kind") != "independent_private_website_cases" or
        not isinstance(cases,list) or len(cases)<5 or len(cases)>100):
        raise ValueError("five or more independent private cases required")
    seen = set()
    commitments=[]
    for case in cases:
        if not isinstance(case,dict) or set(case) != {"id","brief","answers"}:
            raise ValueError("invalid private case fields")
        cid=case["id"]
        answers=case["answers"]
        if (not isinstance(cid,str) or not CID.fullmatch(cid) or cid in seen
            or not isinstance(case["brief"],str) or len(case["brief"])<25
            or not isinstance(answers,dict) or set(answers)!=set(KEYS)
            or any(v is not None and (not isinstance(v,str) or len(v)>2000)
                   for v in answers.values())):
            raise ValueError("invalid, duplicated or incomplete private holdout case")
        seen.add(cid)
        commitments.append({"id":cid,"case_sha256":digest(canonical(case))})
    return {
        "schema_version":1,
        "kind":"private_unseen_case_commitments_only",
        "case_count":len(commitments),
        "commitments":sorted(commitments,key=lambda x:x["id"]),
        "case_text_or_answers_embedded":False,
        "case_independence_independently_verified":False,
        "actual_agent_runner_executed":False,
        "sealed_case_prompts_disclosed_to_public_CI":False,
    }


def validate_manifest(manifest: dict) -> dict[str,str]:
    if (not isinstance(manifest,dict) or manifest.get("schema_version")!=1
        or manifest.get("kind")!="private_unseen_case_commitments_only"
        or manifest.get("case_text_or_answers_embedded") is not False
        or manifest.get("case_independence_independently_verified") is not False
        or manifest.get("actual_agent_runner_executed") is not False
        or manifest.get("sealed_case_prompts_disclosed_to_public_CI") is not False):
        raise ValueError("untrusted private case manifest claims")
    items=manifest.get("commitments")
    if not isinstance(items,list) or not 5<=len(items)<=100 or manifest.get("case_count")!=len(items):
        raise ValueError("invalid holdout case count")
    known={}
    for item in items:
        if not isinstance(item,dict) or set(item)!={"id","case_sha256"}:
            raise ValueError("case commitment fields invalid")
        key=item["id"]; h=item["case_sha256"]
        if (not isinstance(key,str) or not CID.fullmatch(key) or key in known
            or not isinstance(h,str) or not SHA.fullmatch(h)):
            raise ValueError("duplicate or invalid private case commitment")
        known[key]=h
    return known


def _safe_output(root: Path, path: str, expected: str) -> dict:
    if not isinstance(path,str) or not isinstance(expected,str) or not SHA.fullmatch(expected):
        raise ValueError("output location or digest invalid")
    part=Path(path)
    if (part.is_absolute() or ".." in part.parts or
        not path.startswith("specifications/") or not path.endswith(".json")):
        raise ValueError("untrusted specification path outside private workspace")
    file=root / part
    if file.is_symlink() or not file.resolve().is_relative_to(root.resolve()):
        raise ValueError("unsafe specification file path")
    data=file.read_bytes()
    if len(data)>MAX_BYTES or digest(data)!=expected:
        raise ValueError("specification digest mismatch or oversized")
    value=json.loads(data)
    if not isinstance(value,dict):
        raise ValueError("specification content invalid")
    return value


def _spec_structure(value: dict) -> bool:
    """Structural only. Human review judges the meaning of actual text."""
    inferred=value.get("inferred_requirements_unconfirmed")
    items=value.get("inferred_requirement_review_items")
    trace=value.get("requirement_traceability")
    if (value.get("status")!="DRAFT_REQUIRES_USER_REVIEW" or
        any(value.get(key) is not False for key in
            ("specification_approved","write_authorized","deployment_authorized"))
        or value.get("user_review_required") is not True or
        not isinstance(inferred,list) or not isinstance(items,list) or
        len(inferred)!=len(items) or not isinstance(trace,list) or
        len(trace)!=13 or
        {x.get("source_question") for x in trace if isinstance(x,dict)}!=set(KEYS)
        or not isinstance(value.get("functional_spec"),dict) or
        len(value["functional_spec"])<9 or
        not isinstance(value.get("nonfunctional_spec"),dict) or
        len(value["nonfunctional_spec"])<5 or
        not isinstance(value.get("architecture_design_draft"),dict) or
        not isinstance(value.get("delivery_plan_draft"),dict) or
        not isinstance(value.get("test_acceptance_plan"),list)):
        return False
    for item in items:
        if not isinstance(item,dict) or (
            item.get("editable_text_on_select") is not True or
            item.get("auto_submit_on_select") is not False or
            item.get("approval_state")!="PENDING_USER_REVIEW"
        ):
            return False
        choices=item.get("choices")
        if not isinstance(choices,list) or [
            c.get("id") for c in choices if isinstance(c,dict)
        ]!=["accept","modify","reject"]:
            return False
        try:
            d=select(new_review(choices),"modify")
            m=edit(d,"允許使用者修改後自行確認，並不自動送出。")
            result=confirm(m,True)
        except (ValueError,KeyError,TypeError):
            return False
        if result.get("sent") is not False or result.get("approval_granted") is not False:
            return False
    return True


def _profiles(bundle: dict) -> dict:
    profiles=bundle.get("profiles")
    if not isinstance(profiles,dict) or set(profiles)!=set(PHASES):
        raise ValueError("both before/after profiles required")
    for key in PHASES:
        row=profiles[key]
        if (not isinstance(row,dict) or set(row)!={
            "agent_sha","prompt_sha","model_id","runner_id","resource_budget"
        } or not all(isinstance(row[k],str) and row[k].strip() for k in row)
            or not COMMIT.fullmatch(row["agent_sha"])
            or not SHA.fullmatch(row["prompt_sha"])):
            raise ValueError("invalid version or runnable model metadata")
    if profiles["before"]["agent_sha"]==profiles["after"]["agent_sha"]:
        raise ValueError("before/after Agent version must differ")
    for key in ("model_id","runner_id","resource_budget"):
        if profiles["before"][key]!=profiles["after"][key]:
            raise ValueError("model, runner and resource budget must match")
    return profiles


def _artifacts(manifest: dict, bundle: dict, root: Path) -> tuple[dict,dict]:
    known=validate_manifest(manifest)
    if (bundle.get("schema_version")!=1 or
        bundle.get("kind")!="externally_supplied_website_outputs_unverified"
        or bundle.get("official_model_execution_verified") is not False):
        raise ValueError("artifact source cannot self-certify model invocation")
    profiles=_profiles(bundle)
    rows=bundle.get("outputs")
    if not isinstance(rows,list) or len(rows)!=len(known)*2:
        raise ValueError("paired outputs missing")
    artifacts={}
    opaque=set()
    for row in rows:
        if not isinstance(row,dict) or set(row)!={
            "id","case_id","phase","case_sha256","path","sha256"
        }:
            raise ValueError("invalid output record fields")
        cid=row["case_id"];phase=row["phase"];key=(cid,phase)
        uid=row["id"]
        if (cid not in known or phase not in PHASES or key in artifacts
            or row["case_sha256"]!=known[cid] or
            not isinstance(uid,str) or not OID.fullmatch(uid)
            or uid in opaque or any(token in uid.lower() for token in
                                   ("before","after","baseline","candidate"))):
            raise ValueError("duplicate, unpaired or unblinded output ID")
        opaque.add(uid)
        spec=_safe_output(root,row["path"],row["sha256"])
        artifacts[key]={"id":uid,"structural_pass":_spec_structure(spec)}
    if len(artifacts)!=len(known)*2:
        raise ValueError("incomplete paired coverage")
    return artifacts,profiles


def _annotations(reviews: dict, outputs: dict) -> tuple[dict,list]:
    if (reviews.get("schema_version")!=1 or
        reviews.get("kind")!="independent_blinded_human_website_reviews"
        or reviews.get("model_or_agent_run_verified") is not False):
        raise ValueError("review cannot self-certify model execution")
    rows=reviews.get("ratings")
    if not isinstance(rows,list) or len(rows)!=len(outputs)*2:
        raise ValueError("two independent reviews required per artifact")
    by_output={v["id"]:{ } for v in outputs.values()}
    for row in rows:
        if not isinstance(row,dict) or set(row)!={"output_id","reviewer_id","scores","evidence"}:
            raise ValueError("invalid human rating shape")
        uid=row["output_id"];rater=row["reviewer_id"]
        if (uid not in by_output or not isinstance(rater,str)
            or not OID.fullmatch(rater) or rater in by_output[uid]
            or not isinstance(row["scores"],dict)
            or set(row["scores"])!=set(DIMENSIONS)
            or not isinstance(row["evidence"],dict)
            or set(row["evidence"])!=set(DIMENSIONS)):
            raise ValueError("unknown, duplicate or incomplete independent review")
        if (any(type(v) is not int or not 0<=v<=4
                for v in row["scores"].values())
            or any(not isinstance(v,str) or len(v.strip())<12 or len(v)>1500
                   for v in row["evidence"].values())):
            raise ValueError("invalid reviewer score or missing supporting reason")
        by_output[uid][rater]=row["scores"]
    if any(len(v)!=2 for v in by_output.values()):
        raise ValueError("every artifact needs two independent raters")
    disputes=[]
    for uid,raters in by_output.items():
        first,second=list(raters.values())
        for dim in DIMENSIONS:
            if abs(first[dim]-second[dim])>=2:
                disputes.append({"output_id":uid,"dimension":dim,
                                 "rater_scores":[first[dim],second[dim]]})
    return by_output,disputes


def compare(manifest: dict, bundle: dict, reviews: dict, root: Path) -> dict:
    """Do not trust provenance claims; model execution and holdout independence stay false."""
    if not isinstance(root,Path):
        root=Path(root)
    root=_private_path(root)
    artifacts,profiles=_artifacts(manifest,bundle,root)
    by_output,disputes=_annotations(reviews,artifacts)
    adjudications=reviews.get("adjudications",[])
    if not isinstance(adjudications,list):
        raise ValueError("adjudications must be a list")
    final={}
    for x in adjudications:
        if (not isinstance(x,dict) or set(x)!={"output_id","dimension","adjudicator_id","score","reason"}):
            raise ValueError("invalid adjudication")
        key=(x["output_id"],x["dimension"])
        if (x["dimension"] not in DIMENSIONS or
            key not in {(z["output_id"],z["dimension"]) for z in disputes}
            or key in final or
            not isinstance(x["adjudicator_id"],str)
            or not OID.fullmatch(x["adjudicator_id"])
            or x["adjudicator_id"] in by_output[x["output_id"]]
            or type(x["score"]) is not int or not 0<=x["score"]<=4
            or not isinstance(x["reason"],str) or len(x["reason"].strip())<12):
            raise ValueError("adjudication incomplete, duplicated or conflicted")
        final[key]=x["score"]
    unresolved=[x for x in disputes if (x["output_id"],x["dimension"]) not in final]
    if unresolved:
        raise ValueError("rater disagreement requires third-person adjudication")
    scores={}
    for (cid,phase),item in artifacts.items():
        uid=item["id"];ratings=list(by_output[uid].values())
        dim_scores={dim:float(final[(uid,dim)]) if (uid,dim) in final
                    else (ratings[0][dim]+ratings[1][dim])/2
                    for dim in DIMENSIONS}
        scores[(cid,phase)]={"dimensions":dim_scores,
                             "mean":sum(dim_scores.values())/len(DIMENSIONS),
                             "structural_pass":item["structural_pass"]}
    cases=sorted({cid for cid,_ in scores})
    rows=[{"case_id":cid,
           "before_score":scores[(cid,"before")]["mean"],
           "after_score":scores[(cid,"after")]["mean"],
           "paired_delta":round(scores[(cid,"after")]["mean"]-
                               scores[(cid,"before")]["mean"],3),
           "before_structure_pass":scores[(cid,"before")]["structural_pass"],
           "after_structure_pass":scores[(cid,"after")]["structural_pass"]}
           for cid in cases]
    deltas={dim:round(sum(scores[(cid,"after")]["dimensions"][dim]-
                              scores[(cid,"before")]["dimensions"][dim]
                              for cid in cases)/len(cases),3)
            for dim in DIMENSIONS}
    paired_mean=round(sum(row["paired_delta"] for row in rows)/len(rows),3)
    return {
        "kind":"offline_website_before_after_human_rubric_comparison",
        "case_count":len(cases),"rating_count":len(by_output)*2,
        "adjudicated_disagreements":len(disputes),
        "phase_versions":{"before":profiles["before"]["agent_sha"],
                          "after":profiles["after"]["agent_sha"]},
        "paired_mean_delta_on_0_to_4_scale":paired_mean,
        "dimension_mean_deltas":deltas,
        "case_summaries":rows,
        "comparison_conditions_matched":True,
        "output_integrity_sha256_checked":True,
        "two_ratings_per_artifact":True,
        "editable_confirmation_static_contract_checked":True,
        "actual_model_or_agent_execution_verified":False,
        "sealed_holdout_independence_verified":False,
        "model_capability_improvement_verified":False,
        "human_semantic_truth_independently_verified_by_software":False,
        "releases_or_live_websites_authorized":False,
        "report_status":"LOCAL_HUMAN_SCORING_ONLY_PROVENANCE_AND_HOLDOUT_PENDING",
    }


def blind_review_packet(manifest: dict, bundle: dict, root: Path) -> dict:
    """Private packet: only opaque output ID and spec; never phase or version."""
    root=_private_path(Path(root))
    artifacts,_=_artifacts(manifest,bundle,root)
    by_id={row["id"]:row for row in bundle["outputs"]}
    return {
        "kind":"private_blinded_website_review_packet",
        "outputs":[
            {"output_id":uid,
             "specification":_safe_output(root,by_id[uid]["path"],
                                          by_id[uid]["sha256"])}
            for uid in sorted(by_id)
        ],
        "before_after_phase_included":False,
        "model_or_runner_metadata_included":False,
        "human_blinding_independently_verified":False,
    }


def protocol_contract() -> dict:
    return {
        "kind":"public_offline_private_holdout_comparison_protocol",
        "dimensions":list(DIMENSIONS),
        "score_range":[0,4],
        "required_independent_raters_per_artifact":2,
        "third_rater_required_if_score_gap_at_least":2,
        "minimum_private_unseen_case_count":5,
        "before_after_same_model_runner_and_budget":True,
        "before_after_agent_sha_must_differ":True,
        "case_text_not_in_public_repository":True,
        "case_independence_independently_verified":False,
        "real_model_or_agent_run_verified":False,
        "automatic_release_allowed":False,
        "synthetic_tests_measure_real_skill":False,
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    actions=parser.add_subparsers(dest="command",required=True)
    actions.add_parser("protocol")
    seal=actions.add_parser("seal")
    seal.add_argument("--cases",type=Path,required=True)
    seal.add_argument("--output",type=Path,required=True)
    blind=actions.add_parser("blind")
    for key in ("manifest","bundle","workspace","output"):
        blind.add_argument("--"+key,type=Path,required=True)
    score=actions.add_parser("compare")
    for key in ("manifest","bundle","reviews","workspace","output"):
        score.add_argument("--"+key,type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.command=="protocol":
            print(json.dumps(protocol_contract(),ensure_ascii=False,indent=2))
            return 0
        if args.command=="seal":
            output=seal_private_cases(args.cases)
        elif args.command=="blind":
            output=blind_review_packet(_json(_private_path(args.manifest)),
                                       _json(_private_path(args.bundle)),
                                       args.workspace)
        else:
            output=compare(_json(_private_path(args.manifest)),
                           _json(_private_path(args.bundle)),
                           _json(_private_path(args.reviews)),
                           args.workspace)
        location=_private_path(args.output)
        if location.exists() or not location.parent.is_dir() or location.is_symlink():
            raise ValueError("no overwrite, symlink or missing private output parent")
        location.write_bytes(canonical(output))
        print(json.dumps({"status":"OFFLINE_CONTRACT_COMPLETE",
                          "output_written":True,
                          "model_run_verified":False,
                          "case_count":output.get("case_count")},ensure_ascii=False))
        return 0
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError):
        print("WEBSITE_HOLDOUT_OFFLINE_BLOCKED: invalid or incomplete private evidence",
              file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
