# NATIVE-CLOUD-017-C1-READONLY｜C1 真實唯讀查核與部署授權草案
日期：2026-11-15 Asia/Taipei。狀態：C1 PARTIAL VERIFIED；C3 NOT AUTHORIZED；無外部部署。本檔不保存私人 profile、account ID、email、token、私有項目資料或原始帳單。已確認原訓練方向 TD-001/002 + TP-006；C1 不取代其他 gate。
- 使用者明示要求 C1 四平台實際部署能力唯讀查核、選最短真實線上路徑、提供可編輯授權範圍、更新原主檔；未確認不得建立外部資源或部署。讀原 START_HERE、AGENTS、TD-001/002、TP-006、NATIVE-CLOUD-016、guide、deployment、policy/release；REPO_NATIVE/SINGLE_AGENT_ROLE_WORK。外部查核僅 GET/身份/工具探索，無讀無關私人文件/資料、無寫雲端、無建立 token、無啟用 Pages/worker/DB、無部署。僅本候選原訓練紀錄允許增量寫入。
- 基準 exact 822191bbc4fe1e5a98dbd748e87a6a935e698e08 / CI 43712279245 job 132806268195 completed/success，raw 239471 chars，450 tests in 51.133s，EDITORIAL_BROWSER_PASS。正式 main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57 未變，PR #8 draft。維持 A01–A06 本機、A07 fresh dialogue pending。
- GitHub：實際讀 repo metadata，原 repo ID 1455152922，public、not archived、default main、has_pages=false；API 回 repo permission flags admin/maintain/push/pull=true，不能推論 managed GitHub App 有 administration/Pages 權限。允許 repo/git/PR/CI 操作已驗，GET /actions/workflows 被 connector allowlist 明拒 (400 INVALID_ARGUMENT，非 GitHub 伺服器權限拒絕)，tree 只有 .github/workflows/agent-ci.yml（read-only evaluation，contents:read，無部署）。專用 Pages admin/deploy/dispatch 端點未見；不能代設 Pages，不能用原 CI 當部署。查候選發佈分支 cloud-a-pages-training 得 GitHub 404 Branch not found，當時不占用；仍需寫前再查。Git create_tree 可空 base 建 artifact-only tree，再 prepare commit/專用 branch（未執行）。GitHub 官方 public Pages 可免費，site≤1GB，100GB/月軟限，10次 build/hr 軟限（自訂 workflow 例外），10min timeout，符合非商業教育訓練。branch publishing 已知路徑而非保證 App push 觸發；需真部署 log/HTTPS/version。
- Cloudflare：連接身份查詢成功，GET accounts 成功且只1個 standard account（不公開個人 account id/email）；GET workers/scripts 成功回0，GET d1/database 成功且 total=0，兩服務可讀；GET workers/subdomain HTTP404 code10007 無 workers.dev，首次開 dashboard Workers & Pages 可能自動建立，**本輪未開、不指示未授權者先開**。GET subscriptions HTTP403 code10000，OAuth 不覆蓋該 endpoint，實際 plan/remaining usage/寫權仍 unknown；不可用讀權推論寫權，不為讀帳單要求廣泛 API token。已查官方 API schema：PUT subdomain、PUT Worker script、POST versions/deployments、POST D1 建庫等，皆未執行。Free 公共 limits：100k worker requests/day、10ms CPU、D1 10 DB/500MB each/5GB account、5M rows read/100k write per day；需使用者採 Billing/Subscriptions 檢視免費方案、不開 Workers & Pages 初始化或升級；若選 Cloudflare 再核費用、subdomain 命名和資源 scope。Workers 列表為一次回傳，不宣稱所有不可見資源不存在。
- GAS/Sheets：Google Drive 連接已安裝，現有個人 Drive profile 唯讀呼叫成功（僅查身份不查私人檔案）；Sheets metadata/range/batch/create 等工具 schema 存在，非 GAS OAuth/deployment 實證。工具與外掛目錄兩次探索未找到專用 Apps Script deploy 連接，不等於所有未列工具不存在。未查研究帳戶或舊 script；未指定新 scriptId/工作簿/帳戶，不能核實剩餘配額或 GAS API scope。官方 Apps Script API enablement 及 OAuth 獨立，個人 6min/execution、30/user、1000/script、200 versions、mail 100/day、trigger 90min/day；Workspace/實際餘量未確認。GAS API 不等同 Drive。後續選隔離帳戶並明確允許後評估 OAuth/clasp/CI；不收聊天 secrets、不自行啟用 API/建立 cloud project。
- Supabase：真正目錄查獲可安裝、尚未安裝/連接的 Supabase app（描述支援專案、SQL/schema、Auth、functions、migration/log）；已提出連接選項，未自動安裝或讀寫帳戶。官方 Free 2 active projects（owner/admin 組織合計、paused 不計）、500MB/project、50k MAU、5GB egress、5GB cached egress、1GB storage、1 week inactivity pause；實際 org/plan/project/權限未讀，不當作驗證成功。另需前端託管費用及 RLS/backup 等 C2。
- 方案排序（助手建議、非使用者已批准）：CLOUD-A Pages 優先為第一個最短可公開靜態 HTTPS 訓練，既有 public repo、不另建帳戶/DB，預計一次人工 Settings→Pages 設專用 branch/docs；以 artifact-only tree 白名單 index.html/style.css/app.js/.nojekyll（資料只公開合成）隔離主檔與程式、C2 exact artifact/CI 安全驗收，C3 另確認部署/發布 branch、公開受眾/0增量費用/指定操作與限期、v1→v2→前版內容新 commit 回退。**建立分支和公開啟用都尚未授權；先確認後做，不發假 URL**。如 Pages 設定/觸發受阻，不改 main、不強推、不盲重試；Cloudflare 已連接是動態+DB 的較短候選，待 free plan 與 subdomain 額外授權；Supabase 連接後再查 C1；GAS 仍缺安全 API 路徑。此不是完整 WEB-EDITORIAL-01 遠端驗收，Pages 不承擔原私稿/登入/交易。
- 詳 [本輪 C1 實查、差異和可編輯 C3 範圍](training/reviews/2026-11-15-cloud-c1-readonly.md)。C1 audit performed, per-platform PARTIAL，真正 C1 all gates 未通過；C3 未核准。保留所有權限、真資料、免費及正式 release 既有 gate；無新資源、測試部署、付費或跨專案讀寫。NEXT：使用者明確確認 CLOUD-A 隔離發佈及有限操作範圍後，候選 C2 artifact/測試/CI/精確 tree 回讀→重新確認資源未占用及免費→按已確認的 C3 操作；如需人工 Pages 設定，在 artifact 驗收後提供一步 UI、核對真結果。其餘平台的缺口並行用安全唯讀途徑查核、不阻擋可行工程。

