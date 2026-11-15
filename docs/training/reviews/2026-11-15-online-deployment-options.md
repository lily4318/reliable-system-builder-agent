# TP-006｜免費雲端部署能力比較（2026-11-15）
狀態 DISCUSSION / PROPOSED。使用者長期目標為直接協助線上部署，不限於本機 ZIP；供應商選擇、開工、雲端寫入與正式上線尚未授權。原 WEB-EDITORIAL-01/v0.1 合成 localhost 工程保存為已驗收基準，A07 獨立新對話仍 pending。基準 cadf390f2c43d7dee9e66882f5fe440ea437cccf / CI 43709560256 job 132797945225 434/434。

## 官方方案核對
| 方案 | 免費資源與限制 | 適用與風險 |
|---|---|---|
| Cloudflare Workers + Static Assets + D1 | Workers 100,000 requests/day、10ms CPU/invocation；純靜態資源免費不限量；D1 500MB/database、10 DB、5GB/account、5M rows read/day、100k rows written/day、7日 Time Travel | 推薦第一個合成 staging；超額拒絕，需核資源、帳號、查詢、加密與限額；不是原 sqlite3 長交易或任意 production SLA |
| Cloudflare + Supabase | PostgreSQL 500MB/project、2 active projects、50k MAU、1GB object storage、5GB egress；閒置一週可能暫停，free 無 automatic backups/PITR | 複雜關聯/身份與 RLS；須驗 policies/key isolation、TLS、備份、暫停及 quota |
| GAS/Sheets | Google 帳號服務、Web Apps；6min/execution 等配額，dependent services quotas | 行政/Workspace 整合；Sheets 非通用關聯交易 DB，合理使用權及個資獨立審查 |
| Vercel Hobby | 免費個人專案，quota/用途條款 | 前端/函式搭外部 DB；不能假設商業用途免費 |
| Render Free | 15min idle spin-down，本地 FS ephemeral；免費 PG 1GB、30日到期、無備份；注意 bandwidth billing | 不選長期免費 DB，不能將 SQLite 放臨時磁碟 |
| GitHub Pages | 靜態，無原生 DB/後端，商業/SaaS/敏感交易限制 | 文件與公開展示，不作通用全端 |

官方來源（2026-11-15 查核）：
- https://developers.cloudflare.com/workers/platform/limits/ ; https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/ ; https://developers.cloudflare.com/pages/ （新案 Workers）
- https://developers.cloudflare.com/d1/platform/limits/ ; https://developers.cloudflare.com/d1/platform/pricing/ ; https://developers.cloudflare.com/d1/reference/faq/ ; https://developers.cloudflare.com/d1/worker-api/d1-database/ （batch 原子性，不能直接以 sqlite3 BEGIN IMMEDIATE/交互查詢搬移）
- https://developers.cloudflare.com/turnstile/plans/ （free 防機器人方案，不取代身份/ACL）
- https://supabase.com/pricing ; https://supabase.com/docs/guides/security/production-checklist
- https://developers.google.com/apps-script/guides/services/quotas ; https://vercel.com/docs/plans/hobby ; https://render.com/docs/free ; https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
額度會變；部署前必須重新核對個人帳戶實際 plan/配額/超額策略與費用，不能承諾永遠免費。

