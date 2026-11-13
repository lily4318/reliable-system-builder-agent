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

## 新 LLM 行為評測候選：真實模型跑測 vs. 結構化規則
- 新增 `src/llm_requirements_eval.py`、`tests/test_llm_requirements_eval.py`，和 20 筆公開合成暫擬標籤的開發案例。GitHub Actions 僅驗證資料格式、API runner 協定（本地 mock）及品質門檻，**不執行真實 LLM**。
- 模型跑測必須帶明確 `--runner-command`、`--model-id`，將最後一輪／過往訊息與有限需求 ID 送入實際模型，並在獨立評分程式中與人工預標註答案比較；可量測 task/target/authorization、需求缺口、架構安全 gate、專家路由、risk flags、需求 ID 精確率／召回率及危險越權。
- 真正的 holdout 需要獨立標註、兩位標註者一致性與仲裁、外部封存 SHA、無污染證據及私有評測環境；`holdout_manifest.example.json` 只是不可直接通過的樣板。模型標籤／輸出來源及保留集盲測仍需真實驗證。
- 不能把公版資料格式通過率、mock runner 測試成功或自行填寫的 `model_id` 當成模型能力；架構設計的語意與可實作性另需人工評分。
- 完整 rubric、流程與守門見 `docs/LLM_REQUIREMENTS_EVAL.md`。

## 未來 ML/DL
若要真正機器學習，需要另備經授權資料、標註規範、訓練／驗證／獨立測試切分、可重現訓練程式、模型權重／特徵版本管理、成本及安全評估；目前都未宣稱具備。

## v0.1.0 候選｜隔離式恢復驗收與品質退步保護
- 另一條獨立路徑：`src/recovery_reconciler.py`、`src/independent_acceptance.py`、`evaluations/acceptance/recovery_cases.json`。情境案例由預先標註的 expected classification 比對，**不讀取原政策引擎的預測當標準答案**。
- 現有公開測試不是盲測；需要外部審查者另建立真正封存盲測集，才能宣稱模型泛化。
- 品質基準：`evaluations/baselines/v0.1.0-initial.json`；當前候選的最低門檻：`evaluations/quality-targets.json`。
- `python -m src.quality_gate check` 比較原政策與恢復案例的覆蓋、關鍵失敗、危險操作，任何退步須停止升版。
- 人工 Release 與安全回退見 `docs/RELEASE_REVIEW_AND_ROLLBACK.md`；此輪未授權任何外部正式系統寫入。
