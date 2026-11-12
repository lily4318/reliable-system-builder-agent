"""Independent *offline* golden-case acceptance for incident reconciliation.

Separate data/logic path from src.agent_eval. Public cases are not blind.
Runs no external API, no deployment, no mutation and no model training.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from src.recovery_reconciler import GET_ACTIONS, reconcile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "evaluations/acceptance/recovery_cases.json"

def load_cases(path: Path = DATA) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    data = json.loads(raw)
    if data.get("schema_version") != 1 or data.get("independent_blind_holdout") is not False:
        raise ValueError("unsupported independent recovery dataset")
    if data.get("origin") != "sanitized_synthetic_scenarios_not_private_logs":
        raise ValueError("dataset may contain unreviewed non-public material")
    entries = data.get("cases")
    if not isinstance(entries, list) or len(entries) < 15:
        raise ValueError("independent recovery cases are insufficient")
    seen = set()
    for case in entries:
        if not isinstance(case, dict):
            raise ValueError("invalid case")
        code = case.get("id")
        if not isinstance(code, str) or not re.fullmatch(r"A[0-9]{3}", code) or code in seen:
            raise ValueError("invalid or repeated independent case ID")
        seen.add(code)
        if not isinstance(case.get("evidence"), dict) or not isinstance(case.get("expected_classification"), str):
            raise ValueError("invalid expected classification/evidence")
        if not isinstance(case.get("critical"), bool):
            raise ValueError("missing critical flag")
        # Incidents are synthetic. This is a precautionary, not complete DLP scan.
        serialized = json.dumps(case, ensure_ascii=False)
        if re.search(r"(?i)(?:bearer\s+[a-z0-9-_.]{16,}|ghp_[a-z0-9]{25,}|github_pat_[a-z0-9_]{35,}|https?://)", serialized):
            raise ValueError("potential secret or live URL in independent case")
    return entries, hashlib.sha256(raw).hexdigest()

def evaluate(root: Path = ROOT) -> dict:
    cases, digest = load_cases(root / "evaluations/acceptance/recovery_cases.json")
    results = []
    for c in cases:
        assessment = reconcile(c["evidence"])
        actions = assessment["allowed_next_actions"]
        safe = (
            assessment["mutation_allowed"] is False
            and assessment["formal_launch_allowed"] is False
            and assessment["requires_human_review"] is True
            and isinstance(actions, list)
            and all(action in (*GET_ACTIONS, "HUMAN_REVIEW") for action in actions)
        )
        results.append({
            "id": c["id"], "expected": c["expected_classification"],
            "actual": assessment["classification"], "critical": c["critical"],
            "no_unsafe_action": safe,
            "passed": safe and assessment["classification"] == c["expected_classification"],
        })
    critical = [r for r in results if r["critical"]]
    return {
        "dataset_sha256": digest, "total": len(results),
        "passed": sum(r["passed"] for r in results),
        "failed": sum(not r["passed"] for r in results),
        "critical_total": len(critical),
        "critical_passed": sum(r["passed"] for r in critical),
        "unsafe_action_count": sum(not r["no_unsafe_action"] for r in results),
        "public_cases_not_blind_holdout": True,
        "release_gate_passed": all(r["passed"] for r in results) and bool(critical),
        "cases": results,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("evaluate",))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = evaluate()
        content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        print(content)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content, encoding="utf-8")
        return 0 if report["release_gate_passed"] else 1
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("INDEPENDENT_ACCEPTANCE_BLOCKED: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
