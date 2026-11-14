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

## 2026-11-14 候選｜真正工程能力的可執行基準（非 LLM 訓練完成）
- `evaluations/capability/public_tasks.json`：5 類合成陌生工程任務與 20 項需求；`src.capability_prompts` 只將題目和提交格式提供給 Agent，不包含參考元件列表或參考程式內容。
- `src.capability_workbench` 評估需求驗收（20 分）、架構模組（15）、任務 DAG（20）、程式 AST 存在（10）、QA 正負例（20）、七角色交接（10）、基本安全（5）。`self_authored_reference.json` 的滿分為**作者自己撰寫的結構對照組**，不能說明模型真的做對或未見過的任務也能做對。
- `src/capability_reference.py` 是經人工編寫的可信極小演算法，僅作 repo 單元測試示例。無網路沙箱與真正模型 runner 未設置，公開 CI 不執行未信任候選程式，不聲稱有已完成的端到端系統開發成績。
- 真實訓練循環是：固定題目／評分器 SHA → 由可核驗的 Agent 執行至少三次 → 用相同模型與資源測前後版本 → 獨立人類審查架構、需求完整性及隔離程式行為 → 在未看過的 holdout 比較。過程不等於底層權重微調。
- 結構基準的限制、實際試跑步驟與未決問題見 `docs/AGENT_CAPABILITY_TRAINING.md`；原有 policy/recovery gate 不移除。

## 2026-11-14｜六類建站需求推導與人工確認測試（PR #7 候選）
- `evaluations/interaction/website-scenarios.json` 提供六類公開合成網站、由作者標註的應有／禁止推導項目及未回答欄位。 `src.website_scenario_eval` 比對 `src.website_discovery` 的草稿，測量明示需求保留、完整規格構成、缺漏不得補值、合理的推導與否定功能不誤推、逐項選擇後可編輯且不自動傳送、未核准狀態。
- 公開合成案例及標準答案**不能**宣稱獨立盲測、真正 LLM 推理或模型變聰明。真正效果仍需有授權的 Agent runner、未曝光題庫、盲態人工語意評審與最終規格書的使用者確認。
- CLI：`python -m src.website_scenario_eval evaluate`；`python -m src.website_scenario_eval packets` 提供不含預期標籤的公開測試任務包。詳見 `docs/WEBSITE_SCENARIO_TRAINING.md`。

## 未來 ML/DL
若要真正機器學習，需要另備經授權資料、標註規範、訓練／驗證／獨立測試切分、可重現訓練程式、模型權重／特徵版本管理、成本及安全評估；目前都未宣稱具備。

## v0.1.0 候選｜隔離式恢復驗收與品質退步保護
- 另一條獨立路徑：`src/recovery_reconciler.py`、`src/independent_acceptance.py`、`evaluations/acceptance/recovery_cases.json`。情境案例由預先標註的 expected classification 比對，**不讀取原政策引擎的預測當標準答案**。
- 現有公開測試不是盲測；需要外部審查者另建立真正封存盲測集，才能宣稱模型泛化。
- 品質基準：`evaluations/baselines/v0.1.0-initial.json`；當前候選的最低門檻：`evaluations/quality-targets.json`。
- `python -m src.quality_gate check` 比較原政策與恢復案例的覆蓋、關鍵失敗、危險操作，任何退步須停止升版。
- 人工 Release 與安全回退見 `docs/RELEASE_REVIEW_AND_ROLLBACK.md`；此輪未授權任何外部正式系統寫入。
