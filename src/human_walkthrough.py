"""Step-by-step user-assisted setup instructions; no remote actions."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

PATH = Path(__file__).resolve().parents[1] / "evaluations/interaction/human-github-walkthroughs.json"


def workflows() -> dict:
    value=json.loads(PATH.read_text(encoding="utf-8"))
    recipes=value.get("workflows")
    if (value.get("schema_version")!=1 or
        value.get("no_automatic_account_or_settings_changes") is not True or
        not isinstance(recipes,list) or len(recipes)<3):
        raise ValueError("human walkthrough contract invalid")
    ids=set()
    for recipe in recipes:
        if (not isinstance(recipe,dict) or not isinstance(recipe.get("id"),str)
            or recipe["id"] in ids or not isinstance(recipe.get("prerequisite"),str)
            or len(recipe["prerequisite"])<20):
            raise ValueError("invalid manual task")
        ids.add(recipe["id"])
        steps=recipe.get("steps")
        if not isinstance(steps,list) or not 5<=len(steps)<=12:
            raise ValueError("manual assistance requires step-by-step UI details")
        for num,step in enumerate(steps,1):
            if (not isinstance(step,dict) or step.get("number")!=num or
                not isinstance(step.get("action"),str) or len(step["action"])<25 or
                not isinstance(step.get("verification"),str) or
                len(step["verification"])<20):
                raise ValueError("manual steps require action and expected check")
    return value


def walkthrough(task_id:str) -> dict:
    match=[x for x in workflows()["workflows"] if x["id"]==task_id]
    if len(match)!=1:
        raise ValueError("unknown manual workflow; explain steps for the actual UI instead")
    return {**match[0],"human_performs_actions":True,
            "assistant_cannot_claim_setup_completed":True,
            "never_share_password_token_or_recovery_code":True,
            "stop_and_report_if_ui_or_permission_differs":True}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task",required=True)
    args=parser.parse_args()
    try:
        print(json.dumps(walkthrough(args.task),ensure_ascii=False,indent=2))
        return 0
    except (OSError,ValueError,TypeError):
        print("HUMAN_WALKTHROUGH_BLOCKED: use a verified task-specific UI procedure",file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
