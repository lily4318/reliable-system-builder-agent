---
name: security-review
description: "檢查權限、隱私及安全。security 角色；交付 security-review。"
---
# security-review｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：architecture。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
核對資料分類、最小權限、威脅情境及故障邊界；以具體測試及修復建議交 Developer、SRE。僅要求必要的安全驗證；不把安全檢查擴成主要開發工作。

### GitHub 專案身分與授權（EP-09 / EP-10）
以正式 repo 及實際唯讀 API 證據核對資源身分，區分名稱表示、不可變資源 ID、來源版本與操作授權。對 GitHub 已驗 ASCII owner/repo 名稱做大小寫等價判斷，不因 case alias 繞過 Agent/外部專案隔離；未知 rename/transfer、URL、redirect 不自動當同一資源。維持原意圖與明確權限 gate，只有候選建議不等於寫入許可。實作及 red/green 證據見 [工程知識索引](../../../knowledge/ENGINEERING_PATTERNS.md) EP-09/10 與 NATIVE-EP-008 原決策；未測其他 provider，不宣稱普遍識別或 ACL 驗證。

### 雲端架構專屬安全（TP-006 / NATIVE-CLOUD-016-STACK-SELECTION）
讀 [多平台選型及實戰指南](../../../docs/CLOUD_ARCHITECTURE_SELECTION.md)：Pages public artifact allowlist、GAS 真 visitor identity/原試算表不公開/single script writer/RAW/atomic batch、D1 條件命中與交易/receipt/secure cookie、Supabase RLS/grants/auth JWT/service-key isolation/RPC/storage。真資料治理獨立審查；缺 evidence 不因免費、官方功能或 selector 而通過。給各平台負測、backup restore 與安全範圍；同 SHA CI 不替代遠端實測。

### HTTP 收件與寫入邊界（TD004-OFFICIAL-01 / EP-12）
讀 RFC 9110 §8.6 與 RFC 9112 §6.3/8/9.6：身份與 JSON 驗證不代替 framing。固定長度 API 在 mutation 前核 ASCII decimal、大小上限、實收 byte count 與不支援 TE；EOF/timeout 不寫入且關閉連線。QA 用真本機 HTTP 測正反例，同時核 receipt 和具權限 workspace 不變，不能只看 HTTP 狀態。區分 idle timeout/絕對期限、local-only/production；原未知 POST 守門不變。細節與證據見 [獨立官方學習覆盤](../../../docs/training/reviews/2026-11-15-http-framing.md)，不冒稱正式資安通過。

- 同一原理遷移至 form-urlencoded 時，傳輸層先驗完整 bytes，之後才做 percent decoding、欄位數量、CSRF 及業務權限。區分傳輸無效（不應寫任何業務決策）和合法業務拒絕（原契約可能要求持久化 NOT_ACTIVE）；負測必須核對 inventory/requests/lifecycle/action_attempts 等相關表及檔案 bytes，正測保留正常編碼與冪等重放。NATIVE-HTTP-021 實際 red 六個副作用；fix 見原 EP-12 exact CI，無正式網路部署授權。

### PostgreSQL 權限交接（EP-13）
Architect 建立角色與所有權矩陣，Security 核 exposed schema、GRANT、RLS、view invoker、function EXECUTE、owner/superuser/BYPASSRLS；只用真非管理員角色的可見列及拒絕證據，不用 service role 冒替會員。可信後端 writer 的任意 DML 權限仍是信任邊界，production JWT、REST/RPC、Storage 各自查驗。參見 [TD004-OFFICIAL-02](../../../docs/training/reviews/2026-11-15-postgres-architecture.md)，不以 native lab 代替 Supabase cloud 驗收。

### 研究專案成員權限與服務層隔離（TD-005 必要專家訓練）
比較全域角色與「可信 session→actor→當前 study membership→operation」的授權；研究專案撤權後既有 session 不得沿用舊 membership。讀取、單筆更新及全部匯出均需 scope；study/id 複合鍵、參數化查詢、在同一交易查權限與副作用，拒絕須比較原資料、業務事件及適用 DB 快照，不只比較錯誤回應。區分安全稽核事件的合法契約與越權業務寫入。先用跨專案同 ID、撤權、讀者寫入、匯出、正常 operation 的獨立負正例；RLS 可作防縱深而非取代 API 層。參見 [受控研究 scope lab](../../../docs/training/reviews/test_research_scope.py) 及原訓練決策。本例合成 SQLite 本機證據，非真 Auth/JWT、同時撤權競寫、production 或完整資安驗收，不為無登入的靜態 APP 新增功能。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 security-review；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。

### GAS 入口、執行者及訪客權限（GAS-DIAG-002）
access 與 executeAs 分開，USER_DEPLOYING 的 effective user 不代表訪客；ActiveUser email 空白時需識別的操作拒絕，禁止 fallback 到部署者、client email/role。核准匿名非特權入口不等於管理功能公開；每個 server RPC/route 校驗角色及資料範圍，隱藏 UI 不能代替 ACL。USER_ACCESSING 查 granular OAuth scope、Workspace 政策/資源 ACL，不盲升 scope、不公開 Sheet/Drive、不傳 OAuth token；暫時 user key 作診斷而非登入證明。真角色正負測、未預期公開存取立即安全 HOLD，保留 C3/UAT。詳 [GAS-DIAG-002](../../../docs/training/reviews/2026-11-16-gas-diagnosis.md)。


