# 多平台免費架站選型與雲端工程實戰｜TP-006/1

## 目的、範圍、證據層級
使用者 2026-11-15 明確採用 GitHub 共同工程基礎及四平台選型能力、實戰與驗收路徑；外部部署需另確認授權。此指南是候選技能擴充，**不含各帳戶的建置、任何部署或真人資料**。不改 WEB-EDITORIAL-01/v0.1 本機確認規格，不以雲端訓練取代 A07 fresh-dialogue gate。TD-001/002、原 scope/engineering_workflow/正式 release 機制維持。REPO_NATIVE，單 Agent 按角色工作。資料限公開合成、去識別工程證據。沒有實際帳號、算力或服務性能證據時不稱已掌握真部署。

## 1. 從規格到選型
以既有 13 題訪談及已確認需求 ID 為基準。只補問尚未確認的關鍵屬性；不能以猜測填 false/0。提取用途與公開性、原始碼可公開、網域、身分/角色、資料分類、持久資料、交易/一致性（none、同一受控 writer、SQL 約束、Postgres 專屬）、是否 Google 生態整合、SLA/閒置暫停要求、資料量與尖峰、現有帳戶及工具授權。以硬性不適用條件先排除，再比較成本與維護。至少兩個合理候選或明示唯一/無免費適配；供應商原生功能不等於身份、安全或授權。人工決策仍可改選；不以選型器的 preferred 覆蓋已確認規格。
- Pages + Actions：公開、靜態、非敏感交易、符合用途條款的網站。只發布白名單 artifact，不傳私稿、密鑰、DB 或備份；免費公開 source；project base path、HTTPS、自訂域成本、用量。沒有常駐後端/SQL，不能把 git commit 或 runner 檔案當多人交易 DB；用外部 API/DB 是另個架構，需核條款/CORS/identity。
- GAS + Sheets：Google 帶來真正 JS 後端及 /exec，私人 Sheets/Drive、Calendar/Docs/Gmail。只在符合交易需求且所有寫入者遵守同一 script lock 時用一工作簿 atomic batch；不能當 SQL 通用約束、跨 script/人工鎖或跨 Drive/Gmail transaction。Google identity 和部署者是兩件事，空 visitor email 拒絕，執行者不能當來訪者。native /exec 不承諾自訂域。
- Workers + Static Assets + D1：靜態可只用 assets；需動態才用 Worker API；需持久 SQL 才綁隔離 D1。D1 atomic batch 成功仍需確認條件命中，不能直接搬 sqlite3 互動式 BEGIN IMMEDIATE。10ms CPU 對登入 KDF/驗證/JSON 等需真實測量，不為配額降低安全。若要求 managed auth，原生組合不足，需額外身份方案；Postgres 專屬功能改選其他架構。確認一致性模式及 sessions、備份、限額。
- Supabase + 適用前端：Postgres/Auth/RLS/Storage，必要 Edge Functions。不是完整一般網站託管；前端另選（公開非商業且符合 Pages 條款可考慮 Pages；動態或敏感登入用適當的安全前端，例如 Workers assets/API，依架構決定）。所有 exposed schema tables 設 RLS/grants；瀏覽器不能用 service role/secret key；DB transaction/RPC、auth JWT、storage policies 各驗。免費可能 pause，不得用不當 keepalive 規避。DB logical dump 不含 object bytes，獨立保存/驗證 restore。free 沒有自動備份/PITR。
- Free 不代表 SLA 或安全合規。個資、敏感資料、研究和臨床須先獨立資料治理/合法基礎/機構/區域/保留政策與授權，本 selector 一律保留待審。要求保證 SLA 時不自動推薦免費。若沒有免費適合方案，提出縮減需求、延後或經使用者核准的成本比較，禁止自動升級。