## 候選工程方向（非實作授權）
1. 首選 GitHub→Cloudflare Workers/Static Assets→D1。可沿用既有 editorial HTML/CSS/需求、fixtures、contract；新 TS/JS Worker/SQL adapter 需設雲端版本，原 Python 受控版不刪。比較 D1 conditional atomic batch/trigger 等與 Postgres transaction；測試 expected revision、owner/role、public pointer/audit/receipt 同交易，zero rows affected 不能誤當成功；斷線後依 actor receipt 唯讀核對，實際雲端 concurrency、回退及新 DB migration/restore。Workers 10ms CPU 下密碼雜湊等必須重估，不能降低安全成本來符合額度；選成熟身份服務或受控身份方案而非照搬本機憑證。
2. 安全最低門檻：隔離 staging DB/worker、合成資料、HTTPS、Secure/HttpOnly/SameSite cookie、精確 Origin/CSRF、server ACL、輸入驗證、索引/大小 cap、rate/abuse protection、no secrets in repo/log/chat、最小 API 權限、MFA、日誌去敏、備份/restore、quota hard stop。若用 Supabase，RLS 與角色政策、服務端密鑰隔離、備份與基礎設施責任另驗。資料分類及跨境/機構要求獨立審查；真臨床/研究資料不因免費或大品牌而符合要求。
3. 工具：已查 Cloudflare connector docs/search/execute 規格與官方 docs；帳號身份、權限、現有資源/plan 尚未確認。取得讀取及建立 staging 授權後才核 account/plan/resource IDs。實際部署工具用授權 connector 或 GitHub workflow secret/平台管理台，必要由使用者一次性 OAuth/最窄 token 設定；不得索取 secret 於聊天。禁止 auto-merge、正式發布、改其他專案或付費升級。
4. 完成門檻擬定：實際 HTTPS staging URL、部署 version/source SHA/DB ID（不公開私人識別）、遠端 schema、從匿名和授權測試帳號實測 R01–R13 受影響的功能；read-only receipt/並發拒絕、redeploy 後持久化、備份還原到新隔離 DB、舊版相容回退、CI 與 remote readback、0額外費用/配額策略、真人 UAT 限制；與既有 A01–A06 的本機證據分開，A07 獨立新對話不以此替代。正式啟用另審。不得把只寫 GitHub、配置檔或本機測試視為雲端部署完成。


## GitHub 自身部署能力補記（2026-11-15）

- 使用者提問「github也能部署網站，為什麼你沒有推薦?」；原比較有列 Pages，但偏重全端同源架構，未充分說明已可用 GitHub 為靜態站首選之一及 CI/CD 核心。不是使用者已確認選型或授權實際 Pages/Actions 部署。
- 官方查核：https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages 、https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits 、https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site 、https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https 、https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job 、https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments 。Pages 免費方案公開 repo，可直接發布 HTML/CSS/JS 及建置後 React/Vue，HTTPS，1GB published site、100GB/month soft bandwidth、10 builds/hour soft（自訂 Actions workflow 例外）；非 Python/Node 常駐後端或持久 SQL，禁止商業交易/SaaS 等用途及不宜敏感交易/傳密碼，私人 repo 不等於私人 Pages。公開 repo 標準 GitHub-hosted runner 免費但每 job 臨時環境，非長期網站或資料庫。
- 建議分層：A GitHub Pages + Actions 適公開非交易文件/作品集/教育展示、可生成靜態公開文章（僅允許公開內容，不把草稿/私密資料打包）；B Pages + 外部 API/DB 技術可行，須用途符合 Pages 條款、公開前端不放 secrets、精確 CORS/權限；涉及帳密/業務後台改在適合的同源服務/獨立登入服務，不能靠 Pages 儲存敏感交易。C GitHub + Workers/Static Assets + D1 或 Supabase 適完整動態網站；GitHub Actions 做授權 CI/CD，環境 approval、scope secrets/OIDC、版控、遠端部署回讀、回退。GitHub 是否可實際啟用 Pages、配置 secrets/environment 或觸發部署仍須核 connector 權限、目標 repo 與獨立授權；不靠 Actions 把 SQLite/JSON commit 當多人 DB。
- WEB-EDITORIAL-01 有角色登入、私稿、審核、版本及交易，Pages 單獨不能滿足；可評估 Pages 公開刊物＋獨立安全後台 vs GitHub+同源 Worker。若採分離架構，靜態發布延遲及下架立即不可見的既有需求衝突需先驗證或重新取得規格確認；不自動改規格。依需求選最簡單適用方案，不強制所有站 Cloudflare。
- 原 head 81510fd3e8514190cd2ce9d033a7298f37a9d2ff / CI 43709938018 job 132799097402 completed/success, raw 236518 chars, 434 tests in 44.691s、EDITORIAL_BROWSER_PASS；保留 A01–A06、A07 FRESH_DIALOGUE_PENDING。原 TP-006 review 補充比較，未改程式、正式 main、Release、雲端帳號/資源或部署。方案待確認。


## GAS＋Sheets 原生全端部署補記（2026-11-15）

