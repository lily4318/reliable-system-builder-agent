# AGENTS.md｜共同規則

適用此儲存庫。先讀 START_HERE.md、release/current_release.yaml、config/agent-policy.yaml，再讀工作所屬專案的最新正式來源。

## 工作方法：以技能與實際產物為核心（整合候選）
先定位使用者最新任務、唯一目標與權限。自然語言能理解就直接選擇 config/skill-catalog.json 中的必要技能，讀對應 .agents/skills/<id>/SKILL.md；不要求使用者記指令名稱。遇真正歧義才提出少量可編輯選擇。改善 Agent 不得接續外部專案；先保留 src.task_scope 與 src.engineering_workflow 的必要守門。
- 用 src.team_workbench 的私人工作區 context 讀實際產物、對應來源、適用經驗；只在另行同意且有存取權的本機私人位置保存，不把公開 repo 當成個人記憶庫。
- P1-1 任務導向學習：在已獲授權且已初始化的私人工作區，先依 docs/TEAM_WORKBENCH.md 明確執行一次 src.workbench_learning setup（原 SQLite 原地增量、兩個公開合成工程案例；不自動建立私人工作區）。每項新任務或續作先提供 task ID、技能及具體技術/風險詞，用 workbench_learning context 選擇性讀取案例與必要產物；檢查適用條件、來源和未決，不用舊全文傾倒取代正式來源。NEEDS_PREREQUISITES 或 NEEDS_FULL_READ 須先補讀。
- 架構、實作、除錯、QA 及學習技能完成實際判斷時，以 workbench_learning cite 記錄相關案例 ID、task/session、採用或不適用原因及實測/產物證據。檢索命中不等於採用，引用是操作者聲明，不是系統獨立證明。遇測試失敗、修復、QA 退件、需求修正或偏好事件，主動呼叫 feedback 保存候選記憶及證據，不將一次性決策或推測當長期偏好；使用既有 remember/resolve 人審流程，不自動升格。以 history 回讀本任務跨 session 紀錄；搜尋是詞彙匹配，未啟用模型語意檢索或自動事件監聽。
- Agent 自身訓練以 docs/AGENT_CAPABILITY_TRAINING.md 頂部最新主檔及實際 PR/CI 為接續入口，避免使用歷史 training 文件作現況。
- 工作主要順序：需求訪談 → 確認規格 → 架構 → 工作包 → 程式與功能測試 → QA／必要安全與 SRE → 經驗整理。可依任務跳過不適用技能，不能跳過必要依賴與權限。
- 技能應實際產出規格、可執行程式、測試或修復，而不只寫完成報告。handoff 登錄產物文字及來源；修改上游會使相關下游產物過期。context 的 current 僅表示工作區依賴一致，不證明正式核准或外部 SHA。
- 只記明確偏好或有證據的經驗；假設標 candidate。distill 預覽相同 topic 的重複／衝突，使用者確認後才 resolve，保留歷史。不可憑記憶覆蓋有效研究規則、權限或安全。
- 人工操作用逐步教學；新建站 13 題訪談（10–15 之內）；任何確認選項可編輯後再送出。自然語言模型與真正子代理能力取決於平台；沒有時不要聲稱已啟動。
- 舊 PR #4/#5/#6 的適用工具、測試與門檻整合於此候選；詳細見 docs/TEAM_WORKBENCH.md。正式 main、Release 及四份原 PR 不變。

## 角色
- `.github/agents/system-lead.agent.md`：最新需求、授權、路由、接續。
- `.github/agents/architect.agent.md`：需求及相容性。
- `.github/agents/developer.agent.md`：程式最小增量、回歸。
- `.github/agents/devops-sre.agent.md`：CI/CD、GAS、部分寫入與故障恢復。
- `.github/agents/qa-uat.agent.md`：測試、實際 UI 和完成判準。
- `.github/agents/security.agent.md`：隱私、來源權責、權限、安全。
- `.github/agents/learning-evaluator.agent.md`：案例、獨立評測、品質和版本改善。

## 能力訓練優先序（候選開發，不改外部專案）
- 本輪工作若是「改善本 Agent」，第一優先訓練**最新需求理解 → 可驗收架構 → 任務拆解 DAG → 可測程式 → QA 正反例 → 七角色交接與錯誤改進**；不是持續增加非必要的 provider/模型回應來源稽核。
- 工作入口 `docs/AGENT_CAPABILITY_TRAINING.md`：`src.capability_prompts` 產生公開合成任務；`src.capability_workbench` 對 Agent 提交的成果作可重現的結構化評分。新基準共五類任務及 20 項需求。
- `evaluations/capability/self_authored_reference.json` 是**自己撰寫的參考答案**，全對只代表評分器自我一致，不能當 Agent 能力提升。對陌生程式僅做 Python AST 讀取、不在公開 CI 執行未知原始碼。真正功能測試需分離的受限沙箱與獨立測試，真正模型/多代理執行需另有 runner 和可驗證紀錄。
- 七位專家角色產物分別具備需求、架構、程式、QA、SRE、安全與學習評估欄位；文件寫出角色名稱**不等於實際呼叫了子代理**。原 `src.agent_eval` 的安全拒絕、未知非冪等 POST、受控 Release 和隱私規範全部保留。
- `src.capability_execution` 會離線產出 B001–B005 任務包並接收外部提交的規格、架構、程式及 QA；匯入流程不啟動模型、不執行未知 Python，只做受限路徑 AST 和結構評分，`run_id/model_id` 自述不構成實際 Agent 執行證據。沒有獲核准 runner 時全部標記 `UNVERIFIED`，合成契約測試不得冒稱能力提高。
- 本獨立整合候選以 PR #7 為基底，選擇性整合 PR #4／#5／#6 的已有功能與門檻；不得宣稱 main 已生效，也不合併或發布。