## 實際查核矩陣
| 服務 | 已觀測 | 還缺 | 可行最少人工步驟（不立即執行） |
|---|---|---|---|
| GitHub Pages | 公開 repo、has_pages=false、原 CI 成功、候選發布 branch 未存在、Git write 可用；通用 GET allowlist 不含管理部分 | Pages 設定真正權限、專用 artifact、GitHub App 推送是否觸發發布、真網址/部署記錄 | C3 確認且 C2 artifact 完成後，到原 repo Settings → Pages → Build and deployment → Deploy from a branch → cloud-a-pages-training → /docs → Save；如現有 Pages 狀態改變則停止；保留 HTTPS、不可選 main/原 PR #8 或自訂域。Save 即可觸發公開上線，不是唯讀。 |
| Cloudflare | whoami + account list + Workers list + D1 list 成功；0 Workers 返回、0 D1 total；subdomain 404 code10007；billing HTTP403 | Free plan/remaining usage/write scopes 未核，帳號 subdomain 尚無；真正 API deployment、version/DB 也未測 | 只檢視帳戶 Billing/Subscriptions 或當前計費頁，回報 Workers 方案及是否有額外收費、無需分享憑證；不要先進 Workers & Pages（可能初始化子網域），此與子網域命名/建立待另一份確認。 |
| GAS/Sheets | Drive profile 呼叫成功；Sheets 操作工具 schema 可見 | 指定合成帳戶/新 script 及 OAuth、更動部署的 API 連接，實際 quota 未核 | 將來先選獨立 Google 帳戶及隔離 script/工作簿；若需 Apps Script API，先查 script.google.com/home/usersettings 狀態及適用 API/OAuth 途徑。啟用 API access 為帳戶層設定，另要授權，不將 Drive 權限當成 GAS deploy。 |
| Supabase | 專用 app 目錄發現，未安裝；官方 free 定額已重新核對 | 連線/帳號、組織計費、剩餘專案及 scopes、前端託管 | 使用者可安裝並連接 Supabase app，本輪不要求立即；連接後先讀 metadata/plan，不開 SQL 或新 project。 |
現有工具限制不能繞過。僅 GitHub 原候選訓練文件寫入；外部權限 C3 不因文件寫入而成立。

