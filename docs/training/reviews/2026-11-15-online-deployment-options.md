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