## 2. 可執行的離線選型器
`python -m src.cloud_architecture_selection < profile.json`（PowerShell 可用 Get-Content -Raw profile.json | py -3 -m src.cloud_architecture_selection；UTF-8 input/output）。僅 stdin/stdout，不連網、無 secrets、無 DB/檔案/外部資源變更。輸入 exact 14 keys（5 enum +8 bool + estimates），未確定明填 null；未知/多餘/錯型別返回不合法或 NEEDS_REQUIREMENTS。例（已確認合成原規格的 SQL 需求情境；不是當前 production workload）：
```json
{
  "data_class":"public", "visibility":"public", "source_visibility":"public",
  "identity":"custom", "consistency":"sql",
  "commercial":false, "backend":true, "durable_data":true,
  "google_workspace_integration":false, "controlled_writers":true,
  "custom_domain":false, "no_inactivity_pause":false, "guaranteed_sla":false,
  "estimates":{}
}
```
data_class=public/internal_non_sensitive/personal/sensitive，按實際最敏感資料（包含私稿、帳號、日誌、備份）分類，勿只按公開頁。原合成稿件無真個資時可按 internal_non_sensitive；設 public 不等於已准許發布一切。visibility=public/restricted 表示網站入口，私人工作台另有 RBAC；source_visibility=public/private，identity=none/custom/managed（managed 指完整受管 application identity，不是可任意使用第三方登入）；consistency=none/single_writer/sql/postgres，sql 表示所需 SQL 約束與交易需另設驗收，非證明任何隔離等級。controlled_writers 指明所有修改遵守一個 script 寫入協定。google_workspace_integration=true 是需求有 Google 整合，非禁止外部平台串接。
估算 `estimates` 為 provider→metric→非負整數（以欄名單位及公開 ceiling，MB/GB 以十進位規劃，近似不取代 byte-level 計量）或 null；未提供是 unknown，不是零。使用尖峰和全部既有用量（account/project/user scope）而非只算新網站；不使用的服務才估0。GAS 採保守個人帳戶配額；Workspace 可重新比較，但不能隱含付費方案。名義 limits 在 src/cloud_architecture_selection.py，來源日期 2026-11-15。≥80% 警示 reserve，> ceiling 排除該候選（Pages 軟上限也保守處置）；80% 是本訓練建議，非供應商門檻。缺估算/接近限額影響排序，不會變成 PASS；Supabase 前端額度另算，所有其他未列 service quotas、CPU/load、mail、DNS、CI、account plan、retention 和實際成本仍須核對。所有輸出 external_write_permitted/deployment_permitted/paid_upgrade_permitted/actual_provider_verified/free_cost_guaranteed/formal_release_permitted 固定 false。輸入不能傳上述授權旗標。這是可審閱規則，不是自然語言模型能力評分、完整計費器、部署守門替代品或帳號驗證。公開來源會變，每次部署須更新核對。
`python -m unittest discover -s tests -p "test_cloud_architecture_selection.py" -v` 覆蓋靜態、商業/私有 source、Google 整合、SQL、非單 writer、custom domain、managed auth/Postgres、pause/SLA、敏感資料、unknown/malformed、limit-1/limit/limit+1、不同平台資源排序及 CLI duplicate/size/UTF-8。以合成 oracle 評測 deterministic selection，不代表真雲端。

## 3. 共用 CI/CD 及七道獨立雲端驗收門
| Gate | 完成證據（依順序） | 不得以此替代 |
|---|---|---|
| C0 | confirmed requirements、明確資料/維運/預算及 scope，選型 ADR | 外部寫入授權 |
| C1 | exact account/repo/script/project/worker/DB、plan/remaining quota、唯讀 tool permissions、成本限制；完整核對需人核時可編輯確認 | API schema 或 connector 存在 |
| C2 | candidate source、隔離本機/CI contract、security-review、migration/backup/rollback plan、同 SHA 綠燈 | 線上可用 |
| C3 | **另行明示外部部署授權**：提供具體資源、操作、受眾、合成資料、0額外費用不升級、有效期限、回退與清理範圍。先核真實授權和範圍 | 確認規格或 CLI preferred |
| C4 | provider immutable version 或 artifact/migration SHA、部署確切 ID/URL、遠端 readback、HTTPS 真頁面 | 只看到成功旗標 |
| C5 | 真遠端功能+負測、權限、競寫/未知結果對帳、quota/abuse、重部署保留資料、備份還原獨立目標、安全回退；靜態站不適用 DB 時記 N/A 理由 | 本機通過或 mock |
| C6 | 真使用者 UAT、formal launch approval、維護責任、監控、成本及資料保護核可 | 自動啟用服務或正式 Agent release |
C0–C2 可在候選 repo 先工作，C3 後才可外部寫入。C4/C5 任一步 UNKNOWN/PARTIAL 且非冪等先 READ_ONLY_RECONCILE（遠端 id/version/content/receipt）；不盲重送，不為 CI 方便放寬安全。部署前再次 pin Git head、provider resource id、舊版本、restore 路徑；不自動 merge、部署正式 main、升級方案或刪資源。原 src.engineering_workflow 的守門不變。
共通 GitHub：source commit/CI exact SHA、最小 job permissions、固定 Actions 版本（正式使用核安全）、不信任 PR 不給 deployment secrets、不對 fork PR 自動部署、獨立環境/approval（Free plan 實際支援需核）、使用 OIDC 若供應商支持，否則最小 scoped token 由使用者在安全 UI 建立；不收聊天密碼/token。自動部署流程與 actual trigger 需授權；workflow 不設定未授權 on:push 外部部署。遠端回讀對照 commit/deployment artifact, logs, schema, health; 版本回退不等於資料回退。

