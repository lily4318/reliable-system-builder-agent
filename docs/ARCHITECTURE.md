# Multi-Agent 系統架構

**公開 Agent 層**：本 Repository 僅提供共用工作契約、專家角色、去識別化案例、評測與版本。
**原專案主檔層**：每個系統的程式、正式需求、部署及資料權責仍在其原路徑。
**執行層**：實際工具／瀏覽器／CI／GAS API；沒工具就不能宣稱操作成功。
**獨立驗證層**：QA、Security、Learning Evaluator 區分模擬與真實驗收。

## 自主系統開發能力訓練主軸（獨立候選）
1. **System Lead** 把未知需求轉成編號條件及可觀察的驗收。**Architect** 規劃元件、相依、資料流與未決假設。**Developer** 提出程式候選。**QA/UAT** 用可重現正負測檢查行為，**DevOps/SRE** 製作回退／CI 計畫，**Security** 提供必要資料邊界，**Learning Evaluator** 比較新舊成果。
2. 每一階段都能在結構化提交中留下可回讀的 artifact：`requirements`、`architecture`、`plan`、`implementation`、`qa`、`handoffs`、`risk`。任務相依須為無循環 DAG，QA 與程式需回指需求 ID。
3. 執行入口 `src.capability_prompts` 出題；`src.capability_workbench` 僅檢查結構與 AST，不執行未知候選程式。既有安全政策只作必要的安全閘，並非本訓練的主題。
4. 公開 reference 不是 LLM 行為證據。真實能力須由模型／七角色執行紀錄、外部無網路沙箱正反測及人工架構審查另行驗證。完整規劃見 `docs/AGENT_CAPABILITY_TRAINING.md`。

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


## 技能層與私人工作區（整合候選）
自然語言由 AI 判斷任務，System Lead 依 skill-catalog 選擇技能，按角色需要讀 SKILL.md。工作區以 SQLite 保存可回讀產物與已記錄經驗，顯式依賴檢查使舊規格修訂失效；不取代正式專案來源。公開知識只放通用原則及範本。角色分工不等於子代理調度，詳見 TEAM_WORKBENCH.md。
