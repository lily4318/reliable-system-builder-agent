# AGENTS.md｜共同規則

適用此儲存庫。先讀 START_HERE.md、release/current_release.yaml、config/agent-policy.yaml，再讀工作所屬專案的最新正式來源。

## 首要任務辨識：改善 Agent ≠ 操作其他專案

**執行任何 GitHub／檔案／部署操作之前**，依本輪使用者最新明確意圖，先記錄 `TASK_MODE`、`AGENT_REPO`、`TARGET_REPO`、`PROPOSED_WRITE_REPO`、`AUTHORIZATION`。舊聊天、專案背景與先前施工方向**不能**覆蓋本輪對目標的更正。

- **`IMPROVE_AGENT`**：使用者要求「訓練／改善／強化／評測這個 Agent」時，目標是 **本 Agent Repository 本身**：指令、專家流程、去識別化案例、測試、CI 與候選 PR。**不得藉機繼續修改以前服務過的網站或其他目標專案**。不自動宣稱重新訓練 LLM 權重。依 `config/learning-policy.yaml`，候選修正應走獨立分支／可審查 PR 與人工核准，不直接自行升正式版。
- **`APPLY_AGENT`**：使用者明確要用 Agent 診斷／修復某個**指定的外部系統**時，先核對該系統唯一正式來源及獨立讀寫授權；Agent URL 只是工具入口，不能當外部 Repo 寫入授權。
- **`UNRESOLVED`**：本輪未能確認是改善 Agent 還是應用 Agent、目標不明或候選寫入路徑錯誤，必須 `HOLD_INTENT/HOLD_TARGET`；允許先唯讀查證，不推測後修改外部專案。
- 在每次交接／最終回報中，明確區分 `AGENT_TRAINING_CANDIDATE`（本 Repository）、`EXTERNAL_PROJECT_ACTION`（另一專案）及真正模型微調（需要另外的資料、流程和權限）。

合成的結構化任務守門：`src/task_scope.py`、`evaluations/cases/task_scope.json`、`tests/test_task_scope.py`。它**不會自動理解自然語句**；意圖仍須從本輪使用者話語核實，公開案例的 100% 不等於 LLM 任務理解準確率。見 `docs/TASK_SCOPE_TRAINING.md`。

## 角色
- `.github/agents/system-lead.agent.md`：最新需求、授權、路由、接續。
- `.github/agents/architect.agent.md`：需求及相容性。
- `.github/agents/developer.agent.md`：程式最小增量、回歸。
- `.github/agents/devops-sre.agent.md`：CI/CD、GAS、部分寫入與故障恢復。
- `.github/agents/qa-uat.agent.md`：測試、實際 UI 和完成判準。
- `.github/agents/security.agent.md`：隱私、來源權責、權限、安全。
- `.github/agents/learning-evaluator.agent.md`：案例、獨立評測、品質和版本改善。

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
