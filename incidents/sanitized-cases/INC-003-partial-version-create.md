# INC-003-partial-version-create｜部分成功：已建版本但未部署
- 資料類型：observed-pattern（去識別化、公開通用情境）
- 症狀：建立版本回應及內容回讀成功，清單驗證不一致，部署仍未 POST。
- 安全處置：停止新版本建立，僅 GET 對帳並確認當前版本與部署。
- 禁止事項：不因 workflow failure 就自動重跑整條部署流程。
- 評測入口：evaluations/cases/regressions.json
- 判準：須於個別專案再次取得真實來源與遠端證據；本案例本身不是生產修復驗收。
