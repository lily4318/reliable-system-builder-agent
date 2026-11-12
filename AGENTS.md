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