## 優先 CLOUD-A 的實際發佈設計（PROPOSED）
- 目標：一個公開、非商業、無資料收集的合成刊物/工程訓練展示站（沿用已可公開的「紙上」概念與合成公開展示，**不是**原文章管理網站的完整上線）。不公開整份工作目錄或 DB。將 Pages 文件限制在全新專用 tree 的 docs/ 之下：優先 docs/index.html、docs/style.css、docs/app.js（必要才有）、docs/.nojekyll，另可用明確合成 JSON fixture（先列白名單，再核安全）；不含原 repo 文檔或程式、帳號、私稿、憑證、表單、外部 tracking/交易，頁面標明「合成訓練展示，非正式服務」，相對路徑兼容 project base path。
- C2：在原候選分支先開發並測試 artifact（非部署），測相對路徑與 mobile/desktop、鍵盤、公開內容白名單、無敏感檔/secret/外連/個資；exact SHA CI 與 artifact hash/manifest 都通過，再建獨立 publication tree（base_tree_sha=null，從核准內容重建，核 tree 及 SHA，parent pinned，但 branch snapshot 只含允許發布文件）。不將候選全部 docs 作發布內容。新檔寫入僅限確認的範圍。
- C3：使用者另行確認可編輯範圍後，pin 新 source SHA、核 repo immutable id/visibility/has_pages=false、branch still absent；如不符停下唯讀對帳。只在既有 repo 建新 branch cloud-a-pages-training 指向核准 artifact commit；不改 main、不 force push、不改既有 CI permissions、不設 Actions dispatch 未授權 workflow、不另建 repo。人工 Settings→Pages 選分支/docs Save 為真正啟用，前置必須 C2 PASS 和 C3 核准。若 GitHub App push 未觸發布或 connector 無法讀 Pages deployment metadata，核 Actions log 和實際匿名 URL；有必要才引導使用者查看 Pages URL/狀態或一次安全人工觸發，禁止盲改設定。
- C4/C5：觀測真實公開 URL（預計 GitHub project site, 非既有或已部署的 URL）、HTTPS、實際 HTTP/DOM 與 source marker、部署 run/job、artifact bytes；v1→v2→restore v1 artifact via new commit（最多3次發佈，各次先核前版及 source，無 force），驗證同 URL 及恢復的內容/資源。不得把既有 local CI 代替線上證據。No DB/auth/transaction N/A；原 editorial 仍本機合成已驗，完整動態雲端網站另行確認。CI/部署工具不能查時需明確限制，不宣稱 remote PASS。
- 規劃預算新增 NT$0，使用 GitHub Free 公開 Pages、標準 runner、預設 github.io，不買自訂域；預計 artifact <1MB、有限驗收請求、不壓測及不收集資料、3次發布嘗試上限；不保證實際流量/額度，部署前核免費適用及標準 runner、發現可能費用即停止。授權期限建議確認後7日，並非站點自動下架；測試結束保留 v1 公開測試頁，向使用者回報，後續下架或改 Pages source 另經確認。正式啟用、外部專案、付費及真人資料全不允許。
- 請使用者可編輯確認的範圍：我確認 CLOUD-A 為原 repo 非商業公開合成靜態訓練，不是正式 Agent release 或 WEB-EDITORIAL-01 完整發布。允許候選 PR #8 製作/測試只含上述公開資料的靜態 artifact，C2 通過後僅建立 cloud-a-pages-training 分支、發布 docs 白名單及測試 v1/v2/還原 v1 的新提交（共不超過3次發布）；允許且僅允許此 repo Pages 的 branch/docs 啟用（如無服務端工具，由我在收到 C2 PASS/精確 commit 後自行依指示 Save），使用預設 github.io、0新增費用、不買域、不改 main/Release/其他專案、無個資/後端/DB/祕密、無自動推送/自動升級。允許實際匿名 HTTPS 功能/安全/回退及部署記錄回讀；確認後7日限期，結束回報，保留 v1 測試頁；下架/其他部署另確認。任何 target drift、Pages 已啟用、額度/費用或權限不明、部分寫入先唯讀查核並停，不盲重試。此文字尚未獲確認，不是授權。

