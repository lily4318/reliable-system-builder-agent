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

## 七專家可驗證交接（候選訓練，不等於真的召喚子代理）
- 先由 System Lead 確認本輪唯一目標、正式來源／SHA 與寫入授權，然後由 Architect 明列需求、正反向驗收條件、相依性和回退策略。
- Developer **只能**在需求／架構／Security 守門與候選修正授權齊備時提出同原路徑最小 Patch；DevOps/SRE 若遇 `UNKNOWN`／`PARTIAL` 非冪等寫入必須停止 POST、以可信 GET 唯讀對帳，不能照順序直接進下一關。
- Security 獨立檢查資料分級、ACL、Secrets 與外部專案範圍；QA/UAT 核對正向／負向測試、原碼與 CI **同 SHA**，將離線 CI、遠端部署及真 UI 證據分開列示；Learning Evaluator 把去識別化失敗轉成公開案例與品質退步守門，**不自行批准 Release**。
- 七角色的輸入／輸出／交接契約見 `docs/ENGINEERING_COLLABORATION.md`。 `src/engineering_workflow.py` 是讀取**人類或外部工具已驗證之結構化證據**的純建議函式，僅輸出下一個角色和安全行動；`evaluations/cases/engineering_handoffs.json` 是公開合成案例，不是實際多 Agent 協作、真實系統除錯或模型權重訓練證據。
- 此改進為獨立候選 PR；未與先前任務目標分流 PR 合併，不可擅自宣稱兩份候選已共同進入 main。合併順序及整合後 CI 需人工驗證。

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
