# 安全政策

**此 Repository 為公開資料。** 禁止於 issue、PR、incident、測試或 CI 報告揭露 OAuth refresh token、client secret、個資、電子同意、原專案內部資料表、可回復秘密的備份、私人部署網址或完整敏感日誌。

- 如有漏洞，請使用可用的 GitHub 私密回報方式；不要把漏洞證據與秘密直接發佈在公開 Issue。
- 若憑證曾洩漏，需由原權責人輪替並調查，僅刪掉公開文字不足以恢復安全。
- 本公開工具預設唯讀，不授予外部 Repository、Apps Script、Google Sheets 任何隱含寫入權限。
- POST 不明結果需停下唯讀對帳；正式資料、部署及收件須各自授權。
- 本 repo 的 CI 不讀外部專案的 OAuth Secret，也不呼叫其部署 API。