## 官方資料（2026-11-15 復查）
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/workers/platform/pricing/
- https://developers.cloudflare.com/d1/platform/limits/
- https://developers.cloudflare.com/d1/platform/pricing/
- https://developers.cloudflare.com/workers/configuration/routing/workers-dev/
- https://developers.google.com/apps-script/api/how-tos/enable
- https://developers.google.com/apps-script/guides/services/quotas
- https://supabase.com/pricing
- https://supabase.com/docs/guides/platform/billing-on-supabase
官方免費 plan 是公共資訊，非個人帳戶/剩餘用量或寫授權。選擇 Pages 是本輪最短訓練 URL 的具體建議；需要真正登入/持久化資料則不可選 Pages 單獨交付。


## Supabase 連接後實際補查（2026-11-15；最新狀態取代前述未連接欄位）
- 使用者完成 Supabase 連接，沿原本 C1 唯讀授權接續；前次「未連接」為歷史狀態，現已解除。讀 Supabase skill、原主檔、決策與 C1 review。實際 list_organizations 回一組可見組織、list_projects 回空清單，get_organization 回 plan=free / tier=tier_free；不保存私人組織 ID、名稱/email 或身份資訊。僅證實當前連接的可見組織與專案資源，非所有不可見帳號/組織的用量保證。
- Supabase 官方 docs connector 查得 billing-on-supabase、free-project-pausing：Free 提供 owner/admin 所屬組織合計兩個免費專案，paused 不計；500MB DB/project、50000 MAU、1GB storage、5GB egress、500000 Edge Function invocations（多項配額按組織合計）；低活動7日可能暫停，暫停後 dashboard 可於90日內恢復。當次套餐確認成功，但組織角色、真正剩餘配額、建立專案的專案特定價格與寫入 scopes 未驗；不可保證零費用。專案報價需先由使用者選定組織，未呼叫 get_cost、confirm_cost 或 create_project。可在另行授權後核報價、選定區域/隔離新專案、驗 migrations/RLS/Auth/RPC/Edge Functions 及遠端 URL；前端仍需適當託管；禁止使用真人/敏感資料、付費、既有項目或未授權外部寫入。沒有執行 SQL、建庫、建立 branch、部署或讀取個人資料表。
- 原 C1 文件 exact 6274f0cae29d2a71d12c15cb4ef67a97c60b2351 / CI 43712836552 job 132807956654 completed/success，raw 239471 chars，450 tests in 48.013s，EDITORIAL_BROWSER_PASS。原 C1 Pages-first 建議不因 Supabase 連接逕自取代；但 CLOUD-D 現可直接唯讀查核且具實際管理介面，列為可行的 SQL/Auth 進階訓練候選。C1 PARTIAL_VERIFIED，C3 NOT_AUTHORIZED；保留原 A07 fresh dialogue pending。沒有新增免費資源或部署，不寫正式 main。

官方：[帳務方案](https://supabase.com/docs/guides/platform/billing-on-supabase)、[免費專案暫停](https://supabase.com/docs/guides/platform/free-project-pausing)。