- 使用者詢問「那GAS + Sheets呢?」；建議將 GitHub + GAS Web App + 私有 Sheets 列為與 Pages、Workers/D1、Supabase 並列的優先選型，而非一律先用 Cloudflare。GAS 可直接託管 HTML Service、執行後端 JS、透過 google.script.run/doGet/doPost 提供功能，原生整合 Drive/Gmail/Calendar/Docs。適合受控低流量行政、報表、文件、一般報名與預約；不能僅因免費宣稱合規或適用所有交易/高流量系統。現有研究或臨床系統不在本輪讀寫授權。
- 官方來源 2026-11-15：https://developers.google.com/apps-script/guides/web 、https://developers.google.com/apps-script/guides/services/quotas 、https://developers.google.com/apps-script/concepts/deployments 、https://developers.google.com/apps-script/manifest/web-app-api-executable 、https://developers.google.com/apps-script/reference/base/session 、https://developers.google.com/apps-script/reference/lock/lock-service 、https://developers.google.com/workspace/sheets/api/guides/batch 、https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/batchUpdate 、https://developers.google.com/workspace/sheets/api/limits 、https://developers.google.com/apps-script/api/reference/rest 。個人/Workspace 每次6min、30 simultaneous/user、1000/script、200 versions；個人 vs Workspace 每日郵件收件者100/1500、trigger runtime90min/6hr、URL Fetch20k/100k。限額非併發 SLA，執行身分及關聯服務配額另核；Workspace 本身未必免費。
- 架構：GitHub 為 source，GAS 為前後端，私有 Sheets 為資料、Drive 為附件備份、按需 Gmail/Calendar/Docs；公開前端不直連私庫，不公開工作簿。資料 ID/版本、伺服器驗證 actor/role/ownership、每個可呼叫函式授權、拒絕未知身分；execute-as-deployer 不等於來訪者身分，Session.getActiveUser().getEmail() 可空白；外部匿名及管理端分隔、管理端限定適當已驗證身份。資料分類、最小 scope、機構政策、跨境與真人資料另審。
- 交易工程：同一 script 的 getScriptLock + lock 內回讀/expected version/actor-token-payload receipt、單次 Sheets API batchUpdate 原子寫入同一工作簿；不宣稱跨 script、人工修改、跨工作簿/Drive/Gmail 等交易隔離，document lock 在 Web App 可能 null。控制唯一 writer 或明確外部寫入契約，禁止盲重送不明 POST，讀原 actor receipt、對帳、處理逾時與未觀測結果；防公式注入（RAW 或明確 stringValue）、批次讀寫、保護原資料、備份與 restore 到獨立工作簿、quota/abuse gate。對需要嚴格併發、DB 約束、複雜 join、RLS 或大量交易的系統優先評估 SQL。
- 部署：Apps Script API 可 getContent/updateContent、versions.create、deployments get/list/update/create；或經授權 clasp / GitHub Actions。先確認 scriptId、spreadsheetId、部署者/訪客身份、版本、OAuth scope 與帳號政策；完整檔案更新前備份及讀回，immutable version → 更新既有 deploymentId（維持 /exec URL）→ 實際網站與資料驗收；/dev 非正式使用。正式回退到舊 version 不回退資料本身，先驗相容性。可用工具名稱查核未見專用 Apps Script API/部署 connector，不能把 Google Drive/Sheets 權限當成 GAS 更新/發布授權；實際 OAuth/部署途徑未驗收，需要個別授權與能力查核。
- 原 head 64fccdec341595c2ca3d2cd478feaa29eaeb2004 / CI 43711227932 job 132802997034 completed/success，raw 236523 chars、434 tests in 49.896s、EDITORIAL_BROWSER_PASS；A01–A06 受控驗收及 A07 FRESH_DIALOGUE_PENDING 保留，未重跑原測試或改程式。新增 GAS 比較屬 TP-006 建議，不更改主線或自動啟用雲端服務。下一階段建議以適用性、可操作授權、免費限額、身分及資料邊界判斷平台；先設計合成獨立 staging 規格、使用者確認後才建立資源與真 /exec 驗收。


## 使用者確認多平台能力方向
本輪採用四平台選型能力與訓練路徑；原歷史方案保留。候選選型器與 [統一選型及實戰驗收指南](../../CLOUD_ARCHITECTURE_SELECTION.md) 為新的執行入口。NATIVE-CLOUD-016-STACK-SELECTION；外部資源/部署另授權；非真雲端驗收，A07 仍 pending。
