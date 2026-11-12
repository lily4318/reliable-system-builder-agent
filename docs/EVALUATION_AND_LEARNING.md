# 持續評測與企業式改善

## 已實作 v0.1
- `incidents/sanitized-cases/`：不包含原始專案 ID、OAuth、內部部署資訊的抽象化案例。
- `evaluations/cases/regressions.json`：公開可重現的正、反政策情境。
- `src/agent_eval.py`：零外部相依的**確定性安全決策引擎**，僅做政策評估、不對外操作。
- `tests/test_agent_eval.py`：對案例、授權、POST、HTTP、部署及正式上線的回歸檢查。
- `.github/workflows/agent-ci.yml`：push、PR、手動與每週唯讀政策評測。

## 持續改進的正確定義
這是透過事故回饋、案例資料、規則與 PR 改善**Agent 工作流程**；不是訓練或微調 GPT 等底層模型的權重。

## 改進循環
1. 取得可信且授權的實際事故；記錄根因是否已確認，不能捏造缺失數值。
2. 先去識別化，形成新的失敗案例、正確決策與反例。
3. 把新案例加入 regression，先以測試重現錯誤。
4. 只修改相關邏輯，透過 PR、CI、獨立審查與人工核准決定是否更新。
5. 版本、commit、評測與回退點完整留存。
6. 定期評估事故復發率、真實部署成功率、修復時間及重大安全違規。

## 評測限制
公開回歸集可以評估此 Repository 的規則演算法，但不能當作獨立盲測。所有模擬案例的 100% 只是政策最低門檻，不等於實際使用者任務達成率 100%。

## 未來 ML/DL
若要真正機器學習，需要另備經授權資料、標註規範、訓練／驗證／獨立測試切分、可重現訓練程式、模型權重／特徵版本管理、成本及安全評估；目前都未宣稱具備。

## v0.1.0 候選｜隔離式恢復驗收與品質退步保護
- 另一條獨立路徑：`src/recovery_reconciler.py`、`src/independent_acceptance.py`、`evaluations/acceptance/recovery_cases.json`。情境案例由預先標註的 expected classification 比對，**不讀取原政策引擎的預測當標準答案**。
- 現有公開測試不是盲測；需要外部審查者另建立真正封存盲測集，才能宣稱模型泛化。
- 品質基準：`evaluations/baselines/v0.1.0-initial.json`；當前候選的最低門檻：`evaluations/quality-targets.json`。
- `python -m src.quality_gate check` 比較原政策與恢復案例的覆蓋、關鍵失敗、危險操作，任何退步須停止升版。
- 人工 Release 與安全回退見 `docs/RELEASE_REVIEW_AND_ROLLBACK.md`；此輪未授權任何外部正式系統寫入。

## 真實標註、雙版本比較與封存保留資料（候選 PR）
本輪新增 `src/feedback_eval.py`，標註由人類審核的真實任務 outcomes、證據等級、去識別化 reviewer ID、證據 SHA，拒絕 CI-only 冒充真實部署或 UI 成功；任何不能確定的狀態須標為 unknown。

評測會計算 action accuracy、coverage、abstention、false completion claims、unauthorized mutation，以及**標註資料自身**的已知結果成功比例和標註案件耗時；使用相同 label SHA 的 baseline/candidate 比較。標註資料的成功比例與時間在不同 Agent 間不變，**不能冒稱 Agent 的端到端成功率或 MTTR**；`agent_verified_task_success_rate=null`，直到有與指定 Agent 版本綁定且經原系統驗收的執行軌跡。一般真實評測規劃至少 30 筆、無法證明的數字一律未知。未達成數據門檻不能宣稱 improved。

獨立保留資料採**非公開封存**、開發／holdout group 隔離、reviewer 分離、人工 SHA 核對與候選 commit 固定；工具檢查的是離線形式和人工宣告，**不是**密碼學簽章、第三方外部驗證或底層模型重新訓練。範例與指引見 `docs/FEEDBACK_AND_HOLDOUT.md`。

## E2E Execution Evidence（PR #3 候選）
新增 src/e2e_eval.py：依固定 TaskSpec、AgentBuildManifest、獨立驗收收據、部分寫入對帳、失敗歸因、microUSD 費用，對合成 Episode 計算端到端完成率。與 PR #1 動作正確率不同。真實來源尚未驗證，real_world_e2e_certified=false；見 docs/E2E_EXECUTION_EVIDENCE.md。
