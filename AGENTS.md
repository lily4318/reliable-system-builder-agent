# AGENTS.md｜共同規則

適用此儲存庫。先讀 START_HERE.md、release/current_release.yaml、config/agent-policy.yaml，再讀工作所屬專案的最新正式來源。

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
- 本候選 PR 與未合併的 Draft PR #4／#5／#6 平行，不擅自把三份先前候選視為 main 已生效，也不合併任何 PR 或發布。

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
