# Reliable System Builder Agent｜可靠系統建置與持續改善 Agent

這是一套公開、可移植、跨專案的 AI 工程協作框架：**正式來源接續 → 專家分工 → 小步修正 → 回歸測試 → CI → 真實環境驗證 → 安全交付 → 故障回饋**。

## 一句話使用

> https://github.com/lily4318/reliable-system-builder-agent 幫我診斷網站部署失敗，先唯讀盤點，不要重送 POST。

請 AI 先讀 [START_HERE.md](START_HERE.md)、[AGENTS.md](AGENTS.md)、[release/current_release.yaml](release/current_release.yaml)。公開網址只授予**閱讀可能性**，不等於 AI 有任何 GitHub、GAS、Sheets、瀏覽器、部署或背景執行權限。

## 核心能力
- 七種專家 Agent：主管、架構、開發、DevOps/SRE、QA/UAT、安全、獨立學習評測。
- 開源可攜式入口：`START_HERE.md`、`AGENTS.md`、`.github/agents/`、`.agents/skills/`、`.claude/skills/`。
- 去識別化事故與回歸測試，可避免重複忽略已發生的失效模式。
- Python 標準函式庫的**安全政策評測**和 GitHub Actions 週期性唯讀 CI。
- 每次更新須有來源版本、差異、測試、完整回讀與人工核准；部署與正式收件另行控制。

## 本機驗證（不需付費模型 API）
```bash
python -m unittest discover -s tests -v
python -m src.agent_eval validate
python -m src.agent_eval evaluate --output output/evaluation-report.json
```

這是**公開安全規則引擎與案例回歸測試**，不是底層 LLM 權重訓練，也不是現場部署、UI 操作或模型的獨立盲測。

## 重要入口
- [架構](docs/ARCHITECTURE.md)、[事故處理](docs/INCIDENT_RECOVERY.md)、[評測與持續改進](docs/EVALUATION_AND_LEARNING.md)、[跨帳號整合](docs/INTEGRATION.md)
- [安全政策](SECURITY.md)及[當前版本](release/current_release.yaml)

**公開安全**：本儲存庫不得存放原專案的密鑰、OAuth、受試者資料、正式研究文件、私有程式碼或完整內部日誌。授權採 MIT，原專案資料仍各自保留權責。

## v0.1.0 獨立故障復原驗收（候選）
- [隔離復原案例與實際測試](docs/INDEPENDENT_ACCEPTANCE.md)：21 個合成／去識別化情境，與原政策引擎使用不同的評測路徑。
- [品質基準](evaluations/baselines/v0.1.0-initial.json)：歷史 CI 10 單元、22/22 政策案例、18/18 重要案例；未測得的指標記 null。
- [人工 Release／Rollback](docs/RELEASE_REVIEW_AND_ROLLBACK.md)：合格 CI 是必要條件，沒有真人審核不升正式版。
- [安全恢復與對帳](docs/INCIDENT_RECOVERY.md)：未知或部分 POST 只做唯讀盤點，禁止重新從頭部署。

上述評測無遠端 API 寫入；未證明真實 UAT、Agent 自動跨專案執行或底層模型已重新訓練。

## 持續改善與真實任務回饋（候選 PR）
- [實際工程任務標註、盲測資料隔離、品質比較](docs/FEEDBACK_AND_HOLDOUT.md)
- [人工標註依據](docs/FEEDBACK_LABELING_RUBRIC.md)
- [改善 PR、核准與版本回退](docs/FEEDBACK_PR_AND_ROLLBACK.md)
- `src/feedback_eval.py`：純離線結果標註 schema 驗證、預測品質指標、baseline 對比、保留測試 SHA 與 group 隔離檢查。
- `evaluations/feedback/synthetic-*.json`：**僅 36 筆合成回歸資料**，不代表真實工程成果。
- 真實人類標註和 sealed holdout **不得進入公開 GitHub**；目前沒有真實任務的人工標註樣本，也沒有真正 ML/DL 微調證據。

## 離線真實任務事件管線候選（依賴 PR #1）

新功能詳見 `docs/TASK_EVENT_INGESTION.md` 和 `docs/TASK_EVENT_INGESTION_DEPENDENCIES.md`，新增：

- `schemas/task-event-batch.schema.json`：安全工程事件結構。
- `schemas/task-ingest-authorization.schema.json`：操作者提供的用途、專案與操作白名單、來源 SHA 聲明。
- `schemas/pending-review-queue.schema.json`：永遠保持 `PENDING_HUMAN_REVIEW` 的標註佇列。
- `src/task_ingest.py`：只讀本機結構化 JSON，強制丟棄自由文字；有明確輸出路徑才建立獨立待審佇列。
- `evaluations/ingestion/`：不含真實工程資料的合成案例。

**此功能尚在相依的 PR #2，不能視為 main 正式能力，也不會自動讀取其他專案或真人資料。**