## 4. 四個不同驗收目標，避免重做已通過的本機網站
| 工作包 | 交付目標與訓練順序 | 真實線上驗收（全部待另行授權） |
|---|---|---|
| CLOUD-A | GitHub Pages：從既有公開合成網站/工程文件中挑**已可公開的**靜態資源，做最小發布 artifact；先驗 path、資源引用、白名單/secret scan、build。無真資料及 DB。先做最小平台可達性實戰，不再建另一個無關完整網站。 | GitHub Pages build/deploy job+artifact digest+URL；匿名 HTTPS 讀取、375/1280 對應頁面、無私檔與 secret、部署新版與回退舊 artifact（URL 可達，內容 SHA/marker），無原生 DB；條款/免費公開來源核對。 |
| CLOUD-B | GAS/Sheets：隔離合成編輯待辦工作流（非原現有研究系統），單一 writer、合成身份、版本欄/receipt/audit、RAW string、同一工作簿 batch；不把 SQL 全站降格成 Sheets。只實作有差異的交易/授權/部署。 | 核 scriptId/content/version/deploymentId、/exec URL，兩角色實測/匿名拒絕、Sheet 不公開、競寫/lock timeout、公式注入、atomic batch 注入失敗、失回應唯讀對帳，重新部署保留資料；複製新 workbook 核 restore；舊部署 version 相容回退。限制：人工/其他 script 不在鎖內。 |
| CLOUD-C | Workers/D1：以 WEB-EDITORIAL-01 凍結 v0.1 本機為基準，新雲端規格/adapter（不能直接 port sqlite 長交易）。保留 UI/需求/test contract、改 conditional mutation/public pointer/receipt/audit 原子 batch 或 trigger，安全 session/HTTPS、CPU+quota 設計。 | 另核 Worker version/binding D1/migration/HTTPS、部署 immutable SHA；R01–R13 受影響的遠端 A01–A06，實際並發 one success、rollback/after-commit dropped ACK、持久化及 restore 新 D1、schema-compatible Worker rollback。原本機測試已通過，雲端才測新邊界。 |
| CLOUD-D | Supabase：以同一合成文章/修訂資料契約驗證 Postgres/Auth/RLS，不重做共同 UI；加必要多角色細緻政策與跨表約束比較，明定前端架構。 | 實際 anon、兩 author、editor JWT 及直接 REST/RPC/storage 負測；RLS/grants 所有 exposed tables+RPC，service role never in client；transaction rollback/concurrency、migration/restore 隔離新 project（配額2，不能自行刪既有）、dump+objects、pause、front deploy URL/version/quota。真帳號測試僅合成。 |
| CLOUD-E | 由前四包真證據覆盤，用原 architecture/security/deployment/test/learning 技能更新。另一次新對話拿陌生需求做選型+關鍵小工程，不以公開固定例題冒充盲測。 | 各平台實際版本及 log/URL/讀寫/安全與回退證據、維護手冊，成功/失敗與適用限制；human review 確認可泛化再升格，獨立模型能力另評。 |
優先：CLOUD-A 若現有 GitHub 工具和 Pages scope 可用，以最短真 URL 訓練；不因其易部署而省略 CLOUD-B/C/D 的 DB/身份風險。若 Pages 需人或與原 repo 現有站衝突，先做各平台 C1 唯讀 capability/plan 檢查並推最可安全完成之路徑，不反覆要求同一操作。平台實作/指定外部 target 確認分開；不自行建立外部 repo、改現有 Pages、GAS/研究專案、Cloudflare/Supabase 帳號。

