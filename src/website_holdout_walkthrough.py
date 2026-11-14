"""Operator-facing PRIVATE website evaluation helpers. No runner or network.

Rehearsal uses only public development cases, never a real holdout. Review
packets retain source requirements so humans can actually assess the specs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import sys
import tempfile
from uuid import uuid4

from src.website_discovery import KEYS, build_spec
from src.website_scenario_eval import load_cases
from src.website_holdout_compare import (
    DIMENSIONS, OID, ROOT, canonical, digest, seal_private_cases,
    validate_manifest, blind_review_packet, compare, _json, _private_path,
)


def _write(path: Path, obj: dict) -> None:
    path = _private_path(path)
    with path.open("xb") as f:
        f.write(canonical(obj))


def prepare_review(cases_path: Path, manifest: dict, bundle: dict,
                   workspace: Path) -> dict:
    """Keep original answers and candidate spec together; hide phase mapping."""
    resealed = seal_private_cases(cases_path)
    if validate_manifest(resealed) != validate_manifest(manifest):
        raise ValueError("source cases mismatch sealed manifest")
    cases = {row["id"]: row for row in _json(_private_path(cases_path))["cases"]}
    blind = blind_review_packet(manifest, bundle, workspace)
    by_id = {row["id"]: row["case_id"] for row in bundle["outputs"]}
    rows = [
        {"output_id": row["output_id"],
         "brief": cases[by_id[row["output_id"]]]["brief"],
         "answers": cases[by_id[row["output_id"]]]["answers"],
         "specification": row["specification"]}
        for row in blind["outputs"]
    ]
    random.SystemRandom().shuffle(rows)
    return {"kind":"private_website_review_with_source_requirements",
            "outputs":rows, "phase_mapping_included":False,
            "ground_truth_included":False,
            "manual_blinding_check_required":True,
            "real_human_review_completed":False}


def rating_template(packet: dict, reviewer_id: str) -> dict:
    if (packet.get("kind") != "private_website_review_with_source_requirements"
        or not isinstance(reviewer_id,str) or not OID.fullmatch(reviewer_id)):
        raise ValueError("private review packet and valid pseudonym required")
    rows = packet.get("outputs")
    if not isinstance(rows,list) or not rows:
        raise ValueError("empty private review packet")
    ids = [row["output_id"] for row in rows]
    if len(ids) != len(set(ids)) or not all(OID.fullmatch(uid) for uid in ids):
        raise ValueError("invalid or duplicated review IDs")
    return {"schema_version":1,
            "kind":"independent_blinded_human_website_reviews",
            "model_or_agent_run_verified":False,
            "ratings":[{"output_id":uid,"reviewer_id":reviewer_id,
                        "scores":dict.fromkeys(DIMENSIONS),
                        "evidence":dict.fromkeys(DIMENSIONS,"")}
                       for uid in ids],
            "adjudications":[]}


def combine_reviews(first: dict, second: dict) -> dict:
    """Merge two files only after independent review; no automatic scoring."""
    for value in (first,second):
        if (value.get("schema_version")!=1 or
            value.get("kind")!="independent_blinded_human_website_reviews" or
            value.get("model_or_agent_run_verified") is not False or
            value.get("adjudications") != [] or not value.get("ratings")):
            raise ValueError("invalid independent reviewer file")
    one, two = first["ratings"], second["ratings"]
    ids1,ids2 = [r["output_id"] for r in one],[r["output_id"] for r in two]
    raters1,raters2 = {r["reviewer_id"] for r in one},{r["reviewer_id"] for r in two}
    if (len(raters1)!=1 or len(raters2)!=1 or raters1 & raters2
        or len(ids1)!=len(set(ids1)) or len(ids2)!=len(set(ids2))
        or set(ids1)!=set(ids2)):
        raise ValueError("reviewers or coverage do not match independent paired review")
    for row in one+two:
        scores,evidence=row["scores"],row["evidence"]
        if (set(scores)!=set(DIMENSIONS) or set(evidence)!=set(DIMENSIONS)
            or any(type(v) is not int or not 0<=v<=4 for v in scores.values())
            or any(not isinstance(v,str) or len(v.strip())<12 for v in evidence.values())):
            raise ValueError("finish every score and supporting reason before combining")
    return {"schema_version":1,"kind":first["kind"],
            "model_or_agent_run_verified":False,
            "ratings":one+two,"adjudications":[]}


def rehearse(directory: Path) -> dict:
    """Create new synthetic rehearsal directory and run all local stages."""
    root = _private_path(directory)
    root.mkdir(mode=0o700)  # refuse existing directory
    (root/"specifications").mkdir(mode=0o700)
    public = load_cases()[:5]
    cases = [{"id":f"H{i:03d}", "brief":"公開開發案例的合成操作演練，不是真正未見題："+c["title"],
              "answers":{key:c["answers"].get(key) for key in KEYS}}
             for i,c in enumerate(public,1)]
    _write(root/"cases.json",{"schema_version":1,
           "kind":"independent_private_website_cases","cases":cases})
    manifest=seal_private_cases(root/"cases.json")
    _write(root/"manifest.json",manifest)
    profiles={phase:{"agent_sha":digit*40, "prompt_sha":digit*64,
              "model_id":"SYNTHETIC_NO_MODEL", "runner_id":"OFFLINE_REHEARSAL",
              "resource_budget":"SYNTHETIC_FIXED"}
              for phase,digit in (("before","1"),("after","2"))}
    outputs=[]
    for case, commitment in zip(cases,manifest["commitments"]):
        for phase in ("before","after"):
            uid=uuid4().hex
            path="specifications/"+uid+".json"
            _write(root/path,build_spec(case["answers"]))
            outputs.append({"id":uid,"case_id":case["id"],"phase":phase,
                           "case_sha256":commitment["case_sha256"],
                           "path":path,"sha256":digest((root/path).read_bytes())})
    bundle={"schema_version":1,"kind":"externally_supplied_website_outputs_unverified",
            "official_model_execution_verified":False,"profiles":profiles,"outputs":outputs}
    _write(root/"bundle.json",bundle)
    packet=prepare_review(root/"cases.json",manifest,bundle,root)
    _write(root/"review-packet.json",packet)
    forms=[rating_template(packet,rater) for rater in
           ("SYNTHETIC_REVIEWER_A","SYNTHETIC_REVIEWER_B")]
    for i,form in enumerate(forms,1):
        _write(root/f"reviewer-{i}-blank.json",form)
        for row in form["ratings"]:
            row["scores"]=dict.fromkeys(DIMENSIONS,2)
            row["evidence"]=dict.fromkeys(DIMENSIONS,
                "這是公開合成操作演練的固定評分，並非真正人類判斷或能力成效。")
        _write(root/f"reviewer-{i}-synthetic.json",form)
    reviews=combine_reviews(*forms)
    _write(root/"reviews.json",reviews)
    result=compare(manifest,bundle,reviews,root)
    result["rehearsal_only"]=True
    result["ratings_are_synthetic"]=True
    _write(root/"comparison.json",result)
    return {"status":"SYNTHETIC_REHEARSAL_ONLY","case_count":len(cases),
            "outputs":len(outputs),"rating_count":result["rating_count"],
            "paired_mean_delta":result["paired_mean_delta_on_0_to_4_scale"],
            "real_agent_executed":False,"real_holdout_created":False,
            "real_human_review_completed":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="command",required=True)
    trial=sub.add_parser("rehearse")
    trial.add_argument("--directory",type=Path,required=True)
    for name,fields in (
        ("prepare-review",("cases","manifest","bundle","workspace","output")),
        ("rating-template",("packet","output")),
        ("combine",("first","second","output")),
    ):
        cmd=sub.add_parser(name)
        for field in fields:
            cmd.add_argument("--"+field,type=Path,required=True)
        if name=="rating-template":
            cmd.add_argument("--reviewer-id",required=True)
    args=p.parse_args()
    try:
        if args.command=="rehearse":
            print(json.dumps(rehearse(args.directory),ensure_ascii=False))
            return 0
        read=lambda path:_json(_private_path(path))
        if args.command=="prepare-review":
            value=prepare_review(args.cases,read(args.manifest),read(args.bundle),args.workspace)
        elif args.command=="rating-template":
            value=rating_template(read(args.packet),args.reviewer_id)
        else:
            value=combine_reviews(read(args.first),read(args.second))
        _write(args.output,value)
        print("PRIVATE_OUTPUT_CREATED_NO_MODEL_RUN")
        return 0
    except (OSError,ValueError,TypeError,KeyError,AttributeError):
        print("OFFLINE_WORKFLOW_BLOCKED: check input format, completion and private paths; no output overwritten",
              file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
