# 故障診斷與部分寫入復原 Runbook

1. **停止盲重試**：遇 POST timeout、HTTP 503、部分建立版本，先阻擋新寫入。
2. 記下最後實際成功的 API、Git SHA、部署／版本權責及時間；不得把秘密寫入公開 repo。
3. **唯讀對帳**：GET 現有版本、部署、內容 SHA、ACL 和原 HEAD，與寫前基準比較。
4. 區分 `NO_WRITE`、`PARTIAL_VERSION_ONLY`、`DEPLOYED_BUT_VERIFY_FAILED`、`UNKNOWN`。
5. 若已建立不可變版本但尚未部署，不可從頭重建版本；重新核對遠端清單與版本內容。
6. GET 429／503 可有限退避；POST 不因相同 HTTP 狀態就自動重送。
7. 任何寫入恢復須重新取得原專案授權、最新 inventory SHA 與並行競寫核對。
8. CI 通過不代表真實 UI 可用；部署、正式個資、電子同意及收件許可各自驗證。

抽象化案例放 incidents/sanitized-cases；原始私有事故證據留在原專案。
