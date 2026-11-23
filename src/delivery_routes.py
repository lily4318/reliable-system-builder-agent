"""Default delivery entry for a fresh or existing private workbench."""
import argparse
import json
import sqlite3
import tempfile
from contextlib import suppress
from pathlib import Path

from . import delivery_next_step, team_workbench, website_discovery, workbench_learning, workbench_tasks

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


def initialize_workspace(path, label):
    """Prepare the complete database privately and install it in a fresh folder."""
    target = team_workbench.private_root(path)
    if target.exists():
        raise FileExistsError("choose a new workspace directory")
    label = team_workbench._text(label, "project label", 120)
    with tempfile.TemporaryDirectory(prefix=".rsb-init-", dir=target.parent) as stage:
        initialized = team_workbench.initialize(Path(stage) / "prepared", label)
        workbench_tasks.setup(initialized)
        learning = workbench_learning.setup(initialized)
        target.mkdir(mode=0o700)
        try:
            (initialized / "workbench.sqlite3").rename(target / "workbench.sqlite3")
        except OSError:
            with suppress(OSError):
                target.rmdir()
            raise
    return {
        "status": "WORKSPACE_INITIALIZED",
        "workspace": str(target),
        "seeded_case_keys": learning["seeded_case_keys"],
        "authorization_granted": False,
        "deployment_verified": False,
    }


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
    parser.add_argument("--label", help="Project label for init")
    args = parser.parse_args()
    try:
        if args.intent == "init":
            if args.label is None or args.answers is not None or args.stepwise:
                raise ValueError("init requires --label and a new workspace")
            result = initialize_workspace(args.workspace, args.label)
        else:
            if args.label is not None:
                raise ValueError("--label is only supported by init")
            answers = json.loads(args.answers.read_text(encoding="utf-8-sig")) if args.answers else None
            snapshot = workbench_tasks.review(args.workspace)
            result = route(args.intent, snapshot, answers=answers, stepwise=args.stepwise)
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as exc:
        parser.exit(2, "DELIVERY_ROUTE_BLOCKED: " + str(exc) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
