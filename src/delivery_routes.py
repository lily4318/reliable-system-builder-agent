"""Read-only entry for website, booking, and follow-up work in an existing task pool."""
import argparse
import json
import sqlite3
from pathlib import Path

from . import delivery_next_step, website_discovery, workbench_tasks

INTENTS = {
    "做網站": "website",
    "建立網站": "website",
    "接預約": "booking",
    "接上預約": "booking",
    "繼續": "resume",
    "幫我做": "resume",
    "逐步查看": "resume",
    "修復": "repair",
}
ROUTES = {
    "website": ("project-intake", "requirements-spec", "architecture-design",
                "implement-feature", "test-and-acceptance", "deployment"),
    "booking": ("project-scope", "architecture-design", "implement-feature",
                "test-and-acceptance", "deployment", "security-review"),
    "repair": ("resume-project", "debug-and-repair", "test-and-acceptance"),
    "resume": ("resume-project", "project-control"),
}
REVIEW_REQUIRED = "NEEDS_EXISTING_PROJECT_SCOPE"


def route(intent, snapshot, *, answers=None, stepwise=False):
    """Project current selections without changing approval or persisted state.

    Use route-prefixed IDs only for work explicitly assigned that route in
    the original project plan. Existing work with other IDs remains visible
    in the resume route. Full-pool authorization still governs execution.
    """
    normalized = INTENTS.get(intent, intent)
    if normalized not in ROUTES:
        raise ValueError("map the task to website, booking, repair, or resume first")
    checkpoint = delivery_next_step.choose(snapshot)
    if normalized in ("website", "booking", "repair"):
        rows = snapshot["tasks"]
        scoped = [row for row in rows if row["id"].startswith(normalized + "-")]
        dependencies = {dep for row in scoped for dep in row["deps"]}
        done_prerequisites = [
            row for row in rows if row["id"] in dependencies and row["state"] == "DONE"
            and not row["id"].startswith(normalized + "-")
        ]
        projected = {**snapshot, "tasks": scoped + done_prerequisites}
        selected = delivery_next_step.choose(projected)
        selected["protected_inflight_task_ids"] = checkpoint["protected_inflight_task_ids"]
        selected["recovery_required_task_ids"] = checkpoint["recovery_required_task_ids"]
        checkpoint = selected

    one_step = stepwise or intent == "逐步查看"
    ready = checkpoint["ready_task_ids"]
    result = {
        **checkpoint, "intent": normalized, "skills": ROUTES[normalized],
        "mode": "ONE_STEP" if one_step else "CONTINUE",
        "next_task_ids": ready[:1] if one_step else ready,
        "current_questions": [
            {"id": decision["id"], "question": decision["question"]}
            for decision in snapshot["open_decisions"]
            if decision["id"] in checkpoint["ask_decision_ids"]
        ],
    }

    if normalized == "website" and checkpoint["status"] == REVIEW_REQUIRED:
        draft = website_discovery.draft_spec({} if answers is None else answers)
        pending = set(draft["unanswered_questions"])
        result["missing_intake_questions"] = [
            question for question in website_discovery.questions()["questions"]
            if question["id"] in pending
        ]
        result["specification_draft"] = draft
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intent")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--answers", type=Path)
    parser.add_argument("--stepwise", action="store_true")
    args = parser.parse_args()
    try:
        answers = json.loads(args.answers.read_text(encoding="utf-8-sig")) if args.answers else None
        snapshot = workbench_tasks.review(args.workspace)
        result = route(args.intent, snapshot, answers=answers, stepwise=args.stepwise)
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as exc:
        parser.exit(2, "DELIVERY_ROUTE_BLOCKED: " + str(exc) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
