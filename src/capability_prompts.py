"""Generate an executable public development assignment for a real Agent.

No gold components/reference solution or benchmark score is exposed in the
generated task packet. This cannot launch an Agent or authenticate its output.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

from src.capability_workbench import load_tasks


def task_prompt(task_id: str) -> dict:
    task = next((x for x in load_tasks() if x["id"] == task_id), None)
    if task is None:
        raise ValueError("unknown public task ID")
    return {
        "task_id": task["id"],
        "brief": task["brief"],
        "requirements": [{"id": r["id"], "description": r["description"]}
                         for r in task["requirements"]],
        "required_python_function": task["implementation_function"],
        "instructions": [
            "針對這項陌生但公開合成需求，獨立寫出可觀察的驗收準則與衝突假設；不得照抄現成參考答案。",
            "規劃有明確責任的架構元件、資料流與依賴關係，寫出可安全回退的最小實作路徑。",
            "產生具 owner 和 depends_on 的任務 DAG，每一項需求都要由工作項涵蓋。",
            "在隔離測試資料夾建立 Python 候選函式；程式執行測試需要另外授權的受限環境，公開 CI 只做 AST 檢查。",
            "提供每項需求至少一個正測與一個負測，描述預期行為及可重現證據。",
            "記錄七個專家角色各自的輸入與輸出交接；禁止聲稱已真的召喚七個子代理。",
            "未知非冪等寫入只能唯讀對帳，正式上線需人類另行核准。",
            "回覆 JSON submission 物件，不包含自稱已執行模型、正式部署、權重訓練的未驗證主張。",
        ],
        "submission_shape": {
            "task_id": "Bxxx",
            "requirements": [{"id": "R1", "acceptance": "可驗收描述"}],
            "architecture": {"components": [{"name": "component-id",
                                              "responsibility": "負責的資料流與邊界"}],
                             "links": [{"from": "component-id", "to": "other-component-id"}]},
            "plan": [{"id": "S1", "owner": "system-lead", "depends_on": [],
                      "requirement_ids": ["R1"], "deliverable": "可查核產物"}],
            "implementation": {"path": "isolated/candidate.py",
                               "function": task["implementation_function"]},
            "qa": [{"requirement_id": "R1", "kind": "positive",
                    "expected": "可重現預期"}],
            "handoffs": [{"role": "architect", "input": "前階段證據",
                          "output": "審查產物"}],
            "risk": {"hazard": "需根據題目判定",
                     "unknown_write_action": "READ_ONLY_RECONCILE",
                     "human_release_review": True},
            "claims": {"real_agent_invoked": False, "model_weights_trained": False,
                       "system_deployed": False},
        },
        "benchmark_gold_components_included": False,
        "reference_code_included": False,
        "actual_model_execution_by_generator": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = task_prompt(args.task_id)
        content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        print(content)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content, encoding="utf-8")
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("CAPABILITY_PROMPT_BLOCKED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
