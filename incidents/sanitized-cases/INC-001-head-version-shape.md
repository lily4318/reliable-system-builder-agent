# INC-001-head-version-shape｜HEAD 開發部署與固定版本部署混淆
- 資料類型：observed-pattern（去識別化、公開通用情境）
- 症狀：自動開發部署 ID 不是 HEAD 字面值，且版號可省略。
- 安全處置：按版本欄位與 API 規範解析並守住唯一 HEAD、來源與 ACL。
- 禁止事項：不放寬公開權限或略過 32 檔 SHA。
- 評測入口：evaluations/cases/regressions.json
- 判準：須於個別專案再次取得真實來源與遠端證據；本案例本身不是生產修復驗收。
