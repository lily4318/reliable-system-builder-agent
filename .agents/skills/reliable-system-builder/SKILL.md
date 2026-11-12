---
name: reliable-system-builder
description: Safety-first software construction with verified source, specialist routing, regression tests, deployment reconciliation, and evidence-based release gates.
---
# Reliable System Builder Skill

先讀本 Repository 根目錄 `START_HERE.md`、`AGENTS.md`，再讀目標專案最新正式來源。

1. 判定任務來源、Git SHA、使用者授權及讀／寫／部署／真人資料範圍。
2. 依 `.github/agents/` 路由主管、架構、開發、SRE、QA、資安與評測專家；工具不支援子代理時不得聲稱已召喚。
3. 所有非冪等 POST、未知寫入或部分寫入先唯讀對帳，禁止盲目重送。
4. 以同原路徑最小增量更新；實際 CI、版本、部署、UI UAT 各自查證。
5. 去識別化的事故可加入案例庫，經 PR、測試與人類核准才更新正式 Agent。

確定性的安全政策評測入口：`python -m src.agent_eval evaluate`。不使用模型 API，不重新訓練任何 LLM 權重。
