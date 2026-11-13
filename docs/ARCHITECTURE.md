# Multi-Agent 系統架構

**公開 Agent 層**：本 Repository 僅提供共用工作契約、專家角色、去識別化案例、評測與版本。
**原專案主檔層**：每個系統的程式、正式需求、部署及資料權責仍在其原路徑。
**執行層**：實際工具／瀏覽器／CI／GAS API；沒工具就不能宣稱操作成功。
**獨立驗證層**：QA、Security、Learning Evaluator 區分模擬與真實驗收。

## 工作目標分流（優先於專家角色路由）
1. 讀本輪使用者最新明確意圖，將 `IMPROVE_AGENT` 與 `APPLY_AGENT` 區分：前者改本 Agent 的訓練候選 PR／規則／評測，後者才可能讀指定的外部目標專案。
2. 不從 Agent URL、舊聊天或先前專案進度推導另一個專案的寫入授權；先定唯一 `TARGET_REPO`、`PROPOSED_WRITE_REPO`、權責。
3. `src/task_scope.py` 針對**已標註**的結構化意圖提供 fail-closed 守門；它不是自然語言分類模型。新案例須包含錯誤目標、意圖更正與未授權對照組。
4. 正式 Agent 改善採去識別化案例→負測→安全最小修改→PR/CI→人工審查→候選版本，絕不自動發布或修改外部系統。

## 任務路由
- 不清楚版本／需求 → System Lead → Architect。
- 程式修改 → Developer → QA → Security。
- 部署故障／部分寫入 → DevOps/SRE → Security → QA。
- 正式啟用 → 專案負責人、適用核准、實際部署與 UI UAT。
- 重複故障 → Learning Evaluator → 新的去識別化 regression case → PR 評審。

## 故障狀態機
`DISCOVER → READ_ONLY_AUDIT → PLAN → AUTHORIZE → PATCH → TEST → REMOTE_VERIFY → UI_UAT → RELEASE`。
只要 `PARTIAL_WRITE` 或 `UNKNOWN_POST_RESULT` 就轉 `READ_ONLY_RECONCILE`，停止所有非冪等 POST。

## 防止三天部署中斷的工程原則
任務必留最新 SHA、已完成步驟、失敗呼叫、遠端當前狀態、Owner、可安全執行的下一個 GET；且保留小範圍修正、回歸及可靠回退路徑。
