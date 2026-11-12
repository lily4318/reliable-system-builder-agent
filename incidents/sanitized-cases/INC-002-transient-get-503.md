# INC-002-transient-get-503｜GET 503／429 暫時性故障
- 資料類型：observed-pattern（去識別化、公開通用情境）
- 症狀：唯讀列版本或部署時發生服務不可用。
- 安全處置：GET 使用有限退避、敏感資訊遮蔽與失敗關閉。
- 禁止事項：不可推論 POST 可以安全重送。
- 評測入口：evaluations/cases/regressions.json
- 判準：須於個別專案再次取得真實來源與遠端證據；本案例本身不是生產修復驗收。
