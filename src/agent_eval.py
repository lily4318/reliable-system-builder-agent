"""Public deterministic policy tests, NOT language-model training or deployment."""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluations/cases/regressions.json"
DECISIONS = {
    "HOLD_TARGET", "HOLD_SOURCE", "RECONCILE_READ_ONLY",
    "NO_POST_RETRY", "RETRY_BOUNDED_GET", "READ_ONLY_OK", "HOLD_HTTP",
    "HOLD_METHOD", "HOLD_APPROVAL", "HOLD_INVENTORY", "HOLD_SHA",
    "HOLD_ACCESS", "HOLD_INTAKE", "HOLD_FORMAL",
    "READY_FOR_PRIVATE_DEPLOY_ONLY", "READY_FOR_HUMAN_LAUNCH_REVIEW",
    "REQUIRE_UI_UAT", "UI_EVIDENCE_VERIFIED",
    "READY_FOR_PATCH_ONLY", "HOLD_UNSUPPORTED",
}
REQUIRED = (
    "README.md", "START_HERE.md", "AGENTS.md", "release/current_release.yaml",
    "config/agent-policy.yaml", "config/learning-policy.yaml",
    "config/evaluation-policy.yaml", ".github/workflows/agent-ci.yml",
    ".github/agents/system-lead.agent.md", ".github/agents/architect.agent.md",
    ".github/agents/developer.agent.md", ".github/agents/devops-sre.agent.md",
    ".github/agents/qa-uat.agent.md", ".github/agents/security.agent.md",
    ".github/agents/learning-evaluator.agent.md",
    ".agents/skills/reliable-system-builder/SKILL.md",
    ".claude/skills/reliable-system-builder/SKILL.md",
    "docs/INCIDENT_RECOVERY.md", "docs/EVALUATION_AND_LEARNING.md",
    "evaluations/cases/regressions.json", "incidents/sanitized-cases/README.md",
    "src/llm_requirements_eval.py", "tests/test_llm_requirements_eval.py",
    "evaluations/llm/public_dev_cases.json", "docs/LLM_REQUIREMENTS_EVAL.md",
)

def decide(s):
    """Fail-closed advice only; cannot invoke external actions."""
    if s.get("target_isolated") is not True:
        return "HOLD_TARGET"
    if s.get("source_verified") is not True:
        return "HOLD_SOURCE"
    if s.get("partial_write") is True or s.get("unknown_write_result") is True:
        return "RECONCILE_READ_ONLY"
    op = s.get("operation")
    if op == "post_retry":
        return "NO_POST_RETRY"
    if op == "read":
        if s.get("method") != "GET":
            return "HOLD_METHOD"
        if s.get("http_status") in (429, 503):
            return "RETRY_BOUNDED_GET"
        return "READ_ONLY_OK" if s.get("http_status") == 200 else "HOLD_HTTP"
    if op == "private_deploy":
        if s.get("approved") is not True:
            return "HOLD_APPROVAL"
        if s.get("inventory_verified") is not True:
            return "HOLD_INVENTORY"
        if s.get("head_sha_verified") is not True:
            return "HOLD_SHA"
        if s.get("access_myself") is not True or s.get("execute_as_deployer") is not True:
            return "HOLD_ACCESS"
        if s.get("intake_closed") is not True:
            return "HOLD_INTAKE"
        return "READY_FOR_PRIVATE_DEPLOY_ONLY"
    if op == "formal_intake":
        names = ("rec_approved", "pi_approved", "privacy_ready",
                 "consent_ready", "ui_verified", "launch_authorized")
        if not all(s.get(name) is True for name in names):
            return "HOLD_FORMAL"
        return "READY_FOR_HUMAN_LAUNCH_REVIEW"
    if op == "ui_acceptance":
        return "UI_EVIDENCE_VERIFIED" if s.get("actual_manual_ui") is True else "REQUIRE_UI_UAT"
    if op == "code_patch":
        return "READY_FOR_PATCH_ONLY" if s.get("approved") is True else "HOLD_APPROVAL"
    return "HOLD_UNSUPPORTED"

def load_cases(path=DATASET):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("synthetic_or_sanitized") is not True:
        raise ValueError("unsupported or non-redacted dataset")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("missing cases")
    seen = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("scenario"), dict):
            raise ValueError("invalid case")
        cid = case.get("id")
        if not isinstance(cid, str) or not re.fullmatch(r"R[0-9]{3}", cid) or cid in seen:
            raise ValueError("invalid or duplicated case ID")
        seen.add(cid)
        if case.get("expected") not in DECISIONS or not isinstance(case.get("critical"), bool):
            raise ValueError("invalid case expectations")
    return cases

def validate(root=ROOT):
    missing = [p for p in REQUIRED if not (Path(root) / p).is_file()]
    if missing:
        raise ValueError("missing artifacts: " + ", ".join(missing))
    cases = load_cases(Path(root) / "evaluations/cases/regressions.json")
    critical = sum(c["critical"] for c in cases)
    if critical < 10:
        raise ValueError("insufficient critical cases")
    # A heuristic privacy scan, not a guarantee of no sensitive data.
    patterns = (
        r"\bghp_[A-Za-z0-9]{25,}\b",
        r"\bgithub_pat_[A-Za-z0-9_]{35,}\b",
        r"\bAIza[A-Za-z0-9_-]{30,}\b",
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    )
    public = [Path(root) / "evaluations/cases/regressions.json",
              Path(root) / "evaluations/llm/public_dev_cases.json"]
    public.extend((Path(root) / "incidents/sanitized-cases").glob("*.md"))
    for file in public:
        content = file.read_text(encoding="utf-8")
        for pattern in patterns:
            if re.search(pattern, content):
                raise ValueError("public case privacy scan failed: " + file.name)
    return {"valid": True, "required_paths": len(REQUIRED),
            "cases": len(cases), "critical_cases": critical,
            "privacy_heuristic_scan": "passed"}

def evaluate(root=ROOT):
    validate(root)
    cases = load_cases(Path(root) / "evaluations/cases/regressions.json")
    rows = []
    for case in cases:
        actual = decide(case["scenario"])
        rows.append({"id": case["id"], "actual": actual,
                     "expected": case["expected"],
                     "critical": case["critical"], "passed": actual == case["expected"]})
    total = len(rows)
    passed = sum(r["passed"] for r in rows)
    safety = [r for r in rows if r["critical"]]
    safety_passed = sum(r["passed"] for r in safety)
    return {"evaluation_type": "deterministic_public_policy_regression_not_llm_training",
            "total": total, "passed": passed, "failed": total - passed,
            "critical_total": len(safety), "critical_passed": safety_passed,
            "independent_blind_holdout": False,
            "release_gate_passed": passed == total and safety_passed == len(safety),
            "cases": rows}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "evaluate"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = validate() if args.command == "validate" else evaluate()
        output = json.dumps(result, indent=2, ensure_ascii=False)
        print(output)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output + "\n", encoding="utf-8")
        return 0 if args.command == "validate" or result["release_gate_passed"] else 1
    except (ValueError, OSError, json.JSONDecodeError) as err:
        print("AGENT_EVALUATION_BLOCKED: " + str(err), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
