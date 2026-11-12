# 工程任務事件資料管線｜離線唯讀匯入、證據 SHA、人工標註佇列

**候選 PR #2**，建立在尚未合併的 PR #1 上。此工具沒有網路、GitHub、GAS、Google Sheets、資料庫連接器，也不會自動取得私人研究資料。它僅能讀取操作者指定的**本機 JSON**，將安全欄位轉成**未審核的待辦佇列**。不會把原始事件的成功結果當成已核准的真實任務成功。

## 1. 相依性與責任分工

- PR #1（`feat/evidence-feedback-holdout-v01`）提供 `src/feedback_eval.py` 的 `case_id`、`group_id`、`reviewer_id` 與人類標註契約。
- PR #2（`feat/offline-task-event-ingestion-v01`）新增 `src/task_ingest.py`、`schemas/`、`evaluations/ingestion/` 及對應測試。**PR #2 的 base 是 PR #1 分支，不是 main。**
- 任何 `PENDING_HUMAN_REVIEW` 必須由人類查看原始證據、確認授權及標註後，才能在另一個受控管線中升為 `reviewed_real`；本匯入器不能自行核准。
- PR #1 尚未合併前，不得將 PR #2 直接指向 main 並宣稱兩者可獨立使用。等 PR #1 合併且回讀 main 後，才能重新確認 PR #2 base 與差異再安排審核。

## 2. 資料契約

`schemas/task-event-batch.schema.json` 是結構化事件契約，允許 1–250 筆事件，每筆只包含固定的 `event_id`、`case_id`、`group_id`、`project_id`、安全枚舉類別、UTC 時間、來源 commit SHA、證據 SHA-256、HTTP 狀態與布林授權資訊。

`schemas/task-ingest-authorization.schema.json` 是**操作者提供的授權聲明**，必須指定用途 `engineering_task_feedback`、範圍、到期時間、操作／專案白名單、操作者確認與來源檔 SHA。真實資料匯入時必須使用 `reviewed_real`、有效 reviewer 代碼及**符合來源原始位元組**的 SHA-256；授權檔、事件與佇列都必須在公開 Repo 以外。

`schemas/pending-review-queue.schema.json` 定義待標註佇列：每個 case 包含安全的事件時間線（時間、API 操作類型、結果、HTTP 狀態、SHA、證據類型）、`PENDING_HUMAN_REVIEW`、`outcome=unknown`、`verified=false`。自由文字 `note` **整欄丟棄**，不嘗試只用 regex 猜測個資是否已洗乾淨。未列入 allowlist 的 `raw_log`、`url`、`email`、`payload` 等欄位直接拒絕。

**授權聲明只證明當次操作者提供了符合格式的聲明，不是機器可獨立證明的法律／機構核准。** 真正使用前應由資料權責人確認來源、合法用途、保存及刪除政策；原始證據檔和映射索引留在原正式來源／受控儲存。

## 3. 可執行的公開合成案例

```bash
# 零寫入：只驗證授權、資料 schema、SHA 與所有操作白名單
python -m src.task_ingest validate --scope synthetic --input evaluations/ingestion/synthetic-events.json --authorization evaluations/ingestion/synthetic-authorization.json

# 零寫入：顯示安全摘要，不顯示原始 note 或事件 payload
python -m src.task_ingest preview --scope synthetic --input evaluations/ingestion/synthetic-events.json --authorization evaluations/ingestion/synthetic-authorization.json

# 明確指定新輸出才建立待審佇列；拒絕覆寫已存在檔案
python -m src.task_ingest prepare --scope synthetic --input evaluations/ingestion/synthetic-events.json --authorization evaluations/ingestion/synthetic-authorization.json --output output/synthetic-review-queue.json
```

上述輸入是合成，不能用於推定真實工程成功率；公開 CI 只執行 synthetic `validate`／`preview`，不產出真實資料。

## 4. 封閉環境中的真實事件匯入（僅是未來操作說明，本輪未執行）

1. 資料權責人先在受控環境將正式來源整理為**符合上述 allowlist 的結構化 JSON**，不可直接提供原始日誌。將事件和授權聲明存放於公開 Repository 之外，限制存取並建立版本紀錄。
2. 資料權責人檢查 `source_sha256` 是否等於待匯入事件檔的完整原始位元組 SHA，核對 `allowed_projects`、`allowed_operations`、人類授權及到期時間。
3. 在授權的離線電腦上執行以下命令，先只讀 `validate`／`preview`，再經人工確認才可 `prepare`：

```bash
python -m src.task_ingest validate --scope reviewed_real --input ../private-agent-evidence/structured-events.json --authorization ../private-agent-evidence/authorization.json
python -m src.task_ingest prepare --scope reviewed_real --input ../private-agent-evidence/structured-events.json --authorization ../private-agent-evidence/authorization.json --output ../private-agent-evidence/pending-review.json
```

4. `prepare` 不修改來源或已有佇列；只在操作者明確指定**尚不存在的檔案**時建立 mode 0600 的新佇列。佇列仍為**未核准**，不能視為成功標籤或真實 UAT。
5. 對某個原始證據檔，可由有權存取的操作者於本機呼叫 `verify_evidence_bytes(evidence_path, expected_sha256, approved_root)` 進行 chunked SHA-256 比對；只返回比對結果和位元組數，不複製原始證據。**雜湊相符不等於能證明原始證據真實、時間順序或來源合法**。

## 5. 安全與完工門檻

- **Default deny**：授權缺失／過期、專案或操作不在白名單、SHA 不一致、來源超過大小限制、未知欄位、跨事件 case 身分衝突、重複 event ID、symlink 等情況都拒絕。
- **No data exfiltration**：沒有 HTTP 連線、外部 API、秘密或自動背景收集；`source_was_modified=false`，只存固定結構欄位與 SHA。
- **No false completion**：建立佇列永遠 `verified=false`、`outcome=unknown`、`human_review_required=true`。
- **Queue is not a database**：目前是單次批次檔，沒有任務派送、交易鎖、多人競寫或標註 UI；這些屬未來私人資料系統獨立核准的工作。
- **No direct main**：PR #2 的程式需通過新增合成測試與現有 `verify` CI，且須人工審查 PR #1 和 PR #2 的相依性才可考慮合併。
