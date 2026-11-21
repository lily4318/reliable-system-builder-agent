"""Offline, executable structural workbench for an Agent's engineering deliverables.

Scores requirements, architecture, plan DAG, static Python implementation
presence, QA traces, role handoff and minimal safety. Does NOT execute candidate
code, run an LLM, judge code semantics or prove any real seven-agent collaboration.
The bundled perfect reference is authored by us and NOT a model achievement.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "evaluations/capability/public_tasks.json"
REFERENCE = ROOT / "evaluations/capability/self_authored_reference.json"
WEIGHTS = {
    "requirements": 20, "architecture": 15, "plan": 20,
    "implementation_static": 10, "qa": 20, "handoff": 10, "safety": 5,
}
ROLES = frozenset((
    "system-lead", "architect", "security", "developer", "qa-uat",
    "devops-sre", "learning-evaluator",
))


def _dict(x: object) -> dict:
    return x if isinstance(x, dict) else {}


def _list(x: object) -> list:
    return x if isinstance(x, list) else []


def _meaningful(x: object, min_len: int = 20) -> bool:
    return isinstance(x, str) and len(x.strip()) >= min_len


def load_tasks(path: Path = TASKS) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or (
        data.get("schema_version") != 1 or
        data.get("independent_blind_holdout") is not False or
        data.get("real_agent_runs_observed") is not False
    ):
        raise ValueError("public benchmark declarations invalid")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 5:
        raise ValueError("insufficient independent development task families")
    seen, categories = set(), set()
    for case in cases:
        if not isinstance(case, dict) or not re.fullmatch(
            r"B[0-9]{3}", str(case.get("id", ""))
        ) or case["id"] in seen:
            raise ValueError("duplicate or invalid task ID")
        seen.add(case["id"])
        if not _meaningful(case.get("brief"), 40):
            raise ValueError("task context missing")
        reqs = _list(case.get("requirements"))
        ids = [r.get("id") for r in reqs if isinstance(r, dict)]
        if len(ids) != 4 or len(set(ids)) != 4 or any(
            not re.fullmatch(r"R[1-4]", str(x)) for x in ids
        ):
            raise ValueError("invalid requirement IDs")
        if any(not _meaningful(r.get("description"), 10) or
               type(r.get("critical")) is not bool for r in reqs):
            raise ValueError("missing requirement detail")
        components = _list(case.get("required_components"))
        if len(components) < 3 or len(components) != len(set(components)):
            raise ValueError("invalid reference architecture components")
        if set(case.get("required_roles", [])) != ROLES or (
            not re.fullmatch(r"[a-z_]+", str(case.get("implementation_function", "")))
        ):
            raise ValueError("invalid implementation contract or specialist set")
        categories.add(case.get("category"))
    if len(categories) < 5:
        raise ValueError("insufficient task variety")
    return cases


def load_submissions(path: Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("invalid submission schema")
    items = data.get("submissions")
    if not isinstance(items, list) or not items:
        raise ValueError("no candidate submissions")
    seen = set()
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("task_id"), str):
            raise ValueError("invalid candidate record")
        if item["task_id"] in seen:
            raise ValueError("duplicated candidate task")
        seen.add(item["task_id"])
    return items


def _dag_steps(steps: list) -> tuple[bool, set[str], set[str]]:
    if not steps or any(not isinstance(s, dict) for s in steps):
        return False, set(), set()
    ids = [x.get("id") for x in steps]
    if any(not isinstance(x, str) or not re.fullmatch(r"S[0-9]{1,2}", x)
           for x in ids) or len(set(ids)) != len(ids):
        return False, set(), set()
    by_id = {x["id"]: x for x in steps}
    owners, covered = set(), set()
    for s in steps:
        deps = s.get("depends_on")
        reqs = s.get("requirement_ids")
        if not isinstance(deps, list) or not isinstance(reqs, list) or any(
            not isinstance(v, str) for v in deps + reqs
        ) or len(set(deps)) != len(deps) or any(
            d not in by_id or d == s["id"] for d in deps
        ) or not _meaningful(s.get("deliverable")) or s.get("owner") not in ROLES:
            return False, set(), set()
        owners.add(s["owner"])
        covered.update(reqs)
    visiting, visited = set(), set()

    def visit(sid: str) -> bool:
        if sid in visiting:
            return False
        if sid in visited:
            return True
        visiting.add(sid)
        for dependency in by_id[sid]["depends_on"]:
            if not visit(dependency):
                return False
        visiting.remove(sid)
        visited.add(sid)
        return True

    if not all(visit(sid) for sid in by_id):
        return False, set(), set()
    return True, owners, covered


def _implementation_static(item: dict, task: dict, root: Path) -> bool:
    detail = _dict(item.get("implementation"))
    path = detail.get("path")
    if not isinstance(path, str) or not path.endswith(".py"):
        return False
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return False
    file = root / candidate
    if file.is_symlink() or not file.resolve().is_relative_to(root.resolve()):
        return False
    try:
        if not file.is_file() or file.stat().st_size > 65536:
            return False
        tree = ast.parse(file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, SyntaxError, ValueError):
        return False
    function = detail.get("function")
    if function != task["implementation_function"]:
        return False
    return any(isinstance(node, ast.FunctionDef) and node.name == function and
               any(isinstance(child, ast.Return) for child in ast.walk(node))
               for node in tree.body)


def score_task(task: dict, item: dict, root: Path = ROOT) -> dict:
    ids = {r["id"] for r in task["requirements"]}
    comps = set(task["required_components"])
    reqs = _list(item.get("requirements"))
    good_req = {q.get("id") for q in reqs if isinstance(q, dict) and
                q.get("id") in ids and _meaningful(q.get("acceptance"))}
    req_ok = len(reqs) == len(ids) and len(good_req) == len(ids)

    arch = _dict(item.get("architecture"))
    modules = _list(arch.get("components"))
    good_components = {m.get("name") for m in modules if isinstance(m, dict)
                       and m.get("name") in comps and
                       _meaningful(m.get("responsibility"))}
    links = _list(arch.get("links"))
    links_ok = len(links) >= len(comps)-1 and all(
        isinstance(e, dict) and e.get("from") in comps and e.get("to") in comps
        and e.get("from") != e.get("to") for e in links
    )
    architecture_ok = (len(good_components) == len(comps) and
                       len(modules) == len(comps) and links_ok)

    steps = _list(item.get("plan"))
    dag, owners, covered = _dag_steps(steps)
    plan_ok = dag and owners == ROLES and ids.issubset(covered)
    # User/model generated code is NOT executed by CI. This is only AST presence.
    code_ok = _implementation_static(item, task, root)

    qas = _list(item.get("qa"))
    test_pairs = {(q.get("requirement_id"), q.get("kind")) for q in qas
                  if isinstance(q, dict) and q.get("requirement_id") in ids and
                  q.get("kind") in ("positive", "negative") and
                  _meaningful(q.get("expected"))}
    qa_ok = all((rid, "positive") in test_pairs and
                (rid, "negative") in test_pairs for rid in ids)

    h = _list(item.get("handoffs"))
    handoff_roles = {v.get("role") for v in h if isinstance(v, dict) and
                     v.get("role") in ROLES and
                     _meaningful(v.get("input")) and _meaningful(v.get("output"))}
    handoff_ok = handoff_roles == ROLES and len(h) == len(ROLES)
    risk = _dict(item.get("risk"))
    safety_ok = (risk.get("hazard") == task["hazard"] and
                 risk.get("unknown_write_action") == "READ_ONLY_RECONCILE" and
                 risk.get("human_release_review") is True)
    claims = _dict(item.get("claims"))
    unsafe_claim = any(claims.get(key) is not False for key in (
        "real_agent_invoked", "model_weights_trained", "system_deployed"
    ))
    checks = {
        "requirements": req_ok,
        "architecture": architecture_ok,
        "plan": plan_ok,
        "implementation_static": code_ok,
        "qa": qa_ok,
        "handoff": handoff_ok,
        "safety": safety_ok,
    }
    score = sum(weight for name, weight in WEIGHTS.items() if checks[name])
    return {"task_id": task["id"], "score": score, "checks": checks,
            "unsafe_unverified_claim": unsafe_claim, "task_passed": score == 100
            and not unsafe_claim}


def evaluate(submissions: Path = REFERENCE, tasks: Path = TASKS,
             root: Path = ROOT) -> dict:
    cases = load_tasks(tasks)
    candidates = load_submissions(submissions)
    by_id = {s["task_id"]: s for s in candidates}
    unknown = sorted(set(by_id) - {x["id"] for x in cases})
    if unknown:
        raise ValueError("unknown submitted task IDs")
    rows = [score_task(c, by_id.get(c["id"], {}), root) for c in cases]
    score = sum(x["score"] for x in rows) / len(rows)
    is_reference = submissions.resolve() == REFERENCE.resolve()
    safe = all(not x["unsafe_unverified_claim"] for x in rows)
    return {
        "evaluation_kind": "structural_public_development_benchmark_not_model_training",
        "submission_kind": (
            "self_authored_reference_fixture_not_agent_result" if is_reference
            else "externally_supplied_structured_artifacts_origin_unverified"
        ),
        "task_count": len(rows), "submitted_count": len(candidates),
        "mean_structural_score": round(score, 2),
        "tasks_full_structural_score": sum(x["task_passed"] for x in rows),
        "unsafe_unverified_claim_count": sum(x["unsafe_unverified_claim"] for x in rows),
        "all_safety_claims_conservative": safe,
        "metrics": {name: sum(x["checks"][name] for x in rows) for name in WEIGHTS},
        "cases": rows,
        "self_authored_public_gold": True,
        "independent_holdout_evaluated": False,
        "real_llm_or_seven_agents_invoked": False,
        "actual_program_correctness_evaluated": False,
        "architecture_semantics_human_reviewed": False,
        "deployment_or_real_ui_verified": False,
        "formal_release_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "evaluate"))
    parser.add_argument("--submissions", type=Path, default=REFERENCE)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-structural-score", type=int, default=0)
    args = parser.parse_args()
    try:
        if args.command == "validate":
            result = {"valid": True, "public_tasks": len(load_tasks()),
                      "reference_submissions": len(load_submissions(REFERENCE)),
                      "agent_performance_measured": False}
        else:
            result = evaluate(args.submissions)
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        print(rendered)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        if args.command == "evaluate" and (
            result["mean_structural_score"] < args.min_structural_score or
            not result["all_safety_claims_conservative"]
        ):
            return 1
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("CAPABILITY_WORKBENCH_BLOCKED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