## 5. 部署能力與最少人工步驟（待確認）
- GitHub：現有 connector 可讀寫候選 repo/CI 證據；本輪名稱探索未見專用 Pages/environments/secrets/deployments 寫入端點，不推論沒有所有其他途徑。實際查 page state/current deploy source 及可用 API；必要人工 Repo → Settings → Pages → Build and deployment 選 GitHub Actions（先確認沒有現有站或另外確認目標）；Actions 頁核對 deployment URL，只有確認授權後操作。勿公開私人 repo 來求免費。
- GAS：Google Drive/Sheets 連接不等於 Apps Script API。名稱探索無專用 GAS deployment connector。經授權評估 Apps Script API/clasp 或 CI：核 Google 帳戶、scope、script/app deployment target；若需人工在 Apps Script Dashboard 設 API access、OAuth 或 Deploy → Manage deployments，給精確欄位和預期 /exec/version，再以真讀回核對。不要收任何 token 於聊天，不能移用現有研究/治療資料。
- Cloudflare：已有 docs/search/execute API 介面，實際帳號 scopes、免費 plan 和現有資源未查。取得 C1 讀取允許後核對帳號與 product plan；C3 另核資源名、Workers/D1/Secrets permissions 及寫入範圍；使用已支援的 connector 或適用 CLI（新案先查官方 cf CLI；舊 Wrangler 專案保留），不要為本輪安裝或設定外部 CLI。
- Supabase：本輪未見專用 connector；不宣稱具備管理 API 權限。C1 查可用 plugin/API/CLI、project plan/兩 project 配額、region、auth/RLS 與適用前端；必要使用者在 Supabase dashboard 建立安全 connection/最小權限，CI secret 透過 UI，避免 service key/PAT 在 Git。資源建立之前獨立授權。
使用者只負責必要帳號/OAuth/管理政策及確認；其餘有授權工具即由 Agent 執行。未驗證工具不要承諾代辦。C1 唯讀查核不需要建立資源。

## 6. 官方核對來源及更新規則
日期 2026-11-15：參考原 TP-006 [比較與官方連結](training/reviews/2026-11-15-online-deployment-options.md)，再讀：
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits ; https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- https://developers.google.com/apps-script/guides/services/quotas ; https://developers.google.com/apps-script/guides/web ; https://developers.google.com/apps-script/reference/base/session ; https://developers.google.com/apps-script/reference/lock/lock-service ; https://developers.google.com/workspace/sheets/api/limits
- https://developers.cloudflare.com/workers/platform/limits/ ; https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/ ; https://developers.cloudflare.com/d1/platform/pricing/ ; https://developers.cloudflare.com/d1/platform/limits/ ; https://developers.cloudflare.com/d1/worker-api/d1-database/ ; https://developers.cloudflare.com/d1/reference/faq/
- https://supabase.com/pricing ; https://supabase.com/docs/guides/database/postgres/row-level-security ; https://supabase.com/docs/guides/platform/backups ; https://supabase.com/docs/guides/deployment/going-into-prod
供應商文件為公共資訊，實際使用條款、帳戶、額度、計費、availability/security 要部署前當次重查。保留日期及變更原因，以原 selector/原技能/原主檔增量更新。


## 7. 已取得的離線驗收證據
- 2026-11-15 實際 selector 驗收補記：exact 047ca6340337d034842a6bd262ff1d2c80a5e56d / [CI 43711988622](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43711988622) job 132805354146 completed/success，raw 239471 chars，16 新測試方法全部 ok，450 tests in 51.738s，既有 EDITORIAL_BROWSER_PASS。先前434保留。涵蓋四平台選型、硬拒絕、limit-1/limit/limit+1、unknown、malformed、資源排序、CLI process、拒絕偽造外部授權等。原稿 80% 警戒是 advisory 工程假設；估算可由使用者提供但不證實實際供應商帳號/成本。文件整合 exact a59fbc00837e56c0fe14559b67fe6caeb6f44eb7 七份文件回讀 SHA 相符，CI 43712173888 尚未完成；最新回讀及 CI 待分開確認。選型規則已通過離線受控驗收，不宣稱四平台實際部署、安全或獨立模型能力。C0–C6 與 A–E 路徑皆為未來適用的實戰計畫，未有雲端 resource/URL。


## 8. C1 真實查核（2026-11-15）
NATIVE-CLOUD-017-C1-READONLY：實際 GitHub/Cloudflare/個人 Drive 唯讀與 Supabase app discovery，C1 PARTIAL，C3 NOT AUTHORIZED。Pages 尚未啟用、指定訓練分支未存在，建議 CLOUD-A artifact-only branch/docs；Cloudflare GET Workers/D1 0、缺 workers.dev、billing 403；GAS 專用 API 尚缺；Supabase app 可安裝未連接。詳 [C1 原證據與可編輯授權](training/reviews/2026-11-15-cloud-c1-readonly.md)。不能從工具 schema/metadata 推論外部寫入範圍。原 A07 仍 pending；真部署另確認。
