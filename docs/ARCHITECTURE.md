# Multi-Agent 系統架構

**公開 Agent 層**：本 Repository 僅提供共用工作契約、專家角色、去識別化案例、評測與版本。
**原專案主檔層**：每個系統的程式、正式需求、部署及資料權責仍在其原路徑。
**執行層**：實際工具／瀏覽器／CI／GAS API；沒工具就不能宣稱操作成功。
**獨立驗證層**：QA、Security、Learning Evaluator 區分模擬與真實驗收。

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