### TD-004｜資料匯入的受限入口與錯誤診斷隔離（TD004-DB-SECURITY-01）
先定資料分類及批次權責，分收件/封存批准/正式轉入/審閱；不給一般匯入或審閱者直接DML權，受限入口核來源與封存狀態、允許的欄位/批次，拒絕覆寫、OR REPLACE/IGNORE造成靜默異常及既有目標衝突。審閱只讀必要批次/欄/固定原因碼；不得直接暴露raw、SQL exception或敏感日誌，資料最小化不等於匿名。SQLite authorizer由可信host設置、操作與schema/source預設拒絕及可信檔案邊界，非DB login/RLS；不得暴露原始可解除限制的連線或檔案，owner仍可改資料。正式系統另驗真身分、動態scope/撤權、approval digest/版本、競寫、資源上限及所有錯誤路徑，SQL Server view/ownership chaining/角色需真原生驗證。見[原覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜IDE外掛供應鏈與信任邊界（TD004-VSCODE-EXTENSION-01）
Workspace Trust限制部分終端/task/debug/extension和workspace設定，但不能阻任意惡意extension；未知來源保持Restricted Mode，不信任大範圍父目錄、不覆寫extensions.supportUntrustedWorkspaces、不放寬signature verification。核發布者、版本、目標平台/engine、來源與簽章、可信獨立hash、main/browser/activation/contributes/extensionDependencies/extensionPack/capabilities與實際程式/網路/檔案/憑證權限；沒有main或宣告Trust支持不等於安全。VSIX預檢先固定bytes、限制archive/entry大小與路徑/重複/連結、核manifest及預期payload，不執行或抽取陌生程式；本例精確allowlist只適用兩檔合成snippet ZIP，不是通用VSIX安全掃描、真簽章或安裝授權。外掛停用/回退需核既有副作用及可能資料外傳，不清原資料、不以重裝或撤權宣稱外洩復原。原[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜AI上下文、工具與副作用邊界（TD004-AI-CODING-REVIEW-01）
Context讀取不等於獲准傳輸：只選已分類核准的最少必要檔案/版本，校驗實際序列化payload、路徑/連結、來源SHA與byte cap；工具回傳/終端/URL會再進context，先審查分類與prompt injection，不以.gitignore/.aiexclude/content exclusion或MCP readOnlyHint當安全邊界。區分enabled、approval、OS隔離、網路出站及遠端ACL；核tool/target/arguments/before+after digest，過期或變更重新確認；拒絕未授權寫及未知副作用，不自動重送。合成canary測只證固定allowlist，不是通用secret scanner或真外傳防護；人審、實際provider政策/版別/資料保留、組織授權另核。不得用無訓練承諾等同不傳輸。原[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜MSBuild及NuGet可執行供應鏈（TD004-DOTNET-BUILD-01）
陌生project/solution/props/targets/rsp、父目錄自動匯入、SDK resolver、NuGet build/buildTransitive/analyzers與工具還原都可能執行程式；restore或IDE open不等唯讀。先讀來源與上下文，使用可信隔離暫存目錄、最少環境及專屬package cache，固定config source mapping（含transitive）、lock與來源/簽章，已在global cache的package可能不重新走mapping，metadata lookup亦另核。陌生碼不在有secret/網路的正式CI執行，不自動升級/下載；本次自製無程式碼marker/local feed且僅為避免網路的合成實驗停NuGetAudit及workload廣告通知，不推廣到正式專案、不宣稱OS出站隔離或已做漏洞掃描。靜態精確fixture checker非通用安全掃描，詳[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜範本供應鏈及生成後執行邊界（TD004-DOTNET-TEMPLATE-01）
範本來源、參數、實際生成與postActions授權分離。未知範本先唯讀審完整內容/identity及版本，核source/target/rename、路徑、symlink、符號替換及清單/bytes；排除private/.env/obj/bin等不等於通用secret防護，copyOnly仍會複製既有資料，應先分類並禁止真敏感原檔。核每種postAction（restore、script、chmod、reference等）與args/condition，預設不要放行任意腳本，--allow-scripts no只針對script不是所有postActions或OS sandbox；生成後檔案存在不代表action成功，核可觀察副作用。受控可信fixture的一個marker正反對照不是任意程式執行安全證明；必要網路/實際資料/外部權限獨立授權，勿在有secret的CI跑陌生來源。原[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜MVC輸入及狀態修改保護（TD004-DOTNET-CONSOLE-MVC-01）
route constraint不等於resource authorization，FromRoute與窄DTO/FromForm排除不可信body/query覆寫；拒絕型別/值域/缺欄後核真副作用未發生。Cookie型瀏覽器form用正確antiforgery機制，分缺cookie、缺token、錯token與有效pair；CSRF不等於身分/ACL/idempotency。Razor預設HTML編碼不擴及所有JS/URL/raw輸出，勿對不可信資料Html.Raw；輸出與業務驗收分離。原合成in-memory計數非真研究資料、DB/並行/重播及完整資安驗收。詳原覆盤（CI待驗）。


### TD-004｜請求生命週期與提交重播邊界（TD004-DOTNET-MVC-LAYERS-01）
Singleton需thread-safe且無個別請求/使用者的敏感狀態，Scoped不得被長生命週期捕捉；scope validation只驗可辨識組裝錯誤。CSRF、PRG、身分與幂等分離；正式幂等key須綁可信actor/tenant/業務scope及內容版本、資料庫唯一約束與交易、遺失ack唯讀對帳，禁止用key/GUID/receipt id代替權限。單程序lock+memory fixture只證受測重播，不跨restart/multi-instance、不證真ACL或並行壓測；不得把receipt/count測試入口公開給真系統。重導向由可信route生成、不可直接採任意returnUrl。詳原覆盤（CI待驗）。
