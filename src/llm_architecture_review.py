"""Aggregate two independently submitted, PRIVATE architecture-plan reviews.

No LLM or network calls. Raw plan outlines and reviewer submissions stay in
private local files. Distinct IDs are attested, not identity verification.
This tool cannot substitute for adjudication of reviewer disagreements.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.llm_requirements_eval import ROOT

DIMENSIONS = (
    "requirement_coverage",
    "components_and_data_flow",
    "security_and_authorization",
    "failure_and_rollback",
    "acceptance_testability",
)


def _private(path: Path) -> dict:
    path = Path(path).resolve()
    if path.is_relative_to(ROOT.resolve()):
        raise ValueError("private architecture review must stay outside public repo")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("invalid review JSON object")
    return data


def _scores(review: dict, case_ids: set[str], sha: str, model: str) -> dict[str, dict]:
    if review.get("schema_version") != 1 or (
        review.get("dataset_sha256") != sha or
        review.get("model_id_user_supplied") != model or
        review.get("reviewed_without_other_scorer") is not True or
        not isinstance(review.get("reviewer_id"), str) or
        not review["reviewer_id"].strip()
    ):
        raise ValueError("review identity, model, dataset or blind declaration invalid")
    values = review.get("cases")
    if not isinstance(values, list) or len(values) != len(case_ids):
        raise ValueError("review case count mismatch")
    rows = {}
    for item in values:
        if not isinstance(item, dict) or set(item) != {"id", "scores"} or (
            item["id"] not in case_ids or item["id"] in rows or
            not isinstance(item["scores"], dict) or
            set(item["scores"]) != set(DIMENSIONS) or
            any(type(v) is not int or v not in (0, 1, 2)
                for v in item["scores"].values())
        ):
            raise ValueError("invalid review case/score")
        rows[item["id"]] = item["scores"]
    return rows


def aggregate(packet_path: Path, reviewer_a: Path, reviewer_b: Path) -> dict:
    packet = _private(packet_path)
    if packet.get("schema_version") != 1 or (
        packet.get("blind_architecture_human_review_pending") is not True or
        not isinstance(packet.get("dataset_sha256"), str) or
        not isinstance(packet.get("model_id_user_supplied"), str)
    ):
        raise ValueError("invalid private architecture packet")
    cases = packet.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("no private architecture cases")
    ids = [item.get("id") for item in cases if isinstance(item, dict)]
    if len(ids) != len(cases) or any(not isinstance(x, str) for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("duplicate or invalid private case IDs")
    a = _private(reviewer_a)
    b = _private(reviewer_b)
    if a.get("reviewer_id") == b.get("reviewer_id"):
        raise ValueError("two distinct reviewers are required")
    rows_a = _scores(a, set(ids), packet["dataset_sha256"], packet["model_id_user_supplied"])
    rows_b = _scores(b, set(ids), packet["dataset_sha256"], packet["model_id_user_supplied"])
    cells, agrees, disputed = len(ids) * len(DIMENSIONS), 0, 0
    dim_means = {}
    for dimension in DIMENSIONS:
        grades = []
        for case_id in ids:
            a_value, b_value = rows_a[case_id][dimension], rows_b[case_id][dimension]
            agrees += int(a_value == b_value)
            disputed += int(a_value != b_value)
            grades.extend((a_value, b_value))
        dim_means[dimension] = round(sum(grades) / len(grades), 4)
    return {
        "evaluation_type": "private_two_reviewer_architecture_semantic_rating",
        "model_id_user_supplied": packet["model_id_user_supplied"],
        "dataset_sha256": packet["dataset_sha256"],
        "reviewer_ids_declared_distinct_not_verified": True,
        "reviewed_case_count": len(ids),
        "rating_dimensions": list(DIMENSIONS),
        "rating_scale": "0_missing_or_incorrect_1_partial_2_sufficient",
        "exact_cell_agreement": round(agrees / cells, 4),
        "disputed_cells_require_adjudication": disputed,
        "dimension_mean_scores_of_two_reviewers": dim_means,
        "semantic_review_completed": disputed == 0,
        "independent_holdout_origin_proven": False,
        "model_identity_verified": False,
        "human_adjudication_completed": False,
        "formal_release_or_deployment_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("aggregate",))
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--review-a", type=Path, required=True)
    parser.add_argument("--review-b", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = aggregate(args.packet, args.review_a, args.review_b)
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        print(rendered)
        if args.output:
            # Aggregated, no raw plan text or gold labels.
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("ARCHITECTURE_REVIEW_BLOCKED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
