# Multi-Agent 系統架構

**公開 Agent 層**：本 Repository 僅提供共用工作契約、專家角色、去識別化案例、評測與版本。
**原專案主檔層**：每個系統的程式、正式需求、部署及資料權責仍在其原路徑。
**執行層**：實際工具／瀏覽器／CI／GAS API；沒工具就不能宣稱操作成功。
**獨立驗證層**：QA、Security、Learning Evaluator 區分模擬與真實驗收。

## 七專家交接 Gate（候選增量）
- `src/engineering_workflow.py` 只能根據已標註、**來自權威來源且需人類或外部工具先驗證**的結構化事實，提出下一個 `owner_role`／`next_safe_action`；其 `mutation_permitted` 永遠為 false。
- 安全順序：來源及 target SHA → 未知／部分寫入優先 SRE 唯讀對帳 → 需求／驗收（Architect）→ 架構相依／回退（Architect）→ 資料／ACL（Security）→ 寫入授權（System Lead）→ 候選 patch（Developer）→ 原碼 SHA 回讀／正負測／同 SHA CI（QA）→ Learning Evaluator 人審 PR。
- `release` 階段不會輸出部署行動：沒有實際 UAT 證據由 QA 接續，有 UAT 證據仍交 System Lead／人類獨立核准。所有已成功的測試只對公開標註案例及程式邏輯有效，並非真實跨專案執行結果。
- 具體交接來源、否決案例與測試入口見 `docs/ENGINEERING_COLLABORATION.md`。

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
