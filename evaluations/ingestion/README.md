# 公開合成事件匯入測試

這裡的事件、授權與所有 SHA 均為 **synthetic fixture**，沒有連結真實專案、真實使用者、私人日誌或授權。

`synthetic-events.json` 用於測試多個事件彙整到同一個 case；`note` 是故意提供的自由文字欄位，匯入器**不會將它複製到輸出**，也不會把事件結果標成已確認的成功。

使用 `python -m src.task_ingest validate --scope synthetic --input evaluations/ingestion/synthetic-events.json --authorization evaluations/ingestion/synthetic-authorization.json` 進行零寫入驗證。

本公開資料無法證明任何真實任務成果，也不代表私人資料匯入已授權。