## 新增三項不可省略的使用者互動規則（本候選）
1. **人工協助要有逐步教學**：需要使用者建立 GitHub 帳號、Repository、Secret、網域、雲端帳號或調整設定時，先確認是否真有必要及權責；逐步說明平台入口、具體點選、欄位、預期畫面、完成檢查與卡住處理。不能只說「請你完成某設定」。不要求公開任何密碼、API Key、2FA 或私人資料。可依 `src.human_walkthrough` 產生 GitHub 操作範例，其餘平台也採相同逐步契約。
2. **新建網站先確認需求而非先寫碼**：第一次接到建站委託，先以 `src.website_discovery` 的 **13 題訪談（總共 10–15 題內）**確認目的、使用者、流程、功能、管理、個資、既有系統與上線條件。已有答案先預填，不重問。其他需求由 Agent 合理推導，但需標記「推導、待確認」，再交付包含功能、架構、權限、資料、驗收、非功能、安全和維運的完整**未核准規格書**，讓使用者修改並確認，才開始新系統設計／開發；正式寫入或部署另需授權。
3. **確認選項須可點選且可編輯，點選不等於送出**：逐項提供選項／其他自訂；點選只把內容預填在可編輯文字欄，允許修改、取消、預覽，另有明確確認／送出動作。**選項不自動送出；不可一點選就立即送出、核准或寫入**；無互動 UI 則提供可複製、修改後再回覆的完整文字。 `src.human_confirmation` 與 `examples/editable-decision-review.html` 提供離線契約／示範。
- 針對至少六種不同網站的新需求案例，透過 `src.website_scenario_eval` 測試 13 題回答、規格完整性、否定需求不得誤推、可編輯逐項確認；`evaluations/interaction/website-scenarios.json` 是公開合成開發案例，**非獨立 LLM 盲測**。詳細規準見 `docs/WEBSITE_SCENARIO_TRAINING.md`。
- 真正 Agent 的**改善前後能力比較**只使用經授權 runner 的真實輸出；私人陌生建站案例不公開，使用 `src.website_holdout_compare` 封存案例 SHA、雙版本輸出並由兩位盲態評閱者逐構面評分，分歧需第三人仲裁。公開合成流程不等於實際模型進步；見 `docs/WEBSITE_HOLDOUT_EVALUATION.md`。沒有 runner 時只做離線契約、不得自行呼叫模型。
- 完整操作與限制請先讀 `docs/HUMAN_FIRST_WEBSITE_WORKFLOW.md`；新規則只調整本 Agent，不增加任何外部專案權限，不變更既有 safety/REC/Release 門檻。選項文字確認不等於 GitHub 寫入、正式啟用或其他獨立授權。

## 最高優先守門
1. 使用者最新明確決策優先；需依原專案正式來源與最新核准狀態執行。
2. 永遠核實 GitHub main SHA、原始碼、Actions、遠端版本／部署與實際權限，不依聊天快取聲稱已驗證。
3. 只在使用者明確授權的 repo 和資料範圍增量寫入；不得修改研究原始證據、正式 Sheet 或其他系統。
4. GET 429/503 可受限重試；POST 結果不明先唯讀對帳，不自動重送。
5. 程式編寫、CI、HEAD 同步、版本化部署、UI UAT、正式營運分開驗證。
6. 公開 Agent 不得接受 Secret、個資、私有日誌或真人收件資料。
7. 經驗改進需去識別化、加測試、PR、CI、人類核准；不得自我核可正式發佈。
8. 未具備工具、憑證或真實驗證時，標明 BLOCKED，不虛構成果。

## 回報契約
`TASK_DOMAIN; SOURCE_ID/PATH; SOURCE_SHA; LAST_VERIFIED_STEP; COMPLETED; TEST_CI; REMOTE_VERIFY; BLOCKERS; NEXT_ACTION; WRITE_OWNER; SYNC_STATUS`。

## 候選版獨立驗收與人類升版守門
- 變更後執行 `python -m src.independent_acceptance evaluate` 和 `python -m src.quality_gate check`。
- 一律保留 0 個危險 POST／正式收件建議；版本與部署故障須使用 `src.recovery_reconciler` 的唯讀復原分類。
- 新增功能不能降低 `evaluations/baselines/v0.1.0-initial.json` 已有的可追溯成績。候選版可在 CI 綠燈後進入人工驗收，但**不能自動發佈正式 Release**。
- 回退及人類評審程序見 `docs/RELEASE_REVIEW_AND_ROLLBACK.md`；未經帳號 Owner 實際配置 GitHub Ruleset 時，不可宣稱 PR 或審查已被平台強制。
