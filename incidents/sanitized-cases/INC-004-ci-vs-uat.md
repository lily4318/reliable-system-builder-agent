# INC-004-ci-vs-uat｜CI 成功但 UI 未驗收
- 資料類型：synthetic-regression（去識別化、公開通用情境）
- 症狀：CI、模擬與靜態測試成功，但沒有指定部署的實際 UI 操作。
- 安全處置：維持 UI_VERIFIED=false，另行執行真實驗收。
- 禁止事項：不能把合成測試或部署網址冒充正式可營運。
- 評測入口：evaluations/cases/regressions.json
- 判準：須於個別專案再次取得真實來源與遠端證據；本案例本身不是生產修復驗收。
