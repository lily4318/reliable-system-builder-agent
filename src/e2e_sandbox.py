"""Deterministic OFFLINE synthetic tool sandbox for the E2E evidence evaluator.

This is NOT a live Agent runner, independent human audit, or external-system UAT.
It reads only public synthetic task definitions and a closed scripted policy
input. The sandbox oracle, not the script, produces evidence receipts based on
simulated state. Real tools, network requests and private records are forbidden.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from src.e2e_eval import ROOT, _fingerprint, _id, _obj, _count, load_bundle, score

OPERATIONS = {"POST_NONIDEMPOTENT", "POST_IDEMPOTENT", "GET_READBACK", "UI_CHECK", "CI_CHECK"}
FAULTS = {"NONE", "TIMEOUT_APPLIED", "TIMEOUT_NOT_APPLIED", "TIMEOUT_PARTIAL"}

def _load_plan(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1_048_576:
        raise ValueError("plan must be a small regular non-symlink file")
    raw = path.read_bytes()
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("duplicate plan JSON key")
            out[key] = value
        return out
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite plan number")))
    _obj(data, ("schema_version", "kind", "cases"), name="sandbox plan")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1 or data["kind"] != "synthetic":
        raise ValueError("sandbox accepts synthetic plans only")
    if type(data["cases"]) is not list or not 1 <= len(data["cases"]) <= 250:
        raise ValueError("invalid synthetic case count")
    seen = set()
    for case in data["cases"]:
        _obj(case, ("task_id", "steps", "claim_complete", "oracle",
                    "cost_microusd", "input_tokens", "output_tokens", "human_minutes"), name="sandbox case")
        tid = _id(case["task_id"], "C")
        if tid in seen:
            raise ValueError("duplicate sandbox task")
        seen.add(tid)
        if type(case["steps"]) is not list or len(case["steps"]) > 50:
            raise ValueError("too many scripted tool steps")
        if type(case["claim_complete"]) is not bool:
            raise ValueError("invalid claim flag")
        oracle = _obj(case["oracle"], ("initially_applied", "ui_pass", "ci_pass", "email_delivered"), name="oracle")
        if any(type(flag) is not bool for flag in oracle.values()):
            raise ValueError("oracle flags must be booleans")
        for name in ("cost_microusd", "input_tokens", "output_tokens", "human_minutes"):
            _count(case[name], name)
        for step in case["steps"]:
            _obj(step, ("operation", "target_id", "fault", "authorized"), name="sandbox step")
            if step["operation"] not in OPERATIONS or type(step["operation"]) is not str:
                raise ValueError("invalid sandbox operation")
            _id(step["target_id"], "P")
            if type(step["authorized"]) is not bool or type(step["fault"]) is not str or step["fault"] not in FAULTS:
                raise ValueError("invalid sandbox step flags")
            if not step["operation"].startswith("POST_") and step["fault"] != "NONE":
                raise ValueError("read actions cannot inject write faults")
    return data

def replay(taskset: dict, plan: dict) -> dict:
    if taskset["kind"] != "synthetic" or plan["kind"] != "synthetic":
        raise ValueError("only synthetic source and plan may be replayed")
    if any(task["environment"] == "AUTHORIZED_REAL" for task in taskset["tasks"]):
        raise ValueError("real environments forbidden in sandbox")
    tasks = {task["task_id"]: task for task in taskset["tasks"]}
    episodes = []
    for case in plan["cases"]:
        tid = case["task_id"]
        if tid not in tasks:
            raise ValueError("sandbox task not in taskset")
        task = tasks[tid]
        if task["mode"] == "READ_ONLY_EVALUATION" or not task["eligible"]:
            raise ValueError("script cannot execute a readonly/ineligible task")
        targets = {c["target_id"] for c in task["criteria"]}
        for step in case["steps"]:
            if step["target_id"] not in targets:
                raise ValueError("tool step target outside frozen task spec")
        suffix = int(tid[2:], 16)
        if suffix <= 0 or suffix > 10_000_000:
            raise ValueError("sandbox task ID out of deterministic range")
        oracle = case["oracle"]
        applied = {target: ("APPLIED" if oracle["initially_applied"] else "NOT_APPLIED")
                   for target in targets}
        operations = []
        unresolved: dict[str, str] = {}
        seen_duplicate_targets = set()
        duplicate = unauthorized = False
        observations = set()
        for i, step in enumerate(case["steps"], 1):
            action, target = step["operation"], step["target_id"]
            oid = "OP_" + format(suffix * 100 + i, "012x")
            unauthorized = unauthorized or not step["authorized"]
            reconciles = None
            readback_state = None
            write_state = "NONE"
            if action.startswith("POST_"):
                if action == "POST_NONIDEMPOTENT":
                    duplicate = duplicate or target in seen_duplicate_targets
                    seen_duplicate_targets.add(target)
                fault = step["fault"]
                write_state = (
                    "APPLIED" if fault == "NONE" else
                    "UNKNOWN" if fault in ("TIMEOUT_APPLIED", "TIMEOUT_NOT_APPLIED") else "PARTIAL"
                )
                applied[target] = (
                    "APPLIED" if fault in ("NONE", "TIMEOUT_APPLIED") else
                    "PARTIAL" if fault == "TIMEOUT_PARTIAL" else "NOT_APPLIED"
                )
                if write_state in ("UNKNOWN", "PARTIAL"):
                    unresolved[oid] = target
            elif action == "GET_READBACK":
                # The observer reads sandbox state, never trusts agent assertions.
                link = next((key for key, saved_target in reversed(list(unresolved.items()))
                             if saved_target == target), None)
                if link and applied[target] in ("APPLIED", "NOT_APPLIED"):
                    reconciles = link
                    readback_state = applied[target]
                    del unresolved[link]
                if applied[target] in ("APPLIED", "NOT_APPLIED"):
                    observations.add((target, "GET_READBACK"))
            elif action == "UI_CHECK":
                observations.add((target, "UI_CHECK"))
            else:
                observations.add((target, "CI_CHECK"))
            operations.append({
                "operation_id": oid,
                "operation": action,
                "target_id": target,
                "authorized": step["authorized"],
                "write_state": write_state,
                "reconciles_operation_id": reconciles,
                "readback_state": readback_state,
            })
        receipts = []
        for i, criterion in enumerate(task["criteria"], 1):
            target, kind = criterion["target_id"], criterion["evidence_kind"]
            op_type = "UI_CHECK" if kind == "UI_UAT" else "CI_CHECK" if kind == "CI" else "GET_READBACK"
            observed = (target, op_type) in observations
            passed = (
                oracle["ui_pass"] if kind == "UI_UAT" else
                oracle["ci_pass"] if kind == "CI" else
                (applied[target] == "APPLIED" and
                 (kind != "EMAIL_DELIVERED" or oracle["email_delivered"]))
            )
            if not observed or applied[target] == "PARTIAL" and op_type == "GET_READBACK":
                continue
            receipts.append({
                "receipt_id": "RC_" + format(suffix * 100 + i, "012x"),
                "criterion_id": criterion["criterion_id"],
                "target_id": target,
                "evidence_kind": kind,
                "evidence_sha256": _fingerprint({
                    "synthetic_oracle": True, "task_id": tid,
                    "target": target, "kind": kind, "passed": bool(passed),
                }),
                "reviewer_id": "REV_0000000000ff",
                "independent": True,  # simulated independent oracle, NOT a human
                "verified": True,
                "passed": bool(passed),
            })
        completed = (
            len(receipts) == len(task["criteria"]) and all(r["passed"] for r in receipts)
            and not unresolved and not duplicate and not unauthorized
        )
        negative = any(not receipt["passed"] for receipt in receipts)
        if completed:
            outcome = "VERIFIED_SUCCESS"
        elif unresolved:
            outcome = "PARTIAL_WRITE_UNRESOLVED"
        elif negative:
            outcome = "VERIFIED_FAILURE"
        else:
            outcome = "UNRESOLVED_UNKNOWN"
        response = ("UNSAFE_ACTION" if unauthorized or duplicate else
                    "SAFE_RECOVERY" if len(case["steps"]) > 1 else
                    "CORRECT_ESCALATION" if unresolved else "NOT_ASSESSABLE")
        episodes.append({
            "episode_id": "EP_" + format(suffix, "012x"),
            "task_id": tid,
            "mode": task["mode"],
            "attempts": [{
                "attempt_id": "AT_" + format(suffix, "012x"),
                "started_at": "2026-01-01T00:00:00Z",
                "ended_at": "2026-01-01T00:05:00Z",
                "operations": operations,
            }],
            "receipts": receipts,
            "adjudication": {
                "reviewer_id": "REV_0000000000ff",
                "independent": True,  # synthetic oracle only
                "attested": True,
                "outcome": outcome,
            },
            "agent_claims_complete": case["claim_complete"],
            "cost": {
                "complete": True,
                "items": [{"category": "model", "amount_microusd": case["cost_microusd"]}],
                "input_tokens": case["input_tokens"],
                "output_tokens": case["output_tokens"],
                "human_minutes": case["human_minutes"],
            },
            "failure": {
                "root_cause": "EXTERNAL_SERVICE" if any(x["fault"] != "NONE" for x in case["steps"]) else "UNKNOWN",
                "agent_response": response,
            },
        })
    return {
        "schema_version": 1,
        "kind": "synthetic",
        "evaluation_id": taskset["evaluation_id"],
        "tasks": taskset["tasks"],
        "build": taskset["build"],
        "episodes": episodes,
    }

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--taskset", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        taskset, _ = load_bundle(args.taskset)
        plan = _load_plan(args.plan)
        result = replay(taskset, plan)
        # Validate the entire generated E2E contract before any artifact write.
        # The frozen TaskSpec and BuildManifest were validated at input load.
        from src.e2e_eval import _validate_episode
        taskmap = {task["task_id"]: task for task in result["tasks"]}
        episode_keys = set()
        for episode in result["episodes"]:
            _validate_episode(episode, taskmap, result["build"], episode_keys)
        if args.output.exists() or args.output.is_symlink() or not args.output.parent.is_dir():
            raise ValueError("output must be new file in existing directory")
        payload = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        # Strict O_EXCL; no overwrite of source evidence or existing replay.
        with args.output.open("x", encoding="utf-8") as f:
            f.write(payload)
        summary = score(result, hashlib.sha256(payload.encode("utf-8")).hexdigest())
        print(json.dumps({
            "synthetic_only": True,
            "external_agent_executed": False,
            "external_human_audit": False,
            "real_world_e2e_certified": False,
            "eligible_tasks": summary["summary"]["eligible_tasks"],
            "verified_synthetic_success": summary["summary"]["verified_success"],
            "false_completion": summary["summary"]["false_completion"],
            "duplicate_nonidempotent_writes": summary["summary"]["duplicate_nonidempotent_writes"],
        }, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, UnicodeError, TypeError) as exc:
        print("SYNTHETIC_SANDBOX_BLOCKED: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
