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

## 真正 LLM 需求／架構評測的分離守門（候選，未獲正式採納）
- `src/llm_requirements_eval.py` 可透過**人類明確提供的外部 LLM runner**，向實際模型送出陌生多輪需求，再根據獨立人員標註的答案量測意圖、目標 Repo、讀寫授權、規格衝突、架構缺口、正確交接與需求保留。
- `evaluations/llm/public_dev_cases.json` 是作者暫擬的 **20 筆公開合成開發案例**，絕非獨立測試集或已測得模型成績。真正保留測試的案例與標準答案必須由獨立人工雙人標註，密封在 Repo 外，並在鎖定模型／Prompt 後才評估；程序見 `docs/LLM_REQUIREMENTS_EVAL.md`。
- GitHub Actions **只跑離線單元與資料格式驗證**，不得從 CI 秘密自動呼叫付費模型、公開 holdout／憑證或捏造模型答對率；缺模型 runner，明確 `NOT_RUN`。`src/llm_runner_preflight.py` 是唯讀完整性預檢：即使 runner 腳本 SHA、Prompt SHA 與評測器 SHA 一致，也只代表本地設定自述與位元組吻合，**不等於已驗證供應商模型、API 回覆來源、人類授權或可計費呼叫**。模型輸出和人工評分均須獨立列示，不把欄位一致率冒稱架構品質或真實系統建置成功。
- `src/llm_provider_evidence.py` 另驗證私有請求與正規化回應證據的 SHA、公開案例、model/version、請求／回應 ID、授權範圍與有效期。即使全數一致，仍只標記 **LOCAL_EVIDENCE_MATCHED**，不推定供應商已認證、審查者有權限或可呼叫模型。原始供應商記錄須由獨立權責者在官方來源核對，不得由本地合成檔自我證明。
- 新的 `src/llm_provider_dual_source.py` 會先核對上述本地 manifest，再對照**獨立輸入、唯讀取得**的供應商來源匯出以及先前 request/response ID 清冊；拒絕雙來源不一致、重複 ID、可辨識重播、來源保管角色相同、過舊或缺漏的匯出與清冊。匯出來源、保管身份與清冊是**使用者提供的宣告**，本程式不連線供應商、不驗簽、不驗證其官方來源／人工授權，不能把雙來源一致或未在清冊出現說成真正 API 驗證／全域無重播；一律維持 `official_api_response_authenticated=false` 和 `human_authorization_independently_verified=false`。
- 此候選與 Draft PR #4（目標辨識）及 #5（七角色交接）分支相互獨立、未合併。未經人類審核不得將任何候選提升為正式 Agent Release。

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
