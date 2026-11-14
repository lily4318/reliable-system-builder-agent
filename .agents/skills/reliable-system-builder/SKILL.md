---
name: reliable-system-builder
description: Safety-first software construction with verified source, specialist routing, regression tests, deployment reconciliation, and evidence-based release gates.
---
# Reliable System Builder Skill

先讀本 Repository 根目錄 `START_HERE.md`、`AGENTS.md`，**先判定是要改善 Agent 本身還是把 Agent 用於其他專案**，再依工作模式讀必要正式來源。訓練／評測這個 Agent 本身時，僅用本 Repository 候選 PR，不觸碰前一個專案。

先從 config/skill-catalog.json 選擇適用技能，讀相應 SKILL.md。使用者只需白話描述任務。依 docs/TEAM_WORKBENCH.md 按需回讀專案私人記憶及產物；不自動建立或上傳私人記憶。

1. 判定任務來源、Git SHA、使用者授權及讀／寫／部署／真人資料範圍。
2. 依 `.github/agents/` 路由主管、架構、開發、SRE、QA、資安與評測專家；工具不支援子代理時不得聲稱已召喚。
3. 所有非冪等 POST、未知寫入或部分寫入先唯讀對帳，禁止盲目重送。
4. 以同原路徑最小增量更新；實際 CI、版本、部署、UI UAT 各自查證。
5. 去識別化的事故可加入案例庫，經 PR、測試與人類核准才更新正式 Agent。

確定性的安全政策評測入口：`python -m src.agent_eval evaluate`。不使用模型 API，不重新訓練任何 LLM 權重。
