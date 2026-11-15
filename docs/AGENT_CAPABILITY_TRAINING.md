# Reliable System Builder Agent｜自主開發能力訓練與基準評測（獨立候選）

## 最新訓練主檔｜2026-11-15（持續更新入口）

**使用者決策（2026-11-15 最新、TD-001）：** 以教材的專業角色、技能、記憶、工作空間及實際工作覆盤為核心，使用既有 AI 平台執行；本地模型降為選用評測工具，保留已完成的工程能力。此決策取代歷史 P1-2「本地模型優先／缺本地模型先阻塞」的接續順序；不否定真實獨立評測的價值。每次先讀本節及 [訓練決策紀錄](training/DECISION_LOG.md) 的相關有效 ID，歷史頁面僅供證據查核。未核准之建議不覆蓋正式決策；本候選不代表已發布 main 或額外授權。

- TASK_DOMAIN: RELIABLE_AGENT_ENGINEERING_CAPABILITY_TRAINING
- SOURCE_REPO: lily4318/reliable-system-builder-agent
- ACTIVE_CANDIDATE: Draft PR #8, candidate-skill-team-integration-20261114；https://github.com/lily4318/reliable-system-builder-agent/pull/8
- SOURCE_VERSION: TD-004 SPECIALIZED_DEEP_CAPABILITY_ACQUISITION; NATIVE-PG-023 / TD004-OFFICIAL-02 advanced; NATIVE-PG-022 verified; NATIVE-HTTP-021 verified; NATIVE-CURRICULUM-019 verified; PR #8 HEAD authoritative; prior TD-003 retained.
- LAST_VERIFIED_STEP: PG advanced red 7dbd005bfed31e4e9b3cd6898b2082752b254d77 CI 43720967663 499 tests/1 failure SQLSTATE 23505 instead of 40001; fix e19f7a6f45dc25bd4329ef9bfc8453d30fa1b5a2 CI 43721034085 PG_ADVANCED_CANDIDATE_TESTS_PENDING; previous docs 43720331907 success. PostgreSQL native lab b5e61035272a8687b2f24a05030fda9d2eddfd44 CI 43720063088 POSTGRES_NATIVE_CI_VERIFIED (PostgreSQL 18.6, 494/494, 7 native methods); prior transfer docs 43719636689 success. P21 form transfer red c682d19fa6e7ece58dbbb20fede872b46f60282b CI 43719342135 raw 486 tests/6 actual side-effect failures; fix a1cf40d0fa5bdca908c057e92f73436ce4c4a50e CI 43719406375 FULL_CI_VERIFIED; prior documentation CI 43718959810 success. Curriculum validator exact e829d7bd77673fec41fc08535730d9d17ed812b7 / CI 43717413326 job 132822033470 raw 478/478, all 12 curriculum methods and EDITORIAL_BROWSER_PASS. HTTP red 481 tests / 3 real failures, CI 43718703256; HTTP fix 10be998cb877cec8911f83edf61736463f735c9d CI 43718746128 FULL_CI_VERIFIED. TD-004 exact 5a9b12bbaf14b16c2deffe1d07734bec4c3ab9d1 / CI 43716958509 job 132820455774 completed/success (listed steps). Prior direction proposal exact 2d6d6a06d0938b4917b9f906005a7a93c5f60c39 CI 43716539210 completed/success (run metadata).  Exact 0dbb7fc000a589fa0a94eb89f5a99ed6c5a3a2ee / CI 43715920202 job 132817353478 success 466/466 in 46.293s, 16 onboarding methods, EDITORIAL_BROWSER_PASS; preceding eebba69537bb8ed00308b9054c8a6dd8578f67c1 CI 43715814303 success. New continuation evidence is documented separately from exact tested SHA.
- COMPLETED: TD-004 confirmed; native PostgreSQL RLS/transaction/migration lab POSTGRES_NATIVE_CI_VERIFIED; advanced migration/concurrency PG_ADVANCED_CANDIDATE_TESTS_PENDING; source recheck and curriculum coverage validator verified 478/478; independent official HTTP framing unit implemented and real defect reproduced; fix FULL_CI_VERIFIED; equipment form transfer FULL_CI_VERIFIED; candidate instructions, role specialization and original learning skills integrated; TD-003 distilled user direction; four-platform adaptive onboarding router, signup/connect and failure branches, 16 offline methods, original role/skill/policy/guide integrations; prior CLOUD selector/C1 partial and Supabase Free actual readback retained.
- BLOCKERS: Specified HackMD curriculum full source/outline inaccessible; coverage and role-specific learning pending; B10 actual independent beginner guided delivery pending (existing GitHub connection branch partially evidenced); C1 remaining cost/permissions, CLOUD-A C2 and separate C3 approval, A07 independent fresh dialogue and formal launch pending.
- WRITE_OWNER: 僅 Agent 候選分支；main/Release、外部專案、真實個資、付費模型或正式部署不在本次授權內。
- SYNC_STATUS: TD004_CONFIRMED; CANDIDATE_LEARNING_INSTRUCTIONS_UPDATED; CURRICULUM_SOURCE_BLOCKED; CURRICULUM_MATRIX_UNKNOWN_TOTAL; CURRICULUM_VALIDATOR_VERIFIED_478_GREEN; OFFICIAL_HTTP_01_FULL_CI_VERIFIED; OFFICIAL_HTTP_FORM_TRANSFER_FULL_CI_VERIFIED; POSTGRES_NATIVE_CI_VERIFIED; PG_ADVANCED_CANDIDATE_TESTS_PENDING; TD003_CONFIRMED; BEGINNER_ONBOARDING_OFFLINE_VERIFIED_466_GREEN; PRIOR_DOCS_CI_VERIFIED; B10_EXISTING_CONNECTION_PARTIAL_EVIDENCE; C1_PARTIAL_VERIFIED; C3_NOT_AUTHORIZED; NO_EXTERNAL_ACCOUNT_CHANGES_OR_DEPLOYMENT; A07_FRESH_DIALOGUE_PENDING.
- NEXT_ACTION: Verify TD004-OFFICIAL-02 v3 exact CI 43721034085, actual SQLSTATE and 6 new methods before L4 claim; do not redo red evidence. Supabase actual Auth/REST/RPC/Storage and deployment not verified; prior L5 HTTP unchanged. Obtain authorized readable curriculum (Markdown/HTML/PDF/ZIP); incrementally fill the single [curriculum coverage matrix](training/curriculum-coverage.json), validate with python -m src.curriculum_coverage, verify exact source/evidence and assign one owner per unit, compare existing skills/evidence, start first dependency-ready high-value unit with seven stages and maturity evidence. In parallel apply TD-003/B10 to a necessary real beginner onboarding task with actual human step/readback/recovery and human assessment; existing connection branch partially evidenced, no redundant signup. If user separately confirms CLOUD-A scope, perform C2 and guide necessary manual Pages setup after C3. Preserve C1 gaps, A07 and no paid resources/main/release.

- TD-004 已正式確認（原 TP-007）：詳 [原決策紀錄](training/DECISION_LOG.md) TD-004 與 [共同規則](../AGENTS.md)。完整教材仍待取得，本輪不是章節實際學習。

- NATIVE-CURRICULUM-019：來源仍 BLOCKED_SOURCE，正式教材章節與成熟度均未取得；新增唯一矩陣及 offline structural validator（不認證來源、證據或能力），詳決策紀錄。先核新 commit CI 並以使用者合法匯出原目錄及章節續作。

- TD004-OFFICIAL-01 / NATIVE-HTTP-020：獨立官方技術單元，非 HackMD。安全主責與 Developer/QA 角色分工；[深度覆盤](training/reviews/2026-11-15-http-framing.md)。原程式真三拒絕失敗、修復候選及 exact CI 狀態見決策；教材矩陣不變。

- NATIVE-HTTP-021 驗收補記：NATIVE-HTTP-021 修復後 exact a1cf40d0fa5bdca908c057e92f73436ce4c4a50e / [CI 43719406375](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43719406375) job 132828041718 completed/success，所有列示步驟通過；raw log 245557 chars，487 tests in 63.561s OK，5 新 form framing methods 全 ok（含 6 原 red 情境、idle 408、正例及 replay）；P21-EQUIPMENT-BROWSER PASS actual_browser_dom_events=true, roles=3, stock=10, reserved=0, manual_uat=false；EDITORIAL_BROWSER_PASS 375/1280。四表與 SQLite bytes 無副作用負測通過；保留原正常業務拒絕持久化。L5 受控工程知識遷移證據成立（不同 parser/業務流程，非獨立未見 holdout、L6 或模型能力證明）；原 pending 記錄由本補記接續，不改歷史。

- NATIVE-HTTP-021：同一官方單元的 form-urlencoded 設備流程遷移，6 個實際副作用反例已重現，修復 FULL_CI_VERIFIED，詳 [既有深度覆盤追加](training/reviews/2026-11-15-http-framing.md) 及決策紀錄。HackMD 無新增學習單元。

- TD004-OFFICIAL-02 / NATIVE-PG-022：Architect 原生 PostgreSQL RLS/transaction/migration lab，POSTGRES_NATIVE_CI_VERIFIED。詳 [深度覆盤](training/reviews/2026-11-15-postgres-architecture.md) 及 EP-13；非 Supabase cloud/非 HackMD。

- NATIVE-PG-023：原 PostgreSQL 單元進階，實測鎖衝突/late DDL rollback/live prepared compatibility/同 token RC；RR denial stale snapshot 真 red 23505，v3 row version fix PG_ADVANCED_CANDIDATE_TESTS_PENDING，詳 [原覆盤追加](training/reviews/2026-11-15-postgres-architecture.md) 及 EP-13。

### 2026-11-15｜NATIVE-HUMAN-018 接續：文件整合 CI 與真實跨對話接續（PARTIAL DELIVERY EVIDENCE）
- 最新實際 candidate 0dbb7fc000a589fa0a94eb89f5a99ed6c5a3a2ee / [CI 43715920202](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43715920202) job 132817353478 completed/success；raw 241921 chars，466 tests in 46.293s/OK，16 onboarding methods 全 ok；EDITORIAL_BROWSER_PASS（375/1280 px，actual browser DOM events，manual_uat_completed=false，external_deployment=false）；全部 listed job steps success。前一文件整合 eebba69537bb8ed00308b9054c8a6dd8578f67c1 / CI 43715814303 completed/success（run metadata）；不是新程式或真人測試。main exact c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57 unchanged，PR #8 draft。
- 真實接續任務：從另一對話要求繼續原訓練，先找回歷史僅供定位；default main 的主檔／決策檔 GET 404，停止錯路徑，查 open PR #8 得 head 後同 SHA 讀回 START_HERE、AGENTS、主檔、決策與適用 project-intake/deployment/system-lead、account_onboarding、guide；發現歷史記憶仍是 C1，而原主檔已進 TD-003，採新版本，不重做 C1/466 測試。GitHub get_repo 真 metadata public、default main、repo ID 與原 C1 一致、push/pull flags true；實際取得該候選與 CI raw log，證明既有 connector 對本目標之讀能力，並非 Pages 管理授權。REPO_NATIVE/SINGLE_AGENT_ROLE_WORK；不要求真人重註冊、重連、CLI 或展示 secret。
- B10 適用支線：當前必要服務僅 GitHub（接續原 repo 工作，未選定新網站部署）；既有帳號／連接與目標唯讀已實證，人工帳號操作 0，原 main 缺文件時 Agent 自行以正式 PR 導航修復。此為真實工程與既有連接支線證據，不是全新使用者、帳號安全狀態、費用/Pages 權限核實、真人理解度或獨立 B10/A07 驗收；未假造 missing account、wrong account、付費或新增資源。B10/A07 remain pending。若使用者願意真人驗收，僅提供最小必要指引與人類評閱；下一個實需頁面設定在 C2 及獨立 C3 scope 確認後再開始。CLOUD-A 仍 PROPOSED，不以「繼續訓練」視為 C3；未做外部部署、外部寫入、資源建立、費用變動或正式 release。
- NEXT：原 C1 剩餘必要缺口視選定架構處理；CLOUD-A 另確認 artifact/C3 範圍後才實做 C2、必要的新人引導及實際上線驗證；可用獨立新手或 fresh dialogue 驗 A07/B10，勿以本輪跨對話接續自稱獨立盲測。此次僅增量候選文件，無新的決策取代 TD-001/002/003 或 TP-006。

### 2026-11-15｜NATIVE-HUMAN-018-BEGINNER-ONBOARDING：TD-003 完全新手環境引導與交付（CONFIRMED／CANDIDATE IMPLEMENTED）
- 使用者原意：「使用這個agent的人可能會沒有相關帳號與連結設定，在agent的訓練中，應加上帶領使用者完成需要的帳號的申請與GPT連結的部分，假設使用者都是完全新手，step by step的進行相關教學。以上我的需求請你提煉蒸餾出核心關鍵是什麼，並依據此核心需求進行agent訓練」。正式確認新手引導的能力方向；不授權為本輪建立真實帳號、連接、外部資源、付費或部署。TD-001/002、TP-006、原需求/授權 gates 不變。
- 蒸餾：Beginner-First Guided Delivery 零技術門檻的人機協作交付；Agent 主動判斷必要前置與現狀、只教不可代行的人類步驟、用當次介面逐步引導與實際唯讀核對、卡住依原因接續，至可安全繼續工程。不是把四個帳號/工具全當開工門檻、不是替人輸入密碼/同意條款/授權或付費、不是單純增加教學文本。方案：A 靜態通用手冊（原 GitHub 已有，缺動態路由與四平台）；B 既有技能擴充、狀態分流與逐步教學（採用）；C Agent 代所有設定（不可保證工具且有授權/身分風險，不採用）。不重做已完成流程或另建同功能 Agent/主檔。
- 本輪讀最新原 head 745919eef7f7a55ce5e95341441f9e254494de33 / CI 43715050614 job 132814649519 success raw239470 chars, 450 tests in49.721s, EDITORIAL_BROWSER_PASS；讀 START_HERE/AGENTS/master/決策/policy/原 human_walkthrough JSON/原 human-first docs/原測試/角色、project-intake/deployment/cloud guide。原 GitHub signup/repository/secrets 3 recipe 契約保持。實際 C1 Supabase Free/空 project readback、Cloudflare subdomain404/billing403、GAS capability gap/Pages tool restriction 為問題證據，沒有重跑雲端查核。
- 實作 code exact f3dc2575d7a17e1b1b39ebd1f3127ce58ef83c65 src/account_onboarding.py blob 4daea225dc8f83f99b674a90fcc5146874742680，tests/test_account_onboarding.py blob 57cb86a2c220626483332619dd8d0bdab67fa002。四平台 signup/connect recipe，復用原 GitHub signup；typed required+states/router，unknown/missing/ready/conflict/denied/wrong account/target/unavailable/failed/unsupported/cost 路徑；只選必要服務，已有跳過，16KiB stdin duplicate/形狀/未知拒絕，所有輸出 C1 pass、verified、write、deploy、pay false。16 測試方法（含四平台 subcase、multi-stack、CLI）已寫入，CI 43715589058 完成結果待核。路由不假裝真身份查核、費用或逐步 checkpoint 已自行驗證/保存。
- 原 START_HERE、AGENTS、policy、人類優先手冊、project-intake、deployment、system-lead 及 cloud guide 增量整合，仍7角色12技能，沿原 13 題及可編輯確認。操作指南 [新手環境引導](BEGINNER_ACCOUNT_ONBOARDING.md)。官方 ChatGPT Plugins/Apps 連接、權限、故障排除及 GitHub/Cloudflare 官方指南、Google API、Supabase 平台/計費查核。Google 建帳號官方中文頁抓取反爬失敗；Supabase dashboard 無可讀畫面，明示 UI 未實測；不編造截圖或按鈕。訓練設計 B01–B09 離線回歸與 B10 真新人情境獨立驗收（guide B01–B10），不以 CI 通過冒稱真人使用者測試。沒有自動建立帳號/連接/付費/資源/部署，沒有保存私人帳號識別/憑證。
- 影響：任何使用者需人工設定先按 TD-003 以新手為預設，必要才補問、步驟含目的/入口/具體動作/成功證據/安全停點、由 Agent 真查核，缺連接或不願授權提供安全替代。保留正式外部寫入與 C3，使用者從現有對話接續或之後其他實際任務驗證，不要求你再註冊已連接帳號。CLOUD-A 方案及 C3 尚未確認，A07 fresh dialogue pending 保留。NEXT：核 exact CI/文件回讀，進真正任務的 B10 驗收（必要時從零狀態描述引導並以實際已連接/缺設定安全觀測，不製造不必要帳號），使用者另確認 CLOUD-A scope 後可在 Pages C2/C3 實際套用新手引導。

- 離線實際驗收：exact f3dc2575d7a17e1b1b39ebd1f3127ce58ef83c65 / [CI 43715589058](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43715589058) job 132816301983 completed/success；raw log 241919 chars；16 個 onboarding test methods 全 ok，完整 466 tests in 49.191s，既有 EDITORIAL_BROWSER_PASS。四平台 signup/connect、既有帳號跳過、wrong target 全局優先、拒絕/失敗/不可用、GAS capability gap、費用停點、多服務、malformed/duplicate/size/forged approval、全部 ready 仍不授權等均實際跑過。舊 450 tests 保留；沒有建立真新帳號。文件整合 exact eebba69537bb8ed00308b9054c8a6dd8578f67c1 11份檔案已回讀相符，文件版本 CI 43715814303 另查。B10 真新手獨立操作仍 pending，不能由受控測試推論理解度或真 UI 成績。

### 2026-11-15｜NATIVE-CLOUD-017-C1-READONLY 補記：Supabase 已連接，實際 Free 方案讀回
- 使用者完成 Supabase 連接，沿原本 C1 唯讀授權接續；前次「未連接」為歷史狀態，現已解除。讀 Supabase skill、原主檔、決策與 C1 review。實際 list_organizations 回一組可見組織、list_projects 回空清單，get_organization 回 plan=free / tier=tier_free；不保存私人組織 ID、名稱/email 或身份資訊。僅證實當前連接的可見組織與專案資源，非所有不可見帳號/組織的用量保證。
- Supabase 官方 docs connector 查得 billing-on-supabase、free-project-pausing：Free 提供 owner/admin 所屬組織合計兩個免費專案，paused 不計；500MB DB/project、50000 MAU、1GB storage、5GB egress、500000 Edge Function invocations（多項配額按組織合計）；低活動7日可能暫停，暫停後 dashboard 可於90日內恢復。當次套餐確認成功，但組織角色、真正剩餘配額、建立專案的專案特定價格與寫入 scopes 未驗；不可保證零費用。專案報價需先由使用者選定組織，未呼叫 get_cost、confirm_cost 或 create_project。可在另行授權後核報價、選定區域/隔離新專案、驗 migrations/RLS/Auth/RPC/Edge Functions 及遠端 URL；前端仍需適當託管；禁止使用真人/敏感資料、付費、既有項目或未授權外部寫入。沒有執行 SQL、建庫、建立 branch、部署或讀取個人資料表。
- 原 C1 文件 exact 6274f0cae29d2a71d12c15cb4ef67a97c60b2351 / CI 43712836552 job 132807956654 completed/success，raw 239471 chars，450 tests in 48.013s，EDITORIAL_BROWSER_PASS。原 C1 Pages-first 建議不因 Supabase 連接逕自取代；但 CLOUD-D 現可直接唯讀查核且具實際管理介面，列為可行的 SQL/Auth 進階訓練候選。C1 PARTIAL_VERIFIED，C3 NOT_AUTHORIZED；保留原 A07 fresh dialogue pending。沒有新增免費資源或部署，不寫正式 main。

### 2026-11-15｜NATIVE-CLOUD-017-C1-READONLY：四平台 C1 真實唯讀能力查核（PARTIAL VERIFIED / C3 NOT AUTHORIZED）
- 使用者明示要求 C1 四平台實際部署能力唯讀查核、選最短真實線上路徑、提供可編輯授權範圍、更新原主檔；未確認不得建立外部資源或部署。讀原 START_HERE、AGENTS、TD-001/002、TP-006、NATIVE-CLOUD-016、guide、deployment、policy/release；REPO_NATIVE/SINGLE_AGENT_ROLE_WORK。外部查核僅 GET/身份/工具探索，無讀無關私人文件/資料、無寫雲端、無建立 token、無啟用 Pages/worker/DB、無部署。僅本候選原訓練紀錄允許增量寫入。
- 基準 exact 822191bbc4fe1e5a98dbd748e87a6a935e698e08 / CI 43712279245 job 132806268195 completed/success，raw 239471 chars，450 tests in 51.133s，EDITORIAL_BROWSER_PASS。正式 main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57 未變，PR #8 draft。維持 A01–A06 本機、A07 fresh dialogue pending。
- GitHub：實際讀 repo metadata，原 repo ID 1455152922，public、not archived、default main、has_pages=false；API 回 repo permission flags admin/maintain/push/pull=true，不能推論 managed GitHub App 有 administration/Pages 權限。允許 repo/git/PR/CI 操作已驗，GET /actions/workflows 被 connector allowlist 明拒 (400 INVALID_ARGUMENT，非 GitHub 伺服器權限拒絕)，tree 只有 .github/workflows/agent-ci.yml（read-only evaluation，contents:read，無部署）。專用 Pages admin/deploy/dispatch 端點未見；不能代設 Pages，不能用原 CI 當部署。查候選發佈分支 cloud-a-pages-training 得 GitHub 404 Branch not found，當時不占用；仍需寫前再查。Git create_tree 可空 base 建 artifact-only tree，再 prepare commit/專用 branch（未執行）。GitHub 官方 public Pages 可免費，site≤1GB，100GB/月軟限，10次 build/hr 軟限（自訂 workflow 例外），10min timeout，符合非商業教育訓練。branch publishing 已知路徑而非保證 App push 觸發；需真部署 log/HTTPS/version。
- Cloudflare：連接身份查詢成功，GET accounts 成功且只1個 standard account（不公開個人 account id/email）；GET workers/scripts 成功回0，GET d1/database 成功且 total=0，兩服務可讀；GET workers/subdomain HTTP404 code10007 無 workers.dev，首次開 dashboard Workers & Pages 可能自動建立，**本輪未開、不指示未授權者先開**。GET subscriptions HTTP403 code10000，OAuth 不覆蓋該 endpoint，實際 plan/remaining usage/寫權仍 unknown；不可用讀權推論寫權，不為讀帳單要求廣泛 API token。已查官方 API schema：PUT subdomain、PUT Worker script、POST versions/deployments、POST D1 建庫等，皆未執行。Free 公共 limits：100k worker requests/day、10ms CPU、D1 10 DB/500MB each/5GB account、5M rows read/100k write per day；需使用者採 Billing/Subscriptions 檢視免費方案、不開 Workers & Pages 初始化或升級；若選 Cloudflare 再核費用、subdomain 命名和資源 scope。Workers 列表為一次回傳，不宣稱所有不可見資源不存在。
- GAS/Sheets：Google Drive 連接已安裝，現有個人 Drive profile 唯讀呼叫成功（僅查身份不查私人檔案）；Sheets metadata/range/batch/create 等工具 schema 存在，非 GAS OAuth/deployment 實證。工具與外掛目錄兩次探索未找到專用 Apps Script deploy 連接，不等於所有未列工具不存在。未查研究帳戶或舊 script；未指定新 scriptId/工作簿/帳戶，不能核實剩餘配額或 GAS API scope。官方 Apps Script API enablement 及 OAuth 獨立，個人 6min/execution、30/user、1000/script、200 versions、mail 100/day、trigger 90min/day；Workspace/實際餘量未確認。GAS API 不等同 Drive。後續選隔離帳戶並明確允許後評估 OAuth/clasp/CI；不收聊天 secrets、不自行啟用 API/建立 cloud project。
- Supabase：真正目錄查獲可安裝、尚未安裝/連接的 Supabase app（描述支援專案、SQL/schema、Auth、functions、migration/log）；已提出連接選項，未自動安裝或讀寫帳戶。官方 Free 2 active projects（owner/admin 組織合計、paused 不計）、500MB/project、50k MAU、5GB egress、5GB cached egress、1GB storage、1 week inactivity pause；實際 org/plan/project/權限未讀，不當作驗證成功。另需前端託管費用及 RLS/backup 等 C2。
- 方案排序（助手建議、非使用者已批准）：CLOUD-A Pages 優先為第一個最短可公開靜態 HTTPS 訓練，既有 public repo、不另建帳戶/DB，預計一次人工 Settings→Pages 設專用 branch/docs；以 artifact-only tree 白名單 index.html/style.css/app.js/.nojekyll（資料只公開合成）隔離主檔與程式、C2 exact artifact/CI 安全驗收，C3 另確認部署/發布 branch、公開受眾/0增量費用/指定操作與限期、v1→v2→前版內容新 commit 回退。**建立分支和公開啟用都尚未授權；先確認後做，不發假 URL**。如 Pages 設定/觸發受阻，不改 main、不強推、不盲重試；Cloudflare 已連接是動態+DB 的較短候選，待 free plan 與 subdomain 額外授權；Supabase 連接後再查 C1；GAS 仍缺安全 API 路徑。此不是完整 WEB-EDITORIAL-01 遠端驗收，Pages 不承擔原私稿/登入/交易。
- 詳 [本輪 C1 實查、差異和可編輯 C3 範圍](training/reviews/2026-11-15-cloud-c1-readonly.md)。C1 audit performed, per-platform PARTIAL，真正 C1 all gates 未通過；C3 未核准。保留所有權限、真資料、免費及正式 release 既有 gate；無新資源、測試部署、付費或跨專案讀寫。NEXT：使用者明確確認 CLOUD-A 隔離發佈及有限操作範圍後，候選 C2 artifact/測試/CI/精確 tree 回讀→重新確認資源未占用及免費→按已確認的 C3 操作；如需人工 Pages 設定，在 artifact 驗收後提供一步 UI、核對真結果。其餘平台的缺口並行用安全唯讀途徑查核、不阻擋可行工程。

### 2026-11-15｜NATIVE-CLOUD-016-STACK-SELECTION：TP-006 多平台選型與實戰路徑（CONFIRMED / CANDIDATE IMPLEMENTED）
- 使用者本輪明示：「請依 TD-001、TD-002 及 TP-006，建立 Agent 的多平台免費架站與資料庫選型能力，以 GitHub 為共同工程基礎，完整掌握 GitHub Pages、GAS＋Sheets、Cloudflare＋D1、Supabase 的架構、安全、部署、成本與適用條件，設計實際工程訓練及驗收路徑，更新原訓練主檔。外部部署前另行確認授權。」確認此能力方向與候選訓練實作，非任意 provider、account、資源建立、付費、部署、真人資料或正式 release 授權。維持 A07 SOURCE_RESUME_VERIFIED/FRESH_DIALOGUE_PENDING；不用重做本機 A01–A06。
- 原 head fa89fe3e61b418a9d9b1607679ae92ea4df2bd11 / CI 43711638357 job 132804267265 completed/success，raw 236520 chars、434 tests in 49.414s、EDITORIAL_BROWSER_PASS。讀 START_HERE、AGENTS、原主檔、TD-001/002、TP-006、policy/catalog、architecture/security/deployment、角色、EP-09/10；REPO_NATIVE/SINGLE_AGENT_ROLE_WORK；不宣稱獨立子代理。
- 2026-11-15 重新核官方四平台 limits、pricing、身份、交易及備份。方案層比較：公開靜態→Pages，Google 整合單 writer→GAS，動態 SQL→Workers/D1（不需要 DB 則 assets/API 免綁 D1），Postgres 或 managed application auth→Supabase+另擇前端。硬限制優先，不以免費/便利掩蓋資料治理、用途限制、跨 writer、pause/SLA 或特定 DB 需求。保留混合架構及沒有免費適配時停下。原比較的 Cloudflare first 非全部站的預設。詳細 [選型與實戰指南](CLOUD_ARCHITECTURE_SELECTION.md) 及原 TP-006 review。
- 實際候選程式 exact 047ca6340337d034842a6bd262ff1d2c80a5e56d: src/cloud_architecture_selection.py blob a7ba20101506572ba39ece1fe96b9209e7b4ff1e、tests/test_cloud_architecture_selection.py blob 03588c95261fe1bf945d2a2149b394cd1bf43529。strict14欄 structured profile + provider-specific estimated units；不合法/未決/個資或敏感資料/保證 SLA 停或排除；公共免費 ceilings/80% advisory headroom/未估非零；四方案 reason/alternative/checklist/sources；所有實際 provider verification、cost guarantee、deploy、write、pay、release flags false。STDIN 64KiB bounded duplicate check，16 test methods 含 CLI/limit boundary、拒絕偽造授權。CI 43711988622 尚未回讀完成結果，不能稱通過。只離線 advisory，非新 gate 取代既有工程 workflow，自述資料非真實帳戶證據；80% 是設計選擇，保守而非官方。
- 原 architecture-design/security-review/deployment 三技能增量接入 guide/selector，仍7專家12技能；C0–C6 各自獨立 gate（需求/資源能力/同 SHA CI/外部部署授權/實際 URL與版本/真遠端功能及復原/真人與正式啟用）。CLOUD-A Pages 最小公開靜態發布；B GAS 合成單 writer 編輯待辦；C WEB-EDITORIAL-01 雲端 D1 adapter；D Supabase Auth/RLS/Postgres 共享契約差異；E 實際覆盤／遷移。不重做已通過的本機網站，未建/改外部資源，帳號權限及免費 plan 未實測。沒有自動部署 workflow 或外部寫入。
- NEXT_ACTION：先核 selector exact CI 及文件 CI；再 C1 唯讀核對四平台現有工具與授權、帳號可行性（限制只讀/合成目標，不查無關私人內容），提出最短實際 HTTPS staging scope、可編輯單獨授權；優先 CLOUD-A 如可用，若阻塞改下一條可安全推進而非重複同一人工操作。CLOUD-B/C/D 選型與雲端特有契約驗收待實際施工。保留 A07 新對話未驗及真真人 UAT/正式發布/其他平台/獨立盲測，不用 CI 代替。

- 2026-11-15 實際 selector 驗收補記：exact 047ca6340337d034842a6bd262ff1d2c80a5e56d / [CI 43711988622](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43711988622) job 132805354146 completed/success，raw 239471 chars，16 新測試方法全部 ok，450 tests in 51.738s，既有 EDITORIAL_BROWSER_PASS。先前434保留。涵蓋四平台選型、硬拒絕、limit-1/limit/limit+1、unknown、malformed、資源排序、CLI process、拒絕偽造外部授權等。原稿 80% 警戒是 advisory 工程假設；估算可由使用者提供但不證實實際供應商帳號/成本。文件整合 exact a59fbc00837e56c0fe14559b67fe6caeb6f44eb7 七份文件回讀 SHA 相符，CI 43712173888 尚未完成；最新回讀及 CI 待分開確認。選型規則已通過離線受控驗收，不宣稱四平台實際部署、安全或獨立模型能力。C0–C6 與 A–E 路徑皆為未來適用的實戰計畫，未有雲端 resource/URL。

### 2026-11-15｜TP-006 補記：GAS＋Sheets 原生全端部署路徑（DISCUSSION / PROPOSED）
- 使用者詢問「那GAS + Sheets呢?」；建議將 GitHub + GAS Web App + 私有 Sheets 列為與 Pages、Workers/D1、Supabase 並列的優先選型，而非一律先用 Cloudflare。GAS 可直接託管 HTML Service、執行後端 JS、透過 google.script.run/doGet/doPost 提供功能，原生整合 Drive/Gmail/Calendar/Docs。適合受控低流量行政、報表、文件、一般報名與預約；不能僅因免費宣稱合規或適用所有交易/高流量系統。現有研究或臨床系統不在本輪讀寫授權。
- 官方來源 2026-11-15：https://developers.google.com/apps-script/guides/web 、https://developers.google.com/apps-script/guides/services/quotas 、https://developers.google.com/apps-script/concepts/deployments 、https://developers.google.com/apps-script/manifest/web-app-api-executable 、https://developers.google.com/apps-script/reference/base/session 、https://developers.google.com/apps-script/reference/lock/lock-service 、https://developers.google.com/workspace/sheets/api/guides/batch 、https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/batchUpdate 、https://developers.google.com/workspace/sheets/api/limits 、https://developers.google.com/apps-script/api/reference/rest 。個人/Workspace 每次6min、30 simultaneous/user、1000/script、200 versions；個人 vs Workspace 每日郵件收件者100/1500、trigger runtime90min/6hr、URL Fetch20k/100k。限額非併發 SLA，執行身分及關聯服務配額另核；Workspace 本身未必免費。
- 架構：GitHub 為 source，GAS 為前後端，私有 Sheets 為資料、Drive 為附件備份、按需 Gmail/Calendar/Docs；公開前端不直連私庫，不公開工作簿。資料 ID/版本、伺服器驗證 actor/role/ownership、每個可呼叫函式授權、拒絕未知身分；execute-as-deployer 不等於來訪者身分，Session.getActiveUser().getEmail() 可空白；外部匿名及管理端分隔、管理端限定適當已驗證身份。資料分類、最小 scope、機構政策、跨境與真人資料另審。
- 交易工程：同一 script 的 getScriptLock + lock 內回讀/expected version/actor-token-payload receipt、單次 Sheets API batchUpdate 原子寫入同一工作簿；不宣稱跨 script、人工修改、跨工作簿/Drive/Gmail 等交易隔離，document lock 在 Web App 可能 null。控制唯一 writer 或明確外部寫入契約，禁止盲重送不明 POST，讀原 actor receipt、對帳、處理逾時與未觀測結果；防公式注入（RAW 或明確 stringValue）、批次讀寫、保護原資料、備份與 restore 到獨立工作簿、quota/abuse gate。對需要嚴格併發、DB 約束、複雜 join、RLS 或大量交易的系統優先評估 SQL。
- 部署：Apps Script API 可 getContent/updateContent、versions.create、deployments get/list/update/create；或經授權 clasp / GitHub Actions。先確認 scriptId、spreadsheetId、部署者/訪客身份、版本、OAuth scope 與帳號政策；完整檔案更新前備份及讀回，immutable version → 更新既有 deploymentId（維持 /exec URL）→ 實際網站與資料驗收；/dev 非正式使用。正式回退到舊 version 不回退資料本身，先驗相容性。可用工具名稱查核未見專用 Apps Script API/部署 connector，不能把 Google Drive/Sheets 權限當成 GAS 更新/發布授權；實際 OAuth/部署途徑未驗收，需要個別授權與能力查核。
- 原 head 64fccdec341595c2ca3d2cd478feaa29eaeb2004 / CI 43711227932 job 132802997034 completed/success，raw 236523 chars、434 tests in 49.896s、EDITORIAL_BROWSER_PASS；A01–A06 受控驗收及 A07 FRESH_DIALOGUE_PENDING 保留，未重跑原測試或改程式。新增 GAS 比較屬 TP-006 建議，不更改主線或自動啟用雲端服務。下一階段建議以適用性、可操作授權、免費限額、身分及資料邊界判斷平台；先設計合成獨立 staging 規格、使用者確認後才建立資源與真 /exec 驗收。

### 2026-11-15｜TP-006 補記：GitHub 自身部署能力與架構分層（DISCUSSION / PROPOSED）
- 使用者提問「github也能部署網站，為什麼你沒有推薦?」；原比較有列 Pages，但偏重全端同源架構，未充分說明已可用 GitHub 為靜態站首選之一及 CI/CD 核心。不是使用者已確認選型或授權實際 Pages/Actions 部署。
- 官方查核：https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages 、https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits 、https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site 、https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https 、https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job 、https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments 。Pages 免費方案公開 repo，可直接發布 HTML/CSS/JS 及建置後 React/Vue，HTTPS，1GB published site、100GB/month soft bandwidth、10 builds/hour soft（自訂 Actions workflow 例外）；非 Python/Node 常駐後端或持久 SQL，禁止商業交易/SaaS 等用途及不宜敏感交易/傳密碼，私人 repo 不等於私人 Pages。公開 repo 標準 GitHub-hosted runner 免費但每 job 臨時環境，非長期網站或資料庫。
- 建議分層：A GitHub Pages + Actions 適公開非交易文件/作品集/教育展示、可生成靜態公開文章（僅允許公開內容，不把草稿/私密資料打包）；B Pages + 外部 API/DB 技術可行，須用途符合 Pages 條款、公開前端不放 secrets、精確 CORS/權限；涉及帳密/業務後台改在適合的同源服務/獨立登入服務，不能靠 Pages 儲存敏感交易。C GitHub + Workers/Static Assets + D1 或 Supabase 適完整動態網站；GitHub Actions 做授權 CI/CD，環境 approval、scope secrets/OIDC、版控、遠端部署回讀、回退。GitHub 是否可實際啟用 Pages、配置 secrets/environment 或觸發部署仍須核 connector 權限、目標 repo 與獨立授權；不靠 Actions 把 SQLite/JSON commit 當多人 DB。
- WEB-EDITORIAL-01 有角色登入、私稿、審核、版本及交易，Pages 單獨不能滿足；可評估 Pages 公開刊物＋獨立安全後台 vs GitHub+同源 Worker。若採分離架構，靜態發布延遲及下架立即不可見的既有需求衝突需先驗證或重新取得規格確認；不自動改規格。依需求選最簡單適用方案，不強制所有站 Cloudflare。
- 原 head 81510fd3e8514190cd2ce9d033a7298f37a9d2ff / CI 43709938018 job 132799097402 completed/success, raw 236518 chars, 434 tests in 44.691s、EDITORIAL_BROWSER_PASS；保留 A01–A06、A07 FRESH_DIALOGUE_PENDING。原 TP-006 review 補充比較，未改程式、正式 main、Release、雲端帳號/資源或部署。方案待確認。

### 2026-11-15｜TP-006：免費雲端部署能力（DISCUSSION / PROPOSED）
- 使用者明確澄清長期目標：「我希望這個agent是可以直接協助完成線上部署，但我不確定有哪些資源目前是可以免費架設網站和資料庫且足夠安全的」。此為能力目標及方案討論，不是 WEB-EDITORIAL-01 外部部署、建立資源、帳號、付費、真個資、正式發布或跨專案寫入授權。原 v0.1 明示不授權外部部署；本機驗收保留，非長期交付終點。
- 核對原 Draft PR #8 head cadf390f2c43d7dee9e66882f5fe440ea437cccf / CI 43709560256 job 132797945225 completed/success，434 tests in 47.906s，原 Editorial browser PASS；A01–A06 受控驗收、A07 SOURCE_RESUME_VERIFIED / FRESH_DIALOGUE_PENDING 均保留。未再跑測試或修改網站。
- 方案及官方當日查核 [免費雲端部署比較與安全方案](training/reviews/2026-11-15-online-deployment-options.md)。優先建議 Workers + Static Assets + D1（免費配額內、合成資料、隔離 staging）；Workers + Supabase Postgres/Auth 作第二路徑；GAS/Sheets 適行政整合而非通用交易 DB；Render 免費 DB 30日到期，GitHub Pages 無原生後端且用途受限，Vercel Hobby 需核適用條款。原 Python sqlite3 長交易/本機 Host/Origin/cookie 不可直接移植至公開 URL，需獨立新增雲端 adapter/transaction contract、auth/secure cookie、rate/abuse/cost/backup/deployment rollback gate；現有 Cloudflare connector 有 docs/API discovery/execute 介面，但未核個人帳號、權限或資源，不宣稱可部署。無資源建立及雲端測試。
- 使用者意圖確認的是目標，供應商與方案、實際部署範圍尚待個別確認；保留 TD-001/002 及 A07 未完成 gate，不將建議取代主線。可在 A07 新對話獨立驗收之外平行做已獲授權的部署規格/技術前置；後續提出可編輯的雲端規格及零付費/帳號/資源作用域授權，取得後再建立隔離測試環境及真 HTTPS/遠端版本/持久化/安全/復原證據。不得直接上線真研究或醫療資料或從免費推論合規。

### 2026-11-15｜NATIVE-WEB-015-A07-SOURCE-RESUME：A07 正式來源接續查核（獨立新對話尚待）

- 使用者本輪明示依 TD-001/002 完成 WEB-EDITORIAL-01 A07，僅依 GitHub 原主檔、決策、確認規格、程式、原始 CI 與操作指南，不重做 A01–A06，更新原主檔。System Lead/resume-project，REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，EP-10 SOURCE_READ。此次實際取得新一輪工具回讀證據，但本對話含前次工程內容；無獨立新 ChatGPT 對話啟動工具與隔離證據，**不能冒稱跨新對話獨立完成**。不啟動外部服務或其它專案 session，未取聊天記憶或以舊回覆代替正式來源。狀態 SOURCE_RESUME_VERIFIED / FRESH_DIALOGUE_PENDING，非 A07 全 PASS。
- 定位：Draft PR #8 最新 head 1258dc33a5d569721237464294ff1cb88cb9273b，branch candidate-skill-team-integration-20261114，main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57 未變，release/current_release.yaml formal_release_approved=false，AGENTS/config policy 不授權 merge/deploy。讀 START_HERE、AGENTS、原主檔頂、TD-001/002 及原最新決策、確認規格、ADR/plan、操作指南、角色與技能、EP-10。無私人工作區或獨立子代理使用。
- 規格來源：原提案 45b3e32f09107934a8aa6c94e0072446b5d89db9 blob 121e93d77799905c73043bbfe7971d77bd3f56dd；當前確認規格 blob de8ee98b3364e9287ff762ab30dddfbd70d0979f。實際字串前綴完全保留，R01–R13 13列及 A01–A07 7列逐列相等，原提案末補真正使用者確認與候選寫入授權，決策紀錄同確認。歷史 PROPOSED 不覆蓋最新 CONFIRMED；僅公開合成 localhost、原候選範圍，不擴張部署。ADR 有 W0–W6 7工作包及13條需求追溯列；歷史 planned 應依實作驗收補記判讀。
- 版本證據：GitHub compare ca030a15af00d3dd4459a3c9829636385c37378b...1258dc33a5d569721237464294ff1cb88cb9273b 為 ahead，變更僅6份訓練/技能文件。兩個完整 recursive tree 未截斷；逐一回讀11份網站實作/測試/CI/操作指南 blob，包含 store 84755683844217e192ac27c18547c6ac204c2e14、HTTP e0c553e2e83668e797f5cbc557c3b6a8b7621f34、app f45124554953aad15a615e1fa5935db89012180b、index、CSS、browser JS、browser runner、兩測試、workflow、guide；各自兩版本 SHA 相同且實際回讀相符。確認 schema2、唯一 open/public index、角色/授權 API、receipt、同分頁未知結果及 test-only route 的原程式入口。沒有重新執行 A01–A06。
- 原始日誌：程式 exact ca030a15af00d3dd4459a3c9829636385c37378b / CI 43708288874 job 132794093170 completed/success，raw 236518 chars，434/434 in 45.381s；最新文件 exact 1258dc33a5d569721237464294ff1cb88cb9273b / [CI 43708546444](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43708546444) job 132794858407 completed/success，raw 236520 chars，434/434 in 49.976s。兩版各10 editorial unittest methods ok，所有 job steps 成功，獨立讀出 375/1280 各29 true checks、actual_browser_dom_events=true、manual_uat_completed=false、external_deployment=false。核對已存在日誌，不手動觸發重跑。各測試未重複計數或泛化為独立模型增益。
- 接續導覽實查：以目前 Git tree 解析 START_HERE、主檔最新段、決策最新段、確認規格、ADR 與本機指南共15個相對連結出現次數；14個可解析，1處 ADR 的 ../AGENT_CAPABILITY_TRAINING.md 實際指向不存在的 docs/training/AGENT_CAPABILITY_TRAINING.md。修成 ../../AGENT_CAPABILITY_TRAINING.md（原 docs/AGENT_CAPABILITY_TRAINING.md），不改實作。另以原檔與實際 evidence 判斷 W0–W5 完成、W6 覆盤已交，A01–A06 受控驗收保持；A07 工程交付已備、正式來源重建通過，但另一獨立新對話仍是最高前置缺口。禁止用舊批准自動做外部寫入、部署、人審或主檔宣稱全 PASS。
- NEXT_ACTION: 使用者在真正另一個新對話（不把本輪結果或前次進度貼入，若平台允許則不用舊聊天記憶）送出最短自足指令：「https://github.com/lily4318/reliable-system-builder-agent 請依 TD-001/TD-002 及 Draft PR #8 正式來源，接續 WEB-EDITORIAL-01，實際核對目前狀態、版本、授權、原始驗收與下一項安全工作，保存可查核 A07 接續證據；不要使用舊聊天內容、重做已驗收工作、部署或跨專案寫入。」新對話應報實際讀取的 head/blob、CI job/log、已完與待辦、授權、最小真實接續動作與回讀，並誠實說明對話隔離可驗程度。若仍是同一對話，不能關閉獨立 gate。真人 UAT、正式發布/HTTPS/跨平台等各自另驗，無需先安裝模型。文件 commit 自動 CI 另核，不將自動回歸視為本輪重做驗收。

### 2026-11-15｜NATIVE-WEB-014-EDITORIAL 完整工程驗收（WEB-EDITORIAL-01/v0.1）

- 授權與正式來源：使用者本輪明示確認 R01–R13/A01–A07 並獨立授權原 PR #8 候選程式開發，不授權正式發布、外部部署、跨專案修改。原規格 blob 121e93d77799905c73043bbfe7971d77bd3f56dd @ 45b3e32f09107934a8aa6c94e0072446b5d89db9；[確認及 ADR/工作包](training/reviews/2026-11-15-editorial-architecture.md) commit 3995edb4ca744bc57a05eb335d8a412f2f7e19f6。保留原提案及實際確認，不另造 local review/私庫收據。基準 CI 43706231648 job 132787799571 success 424/424。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，按目標實際選用 System Lead/resume-project, task-planning、Architect/architecture-design, requirements-spec、Developer/implement-feature、Security/security-review、QA/test-and-acceptance、SRE/deployment（僅同 SHA CI、本機恢復指南）、Learning Evaluator/learn-from-feedback, knowledge-distillation；非獨立子代理呼叫。
- 實作：stdlib Python HTTP + SQLite + HTML/CSS/JS（同一 CI 零新套件；Flask/Django 比較見 ADR），新 src/editorial_store.py、src/editorial_site.py、examples/editorial-site/、src/editorial_browser_test.py、tests/test_editorial_store.py、tests/test_editorial_site.py；原 CI 僅增加本機瀏覽器步驟。資料庫 schema 2：帳號 PBKDF2 加鹽 hash、30 分鐘 session hash、article/public revision 指標、唯一未完成稿/公開稿、revision counter、audit 與 actor/token/payload receipt；BEGIN IMMEDIATE 核對 session、角色、owner、狀態、expected article version，成功同交易保存 public pointer/狀態/audit/receipt。合法拒絕保留 receipt 但不增加有效事件，未知結果唯讀查收據；公開只讀 PUBLISHED 指標，私稿不覆蓋舊版。獨占 init/backup/restore，復原清舊 session；原 schema1 中間候選不直接開啟，無正式資料 migration。編輯只能審查已送審及歷史稿，不讀現行 DRAFT，不直接改文。真 HTTP 嚴格 loopback Host/Origin、CSRF、session cookies、128KiB JSON cap/shape，純文字 DOM；UI 先保留 action token/原帳號（同分頁 sessionStorage；非認證憑證），未知結果停止新增業務寫入，原帳號唯讀查已觀測才清除；NOT_OBSERVED 需先停止舊 writer、核實狀態再人工處置，不自動 replay。
- 逐版實際證據（均以 exact CI 原始日誌，沒有虛構 RED）：664d73280929e2cc48f4b118ba65edd5ee4e02fa / CI 43707660255 job 132792149277 green 429 in 45.725s；核心五項方法，交易/權限/版本/21列分頁/備份。70fa4676a8cdf354cb6ffa4588e1642be103ad62 / CI 43707790046 success（前後端初版，只前次既有 tests）；410fd06d3d30a68df5fa653d897a701cd9f51eda / CI 43707952490 job 132793042213 raw 235660 chars, 432 in 49.326s，2 viewport 各20 true DOM checks；逐項規格對照後 10eb16e94e5317049036c6c5789af83b039c68cb / CI 43708130426 job 132793593785 raw 236147 chars, 433 in 48.686s，2x26；增 revision counter/退回理由歷史、實際 subprocess cut/CLI backup restore、實際分頁及遺失 ACK read-only recovery。不放寬安全規則。
- 最終 EXACT ca030a15af00d3dd4459a3c9829636385c37378b [CI 43708288874](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43708288874) job 132794093170 completed/success，raw 236518 chars，434 tests in 45.381s/OK；6 new store methods +4 HTTP/CLI methods（共10新增，原424保留），actual Chromium 375/1280 exact CSS width 各29 checks（58 observations，非58獨立需求），EDITORIAL_BROWSER_PASS / actual_browser_dom_events=true, manual_uat_completed=false, external_deployment=false。兩種尺寸均完成兩作者/編輯/匿名、真 Tab 鍵、21列分頁、實際事件從草稿、送審/退回/再送、核准未公開、另行發布、修訂中保留舊公開版、原子切換、下架、再發布。真網路回應遺失由 test driver 在 server 已回應後 drop ACK；原 POST count=1，跨帳號拒絕、原帳號重登入唯讀查 receipt，未發第二 POST。store subprocess os._exit(17) 在 audit 寫後 receipt/commit 前 cut，原資料及公開 pointer/receipt 未變，核對後合法執行。CLI init/verify、兩次獨立 server processes、backup/restore 到不同新檔、公開結果一致、還原舊 session 拒絕。其餘既有 CI 全步驟 success。
- 完整實作檔 blob（exact ca030a15af00d3dd4459a3c9829636385c37378b）：store 84755683844217e192ac27c18547c6ac204c2e14；HTTP e0c553e2e83668e797f5cbc557c3b6a8b7621f34；app f45124554953aad15a615e1fa5935db89012180b；index ba1694a5bac5fb1badb9565ef43e276bfa804253；CSS 8840a293183f6e0445f4fac1b0cee1661c27246a；browser driver 021516ae9a5e76060cbeb30c49cf96406e64f149；browser JS 9c078f1d26507b25ed87d9fc024bc2eb7d09e958；tests store 3d0ce94ab5f465664168083a23747ae8c83f43d1；tests HTTP d8ec6726cff2e19ca9218ec4cbf84f626adb6939；CI f9a54baeb58ceb0c056de35931ae29efada4719a；[本機使用與回退指南](EDITORIAL_SITE.md) fe5fa094f6204cd03c54f450eb0481b3b2d1cf16。原 main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57，PR #8 仍 draft。
- A01–A06 受控本機功能、安全與復原驗收通過；A07 已交確認規格/架構/DAG/schema/程式/測試/同 SHA CI/操作復原指南及原檔 Git 證據，尚待**另一次新對話實際依原來源接續**，不可用本輪接續文檔冒充跨對話完成。A05 實測公開內容、pointer/list、交易狀態、integrity/FK、舊 session 失效，並非對每一資料欄位作全庫比對或敵意 DB 測試。A06 為自動真 Chromium，非手動 UAT/完整 WCAG。UI pending 保留於同一分頁 sessionStorage、跨同分頁重登入有實測，非跨設備或任意 reload/瀏覽器關閉的復原證明。受控 loopback 無 HTTPS/Secure、production rate limit/容量/長歷史負載及 adversarial shared localhost 驗收；不能直接作公開服務。無正式部署、真人資料、付費模型、獨立多 Agent/盲測或跨平台模型增益。
- 覆盤：EP-02 確認與 immutable revision/public pointer 綁定，不用 state=APPROVED 自動發布；EP-03 同 transaction 版本/事件/收據，一次業務 effect，UNKNOWN 先查同原 actor receipt，實際 cut/ACK 兩種不同失敗；EP-06 用真 DOM＋直接 HTTP 及 CLI 測而非以 JSON/頁面或 local flag 冒充全站。選擇同一縱向網站，不再做與報名、設備、報表相同的獨立工具；共用知識補進原 EP-02/03/06、implement-feature、test-and-acceptance，非重複新增知識卡或自動升格；2 DEFAULT +6 OPT_IN 不變。未改正式政策、原 Release 或外部 repo。
- NEXT_ACTION：核對最終文件 exact head/CI；於另一新對話讀原正式訓練主檔、決策、已確認 spec、ADR、guide、exact code/CI，再進行 A07 跨對話接續驗收（識別已完、未完與 scope，不重做已通過的網站）；若使用者另行做本機人工 UAT，依具體指南與結果更新。優先以已完成完整網站作為長期工程能力驗證，知識升格另審，不擅發布。

### 2026-11-15｜NATIVE-WEB-014-EDITORIAL：確認規格、架構與施工工作包

- 使用者本輪明示：「我確認 WEB-EDITORIAL-01/v0.1 完整規格 R01–R13 及驗收 A01–A07，並另行授權在原 reliable-system-builder-agent PR #8 候選分支內實作此合成網站。請完成架構設計、工作拆分、前後端、資料庫及實際驗收，持續更新原訓練主檔。不授權正式發布、外部部署或跨專案修改。」狀態 CONFIRMED（規格與獨立候選寫入兩項）；原 v0.1 內容 blob 121e93d77799905c73043bbfe7971d77bd3f56dd @ 45b3e32f09107934a8aa6c94e0072446b5d89db9，無需求變更，保留歷史。非本機確認或模型產生旗標。
- 基準 45b3e32f09107934a8aa6c94e0072446b5d89db9 / CI 43706231648 job 132787799571 success，424/424，43.929s。架構與 DAG [原實戰架構](training/reviews/2026-11-15-editorial-architecture.md)，W0/W1 設計已記錄，W2–W6 待實作與驗收。選 stdlib SQLite/HTTP/HTML 以零依賴受控本機，非正式公開架構；EP-02/03/06 SOURCE_READ，同一實際 Agent 角色分工。不得自動發布。

### 2026-11-15｜NATIVE-MATURITY-013-EDITORIAL-SPEC：完整網站工程實戰，規格提案（TD-001）

- 本輪使用者明示選不同設備/報名/報表的完整網站實戰，設計需求/資料/權限/功能驗收，先可編輯規格審閱確認後才實作。原 Draft PR #8 HEAD a8d392d2ded5386b44613246567df5953f8bfdce / CI 43705942761 job 132786914468 completed/success，raw 232218 chars，424 tests in 41.433s，六案例 actual DOM handoff 全過；不重做成熟度盤點或原功能。
- 選定公開合成委託 WEB-EDITORIAL-01/v0.1 線上編輯與文章發布管理平台，非既有 W101–106 的完整網站類型。比較付款商城（額外付款授權及範圍）、另一預約/目錄（重疊）、編審發布（採為待確認提案，驗證文章版本、角色、狀態、公開內容隔離、持久化、安全與瀏覽器）。原 P22 文件審閱經驗可用但不等同此完整網站。詳 [完整可編輯規格](training/reviews/2026-11-15-editorial-website-spec.md) R01–R13 / A01–A07 / D1–D6；皆 PROPOSED 非使用者實際答覆。單 Agent 模式 REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，讀 System Lead/project-intake、Architect/requirements-spec、原 13 題/6網站案例、EP-01/02/07 SOURCE_READ。未取得真正 review export，未執行交接 CLI、不製造批准旗標。
- 建議網站限定公開合成資料、localhost、匿名讀者/兩作者/編輯，草稿→送審→退回/核准→另行發布→修訂/下架；舊公開版不隨私稿變更。資料模型/交易/權限/驗收及技術取捨先提案。只更新原訓練主檔/決策與 review 規格文件，不寫網站程式、不自動部署或升格案例，不改正式 main/Release 或外部專案。
- NEXT_ACTION: 等使用者真實逐項編輯或確認整份 WEB-EDITORIAL-01/v0.1（R01–R13/A01–A07）及獨立候選程式寫入授權 D6；有修改先保存 v0.2 或後續版本與決策證據，核對實際 source/範圍。再 architecture-design/ADR、task-planning、implement-feature、QA/security、部署準備及真實驗收。不把按選項、hash、local review 當授權。未確認不進入施工；無付費模型或本地模型前置。

### 2026-11-15｜NATIVE-MATURITY-012-REVIEW-HANDOFF：整體網站工程成熟度與規格交接（TD-001）

- 使用者明確要求轉向實際使用成熟度、盤點7專家/12技能/11 EP及近期實證，實作妨礙完整網站工程之最優先缺口。維持 TD-001/002、REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，不自動升格/部署/發布。詳細 [盤點及剩餘驗收路線](training/reviews/2026-11-15-website-engineering-maturity.md)。
- 基準 exact 9384651b6f4243706ff9bfbf19df5afe7c71b29d / CI 43705370942 job 132785180100 success / 418 tests in 39.204s。回讀7角色、catalog 12技能、11 EP、原來源與決策及 website_discovery、website_intake_ui、browser export、engineering_workflow、TEAM_WORKBENCH。EP-01/02/09 SOURCE_READ；角色/技能按需分工而非獨立模型。
- 觀察：原 UI 匯出 local_reviewed_website_draft（原草稿 + 另列決策；明示不批准）；requirements-spec 已要求真正反映接受/修改/拒絕，卻無程式化整併及向下一設計階段交接的契約。比較 A 再寫報名網站/增加合成樣例，不能解決共同上游斷點；B 狹義修補交接（採用）；C 通用自動部署/完整 Agent orchestration，須另具平台能力與授權。此次是新功能補缺，不冒稱已有 RED regression 或實際事故。
- 新 src/website_review_handoff.py（blob 57e82c01244511362c7846333cde8f4bb67b2b31）唯讀精確 export schema、全部13答鍵、重新 build_spec 並 canonical 比對原草稿、逐項 ID/title/choice/text/literal boolean coverage、拒絕空白/重複/錯配/不合法權限。保留 REQ IDs 及原正規化文字（含否定與未決）；accept/modify 用使用者審閱後文字，reject 獨立排除及理由/歷史 proposal；缺答明確 NEEDS_REQUIREMENTS_CLARIFICATION，否則 DESIGN_REVIEW_INPUT_ONLY。canonical review hash + handoff hash，CLI 可 --expected-sha256 比對原先可信 pin；不是簽章或身份/核准證據。所有權限 flags false、construction_permitted=false；下一站 requirements-spec 仍須整合衝突、具體 acceptance、整份正式確認及獨立施工權限。無 workspace/外部寫入或新模型呼叫。
- 原 localhost UI 新 /review-handoff 入口（沿 Host/Origin/token、1 MiB bounded JSON/拒絕 duplicate keys）、final-confirm 後才可點「產生下一階段交接預覽」；結果以純文字呈現，編輯/取消/答案修改清除、epoch 與相同 captured export 防延遲回應。原 JSON 匯出格式相容，CLI 讀同一 export，stdout only，資料由使用者留在合適私人位置。無新公開服務、資料自動保存、正式規格核准或自動部署。
- GREEN exact 560d143bd9db245f263906bc478ad5379b9eab23 / [CI 43705735689](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43705735689) job 132786283387 completed/success，raw 232216 chars，424 tests in 41.273s/OK。6新增方法：6 case exports/拒絕與修改分流、13種 stale/malformed/pin 負例、digest 變更（文/選擇/來源）、零推導/未授權、唯讀 CLI/duplicate JSON/cap、HTTP guarded endpoint。真實 Chromium W101–106 6/6，20推導項，handoff_test=true、原 export/import 與編輯失效同過；EDITABLE-DECISION-BROWSER 12/12、P21-EQUIPMENT-BROWSER PASS。不是獨立模型或真人 UAT、未實際磁碟下載驗收。
- 覆盤：EP-01/02/09 在真實 UI→規格交接接口遷移。改善唯一共通施工前置，不宣稱已完成從需求到產品的所有階段；缺真實語意審查、目標/來源綁定的完整已確認施工規格、實際陌生網站 vertical slice、跨對話只靠原正式產物續作與獨立實際平台/部署驗收。原11 EP、2 DEFAULT+6 OPT_IN、既有 schema/任務池/QA 功能保留。不得拿 hash 或 local flag 當確認；原主檔、決策、EP-01/02、requirements-spec 與入口指南增量更新。
- NEXT_ACTION: 先核對文件 exact CI；使用明示為公開合成/受控的不同完整網站委託，依已確認規格、目標/版本和使用者實際授權做可運作 vertical slice 及實際功能/權限/UI QA、接續證據；先向使用者提出可編輯的具體規格，未確認不開工於新網站。實際外部整合、正式上線、私人資料與平台獨立評測仍另行授權。不重做本次交接或舊缺陷。

### 2026-11-15｜NATIVE-EP-011-SNAPSHOT-FIELD-BOUND：EP-05/08 快照欄位物化與索引排序（TD-001）

- 使用者明確授權在 PR #8 檢查 CSV、SQLite snapshot、報表與資料處理實際缺陷，以 EP-05/08 做最小實作、實測、知識回饋；不重做已通過的 QA oracle 或 task pool。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK；按需 Architect/architecture-design、Developer/debug-and-repair、QA/test-and-acceptance、Learning Evaluator/knowledge-distillation，讀原角色/技能、政策、索引與案例來源。EP-05 主資料驗證/快照/不覆寫；EP-08 跨 DB→Python 物化大小及 query plan；P22-CASE-003（同版本可重現報表）、原 NATIVE-ARCH-005（保留結果的集合式查詢）SOURCE_READ，非 runtime/私人檢索。原 index blob 8431da8f40cad680a7f18b353e159f35c7663c6e。
- 基準 exact a2c88071aba82629566854a2d7dbf87970c9d55a / CI 43704736065 job 132783271508 completed/success，raw 229714 chars，415 tests in 41.005s/OK，原 CSV 中斷復原、SQLite WAL、三代報表證據仍通過。讀 src/p22_file_intake.py（64 KiB 與列數 cap）、src/p22_snapshot_report.py（blob 4cc8830262148a211bc22ce759e255032e29b4d0）、src/p22_report_workflow.py。缺口選定 snapshot 的 metadata LIMIT 2 與 records LIMIT 1001 都在 Python fetchall 後驗欄位；巨型非法 TEXT/BLOB 已物化才拒絕。不是既有合法報表數值錯誤，不聲稱觀察到 OOM 或生產事故。
- RED exact ffa3af7b90d5127830b4b01188a4ae4d374f7eb2 / [CI 43704992532](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43704992532) job 132784045186 completed/failure，raw 103155 chars，417 tests in 50.357s FAILED(failures=6)。真 SQLite row_factory 衡量回 Python 字串字元/BLOB bytes，不是 RSS。metadata revision、record_id、category、state BLOB、quantity BLOB 各 262144；valid-prefix + NUL 的 record_id 為 262153 字元。六個 subcase 的 publish/reconcile 依然拒絕且原資料/成品不變，但欄位物化超界。另 1000 合法筆/UTF-8、UTF-16LE、UTF-16BE/第1001筆拒絕、canonical rows hash 及相同 ZIP 正向方法原已通過。
- 方案 A Python streaming（仍先 materialize 巨型單欄）、B WHERE/LIMIT/filter/truncate（易隱藏非法列或改資料語意）、C SQL 有界 projection + NULL sentinel（採用，不刪列、不改值為合法、不修改 schema/DB）。metadata/quantity typeof integer；文字欄 typeof text + length(CAST AS BLOB)<=16，以容納最長八個 ASCII 字元在 UTF-16 的原儲存編碼、也避免 TEXT length 遇 NUL 截斷；精確正規式/enum/quantity/唯一 revision/row cap 仍由 Python 驗。同 mode=ro/query_only/BEGIN、同一次 snapshot、hash/ZIP/version/排他發布及對帳語意，無新套件。16 是此固定 schema 的編碼 byte bound，非通用 TEXT 長度政策。
- 第一階段 green exact d40fd9f38500cb46c6a318884a4956144631dc60 / [CI 43705098826](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43705098826) job 132784375716 success，raw 230741 chars，417 tests in 42.988s/OK。最大回傳 text/blob field 由 262144/262153 變為 0（metadata）或8（其他仍合法欄位）；並非全程序記憶體量測。測試保留來源 bytes、舊輸出及無 staging；1,000 合法列三編碼 exact hash/ZIP 相同，1,001 拒絕。
- 首版副作用：本輪在隔離本機 SQLite 3.46.1 以帶 records_id 索引的同型 schema，實際 EXPLAIN QUERY PLAN 比較原 SELECT、投影後 ORDER BY alias、保留原排序鍵；原 SCAN records USING INDEX records_id，首版 SCAN records + USE TEMP B-TREE FOR ORDER BY，改良版 SCAN records USING INDEX records_id。故最終改為內部 records.record_id AS sort_id，外層只回傳四個有界欄位，ORDER BY sort_id，保留原排序/索引資格；不要求新增使用者索引。新增同實際 SQL trace 的相對 query plan 回歸；條件於原查詢使用索引時不引入強制暫存排序，非保證所有 planner/schema。
- 最終 GREEN exact 656c34fe580ac57402ff94bc7bc9170325dcb009 / [CI 43705180025](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43705180025) job 132784654510 completed/success，raw 231060 chars，418 tests in 42.547s/OK；3 新方法全 ok，6 subcases 拒絕/有界、三編碼與 1000/1001、P22C-INDEX-PLAN 3.46.1 原/新同 SCAN records USING INDEX records_id。P22C-SNAPSHOT WAL R1 coherent/R2 committed、全部 CI steps、EDITABLE-DECISION-BROWSER 12/12、P21-EQUIPMENT-BROWSER PASS。從基準 diff 僅 src/p22_snapshot_report.py（blob 913acb31e173f2b1ea039a68fb1232a685252ff2）、tests/test_p22_snapshot_report.py（blob cd1a85fd9a3c909caa0a662ce4ba4054af7f823f）。src/p22_file_intake.py、src/p22_report_workflow.py、task pool、bounded QA、workbench_learning corpus 不改。
- 覆盤／限制：把 EP-08 從 latest-head 列數選擇遷移到單欄 bytes/type；預先界定資料跨邊界物化，再做全資料語意驗證（EP-05）。有界 projection 不代表 SQLite native scan/sort/CAST 的 CPU RAM I/O 總資源有界或查詢無延遲，原排序鍵仍可能由 DB 處理巨型值；本輪未測生產/敵意 DB、任意 UTF/SQLite schema、全程 RSS/latency 或 live-source CAS，不聲稱匿名/Windows/斷電。用可信隔離合成 DB 與原功能、同版 CI 證據，不宣稱獨立多 Agent/跨平台/模型增益。原 EP-05/EP-08 交叉引用同一新證據、architecture-design skill、主檔/決策更新；11 EP、2 DEFAULT + 6 OPT_IN 不變，未自動升格。
- NEXT_ACTION: 核對文件版 exact CI，與已驗收程式分開；不重做此欄位物化與 index 修補、舊 oracle 或任務池。優先審查具實證的 EP 知識之非重複升格/實際適用範圍，或選不同尚未解的真實工程缺陷。未獲額外授權不改 main/Release/外部系統或私庫。

### 2026-11-15｜NATIVE-EP-010-ORACLE-BOUNDARY：EP-11 驗收器邊界及資源預算（TD-001）

- 使用者授權原 Draft PR #8 選不同於任務池的未解工程缺陷，優先 EP-05/08/11，實際重現、修復、驗收、知識回饋，不重做通過工作。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK；Developer/debug-and-repair、QA/test-and-acceptance、Learning Evaluator/knowledge-distillation，讀原角色/技能、政策及知識索引。EP-11 為主要知識（host 功能 oracle、資源預算及候選退件）；EP-05 的 evidence hash/版本分離用於更改 oracle，EP-08 不適用（無資料庫查詢或歷史物化問題）。SOURCE_READ 原 index blob 587f450073f5605f128300e8b943cdd93c048b57；非私人案例檢索或獨立子代理。
- 基準 exact 40f44e68a32a2d82aa7ccf3955a7efe9d0acbc5e / CI 43703816110 job 132780473177 completed/success，raw 229107 chars，412 tests in 42.115s/OK。上一輪 recovery fence 已驗收不重做。原 src/p1_restricted_functional.py blob 955b279de16247ae15a538d8d888942e466231ce，公開合法域 existing 0–32 pairs，exact int -10080..10080，3000 interpreter steps/case；舊 12 oracle samples 最大僅 3 pairs，沒有數值端點。缺口是驗收覆蓋，非原解譯器安全限制被繞過。
- 反例：可信 public fixture EXPENSIVE_SOURCE 有多餘三層迴圈，小輸入答對但獨立呼叫同一 bounded interpreter 32 合法不重疊 intervals 實際 STEP_BUDGET；兩個端點錯誤候選在合法相等區間實際回 False（預期 True），舊 evaluate 卻均 PUBLIC_SLICE_PASS。scripted transport 的 REVIEW_READY 使第一版不合格候選取得 0 次退件。並未執行任意 native Python 或真正模型，未觀察外部事故。RED exact 19e9cebe79b213b37648c64655fac004a5590b3c / [CI 43704461951](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43704461951) job 132782453479 raw 101090 chars，415 tests in 45.644s FAILED(failures=4)，3 新方法含2個端點 subcase。
- 方案比較：A 放寬 3000-step guard（不採用，不能解決錯誤答案且破壞資源契約）；B 全域窮舉或任意 native sandbox（不採用，巨大輸入組合、授權/隔離未驗）；C 保留原12固定案例並增加六個必要合法邊界（採用：max-disjoint、max-last-overlap、max-first-overlap、lower-bound-overlap、upper-bound-overlap、full-domain）。固定預期值與候選分離；CONTRACT 新增 public_oracle_version=2、resource_budget，tool tag restricted-b003-intervals-v2，oracle_digest 依原 contract+cases 雜湊自然變更，舊 v1 receipts 仍為歷史，不能借用為 v2。AST allowlist, parsing, interpreter step bound, existing dispatch/rejection/repair semantics 不改。原測試的12個樣本數斷言適配18、新 tag/hash，沒有刪減原案例。
- GREEN exact 3e27e126288825802447d860601d898da54b180e / [CI 43704563695](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43704563695) job 132782754487 completed/success，raw 229713 chars，415 tests in 42.671s/OK；3 新方法全部 ok（含兩端點），18 public cases 正確參考候選成功，昂貴候選拒絕、host 實際退件1次、revision2修復通過且 findings 含 STEP_BUDGET；原所有 workflow steps/EDITABLE-DECISION-BROWSER 12/12/P21-EQUIPMENT-BROWSER PASS。原 source blob 5507d4c4fbede4516228b8da370afca2b26062e7，test blob c89fdd995e5582f4375115ea25f50debfd5ee506；src/p1_dispatch_runner.py ebebbe04930dd3c46e67e873fe6cf0f9f958faf9、src/workbench_learning.py 6390fa05bb2ac56dddb451523a75985aa791b86a 未改，已回讀。
- 覆盤：驗收器本身也應以實際反例驗收，既有安全限制須有合法最大工作量、端點及失敗跨 host 流程覆蓋；正確性和資源邊界都要通過，測試/契約變動需新 oracle 版本與 hash。更新原 EP-11、QA skill、決策、此主檔。仍只18個公開固定樣本，非全域正確性、任意 Python sandbox、實際模型、獨立人審或盲測；無私人庫、外部專案、部署、main/Release 變更，2 DEFAULT+6 OPT_IN 原 corpus 保留，不新增知識卡或自動升格。
- NEXT_ACTION: 核對本證據文件的 exact head/CI，與已驗收程式分開；再以不同領域真實缺陷 (EP-05 或 EP-08) 驗證知識遷移，或整理人審候選升格，勿重做 recovery fence、scope 或此 oracle 邊界修復。無本地模型強制前提。

### 2026-11-15｜NATIVE-EP-009-RECOVERY-FENCE：EP-04 實際遷移——依賴重接與舊 worker 隔離（TD-001）

- 使用者授權以 EP-01–11 選真正未解工程任務、實作、驗收、覆盤，範圍原 Draft PR #8。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK；按需讀 System Lead/task-planning、Developer/debug-and-repair、Security/security-review、QA/test-and-acceptance、Learning Evaluator/knowledge-distillation 原角色/技能與 formal sources。EP-04 主卡（current DAG/revision/復原隔離），EP-03（同庫拒絕原子性與唯讀憑據）、EP-09（業務狀態守門先於寫入）輔助；其餘八卡不強制套用。SOURCE_READ 原 index blob 0c0a5c7d0bf06e2c5475e7c7e3aa51dea29f1ad0；無 runtime retrieval、私人引用或獨立子代理。
- 基準 4c0771394ae7339ce53ab4bc094aff2fd44c39b0 / CI 43703079220/job 132778228179 raw 227947 chars，406 tests in 43.951s/OK。並行 scope repair 44387d791df6c892dc0352be71f7aee1c77727aa / CI 43703386263/job 132779195199 408/408；保留 NATIVE-EP-008，不歸為本輪成果。
- 根因：原 workbench_tasks._pool 從當前 DAG 計算 RECOVERY_REQUIRED worker 的祖先 recovery_blockers；revise(deps=...) 可重接其祖先，讓舊上游保護消失，與 extend_topology 的 active affected worker 拒絕不一致。比較 A 依新圖重算（已知失敗，不採用）、B 保存舊/新完整資源圖與遷移（有意義但需 schema/歷史及外部資源另驗，暫不採用）、C 沿既有拓撲守門，真正改邊且受影響節點 RUNNING/RECOVERY_REQUIRED 時拒絕整筆（採用）。同一 BEGIN IMMEDIATE、驗證圖及 affected closure 後、任務/需求 artifact/event 寫入前檢查；改入邊不改該節點下游集合，集合相同的 deps 或單純內容修訂維持原失效及復原路徑。無 schema、資料遷移、外部操作。
- RED：tests/test_task_revision.py blob 6d679fbad924402e0b6a469a12472226ca2f550a、tests/test_bound_artifacts.py blob b3dffa9bb7bf34e27edb20eb99b6ab242f93f116；exact 6ed0c60d58246c65f84559edfeaf25a858cae42b / CI 43703424124/job 132779499998 completed/failure，raw 97429 chars，412 tests in 40.043s FAILED(failures=3)。實際 old ancestor fence lost: spec blockers=[], next_ready=['other', 'spec']；直接 running edit 及 combined root graph edit 未拒絕；相同 deps 內容修訂原已通過。未發生真實外部事故。
- GREEN：a55f0c99c382f4326fc48865f19c76131832283b / [CI 43703631052](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43703631052) / job 132779930593 completed/success，raw 229106 chars，412 tests in 42.650s/OK。原 src/workbench_tasks.py blob cd452201d0c0daa53759fb5d259ab2644995b938，7 行新增、原兩 test blobs 不變，四項新方法全 ok；確認拒絕前後 task/event/artifact/DB bytes 不變及 receipt NOT_OBSERVED，recover 後合法修訂、獨立工作與正常內容修訂可繼續。原所有 CI steps、EDITABLE-DECISION-BROWSER 12/12、P21-EQUIPMENT-BROWSER PASS。保留並行 EP-008 記錄 commit 9a2560c7ae40d104088d56866ef0310f0b0b9c7d；競寫時以最新 parent 接續，非 force。
- 覆盤：EP-04 由「新增節點」遷移到既有 revise 改邊，EP-03/09 提供交易及守門位置，具同 oracle red/green 實證；不將知識選用自述當獨立評審、模型增益、真多 Agent 或自動檢索。增量更新原 EP-04、task-planning、TEAM_WORKBENCH、原決策，11 卡及 2 DEFAULT/6 OPT_IN 未改數量。不增加第二案例庫或升格。限制：可信同庫新版 API；禁止活躍受影響 worker 改邊，不代表已完整實作任意刪邊/重綁、保存舊資源圖、阻止舊版/direct SQL、修復歷史上已被解除的 fence、確認 OS worker 停止或撤回外部操作。舊庫須另行人工唯讀對帳，不自動推定或修復。未改真私人庫、main/Release、外部專案或部署。
- NEXT_ACTION: 核對本次文件回讀與其 exact CI，與已驗證的程式 SHA 分開；後續選不重複的不同真實工作或進行知識人審，無須重做本缺陷。未獲授權不處理外部或私人庫。

### 2026-11-15｜NATIVE-EP-008：EP 知識索引實際任務遷移——GitHub 專案身分（TD-001）
- 使用者授權在候選 Agent 選不同尚未解的真實工程問題，使用 EP-01–11 索引、角色與技能實作及驗收。範圍只原 PR #8。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK；System Lead/resume-project、Security/security-review、Developer/debug-and-repair、QA/test-and-acceptance、Learning Evaluator/knowledge-distillation（已讀原角色與技能）。不冒稱分身或私人工作台檢索。選 EP-09（輸入/守門順序）與 EP-10（唯讀來源/專案隔離），其他卡未強制使用；source read 原知識索引 blob 0c0a5c7d0bf06e2c5475e7c7e3aa51dea29f1ad0。
- 基準 4c0771394ae7339ce53ab4bc094aff2fd44c39b0 / CI 43703079220/job 132778228179 completed/success，raw 227947 chars，406 tests in 43.951s/OK。實際 GitHub GET repos 原名與全大寫，均回傳 id 1455152922、full_name lily4318/reliable-system-builder-agent；原 src/task_scope.py blob a29cafe71a91236ffd8da7ee1cb5b12b1624ad01 以區分大小寫相等比較，在 apply_agent 可將自身當不同外部專案，亦錯擋合法同名；判定器 advisory，未發生外部越權證據。
- QA 固定同一 13 subcase 的兩個測試方法，red 9adf48529bca0dee7a78c2b844c8caa1e2b77bf9 / CI 43703326898/job 132778987522 completed/failure，raw 107296 chars、408 tests in 42.992s FAILED(failures=9)：自身別名 4 個錯放（PROJECT_READ_ONLY/PATCH_ONLY），原有授權/跨案/權重 gate 4 個錯擋，以及合法外部大小寫 1 個錯擋。其他原測試不删、不重造 oracle。測試 blob 830cf3cfb7e225fd2f705712fafbbdf5b9e703a9。
- Developer 最小修補：先保留原 ASCII 格式/intent/boolean 授權，再比較 agent/target/proposed 的 lower()；不修剪空白、不解析 URL、不推定 rename/redirect、不增加網路呼叫、schema 或外部寫入。原檔 blob c39d8bb4975532a1f74abf4e9c25a0e6d608cf89 / green 44387d791df6c892dc0352be71f7aee1c77727aa；exact CI 43703386263/job 132779195199 completed/success; raw 228286 chars; Ran 408 tests in 38.985s/OK; 兩個新增 methods 均 ok，原品質及安全流程全過。 程式與測試 SHA 回讀已比對。後續同分支有其他任務提交 tests/test_bound_artifacts.py、tests/test_task_revision.py，保留並行工作，整合 HEAD 需獨立 CI，不能借用本輪 408 綠燈。
- 覆盤：原 EP-09/10 增量交叉記錄同一次應用，原 security-review 補資源 ID 與授權隔離；不新增 EP、runtime seed、模型盲測或私人案例。此為實際單 Agent 選用/執行/驗收證據，不證明自動檢索、真獨立多 Agent、跨平台泛化或模型能力增益。正式 main/Release、其他專案、GAS、私人庫未改。獨立人審/正式升格仍未完成。
- NEXT_ACTION: 核對此文件及當時最新 PR exact HEAD CI（與本輪 green SHA 分開）；保留並行任務驗收證據。下一項實際工程任務選不同 EP，或整理人審准入/退回標準，不重做通過的 scope測試或自行升格。

### 2026-11-15｜NATIVE-KNOWLEDGE-007：按任務蒸餾與共用索引（TD-001）

- 使用者本輪明確要求：盤點已通過實際驗收但尚未完整納入技能與案例庫的經驗，整併重複內容，建立按任務選用的知識索引與限制；不重做已完成測試。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，主責 Learning Evaluator（knowledge-distillation / learn-from-feedback）及 System Lead（resume-project），非獨立子代理。
- SOURCE_VERSION: exact prior head 05d123b49860ce0fef772d9cd96dd47d4e79da4d / CI 43702633084 job 132776872828 completed/success；原始日誌 227954 chars，406 tests in 39.910s/OK，7 拓撲方法、原 browser/CLI、privacy/quality 全步驟成功。另讀原始 logs 132748261530（需求 trace 395）、132772332813（latest heads 397）、132775328752（ordered gate 399）、132667997029（document same-oracle 6→10、case retrieval 3/2/1）與最新 406 日誌的 B003、核心確認、公共檢索、P22、有限 host QA 負例。不新增或手動重跑任何已完成的功能測試。
- 原檔盤點：12／12 skills、原 learning policy、START_HERE/AGENTS、原工作台手冊、訓練主檔及決策、src/workbench_learning.py 2 DEFAULT + 6 OPT_IN；舊 knowledge/ENGINEERING_PATTERNS.md 只有 3 概括主題。新增索引 EP-01–11 覆蓋需求 trace/核准內容、交易、任務與產物及拓撲、檔案/快照、DOM/遷移、未決政策、查詢、依序守門、平台隔離、host functional QA。原 case keys 完整保留且對照，P22-CASE-004 跨卡但不重複計數；B003/TASK/P22-CASE-001/NATIVE/有限 host QA 證據透過索引補導航，不自動升格種子。
- COMPLETED: [唯一共用知識索引](../knowledge/ENGINEERING_PATTERNS.md) 原檔整併三概括原則，11 卡具備任務詞、技能 ID、原 case/source/CI、實測方法、限制及狀態。START_HERE/AGENTS 建立按技能/風險讀取入口，knowledge-distillation skill 補公共蒸餾協定，TEAM_WORKBENCH 補 SOURCE_READ/私人檢索界線，原 DECISION_LOG 保留本次決策證據；未改 Python/runtime case pool、私人 DB 或外部專案。
- BLOCKERS: 索引是候選文件型導航，非 public-context 自動檢索或語意模型、非正式 Release；新案例需原 learning-policy 人審、去識別化、適用與重複檢查才可升格。獨立模型能力、跨平台和真私人資料庫未驗；無新增測試需求，GitHub 自動文件 CI 若觸發須單列，不重新計為新增訓練成果。下一步選不同已授權實際任務驗證是否正確選用 EP 卡並保存採用/不適用及實測，或由人審選出值得升格的非重複案例。

### 2026-11-15｜NATIVE-TOPOLOGY-006（使用者明確要求，工程驗收通過；候選未發布）

- 本輪同 SHA 原始 CI 證據：0f4f536d4c3daf05304add614d24e2563b42b1ef / Run 43607088233 / job 132483961970，完整 raw log 214344 chars，351 tests in 39.918s/OK；7 bound artifact、9 revision sync 逐項 ok，全部步驟 PASS。最新基準 a0d2c1cb7d8c16f62c021f334759f023c58f7948 / Run 43702126591/job 132775328752 completed/success，399 tests in 39.528s，malformed stage 與 ordered advisory gate 回歸、editable decision 12/12、equipment browser PASS。沒有上一輪待修 CI 失敗。
- 本輪 REPO_NATIVE / SINGLE_AGENT_ROLE_WORK：以實際已知的 bound pool add 禁令為功能缺口，沿用原 src/workbench_tasks.py、task_artifact_bindings、task_events，不新建主庫。SOURCE_READ P21-CASE-005 交易與受控恢復、P22-CASE-004 版本失效與舊證據隔離；角色按 task-planning / implement-feature / test-and-acceptance 分工（非獨立子代理）。採全快照 CAS、只增節點與邊、唯一 producer/catalog 祖先/DAG/gate 驗證，原子寫入及傳遞失效，拒絕活躍 affected worker，保留其他歷史。原 add 仍拒絕；根需求、刪除與重綁非本次擴充。新增唯讀 extension-status 回讀，明確版本範圍不代表驗收。
- TEST_PLAN: tests/test_topology_extension.py 七項真 SQLite 測試：跨階段失效重驗、非順序批次新增 producer、錯誤圖/版本/權限拒絕、active affected worker、事件失敗回退、多 writer 競寫、真子程序退出及遺失回應；同 SHA CI 已讀回：見下方實際驗收。維持既有原子修訂、artifact 版本及安全測試；不改私人真資料、外部專案或 Release。
- NEXT_ACTION: 查本輪 exact SHA CI 原始日誌；修正實際失敗並回讀。若已接受，依 TD-001 以此經驗處理不同已授權實際工作，不重做相同合成案例；涉及既有 DAG 刪邊、重綁、跨庫或獨立人審另確認。限制：同庫可信新版 API、證據為操作者聲明，無外部原子性/正式核准或真模型盲測。

- **實際驗收（GREEN）**：exact head f060bb5db658d53b7b7a8d40a8d5425ed37c7ac0，Run 43702359542/job 132776289042 completed/success。完整原始日誌 227947 字元，七個 TopologyExtensionTests 方法皆 ok：affected worker isolation、reverse-order batch、DONE cascade、trigger rollback、concurrent CAS and replay、real subprocess cut and lost acknowledgment、invalid graph/binding/gate/CAS。Ran 406 tests in 43.517s/OK。EDITABLE-DECISION-BROWSER 12/12、P21-EQUIPMENT-BROWSER PASS；privacy/policy/independent acceptance/quality gates 全部 success。上一輪 exact CI 無失敗需修；新功能亦無失敗需修。最終實作承接並行文件更新 21cd57c997cdb67f48d766a8fcb97df6af4ea2d2／CI 43702309522 399/399，保留並行工作。實際 commit 五份檔案 blob 回讀相符；未改私人真庫、外部專案、main/Release。合成工程驗收不是獨立模型能力增益。

- 可泛化候選經驗：已完成圖的拓撲變更應與 state、revision、artifact binding、事件憑據原子聯動；證據不足或 active affected worker 時先停，不依變更後的圖解釋舊執行者。新增邊導致的影響以全圖傳遞下游計算；獨立支線保留。receipt 的 current 只比較受影響版本範圍，不代表驗收或授權。待其他實際任務遷移後人審，不自動升格公共有效案例。

### 最新有效訓練優先序（TD-001；取代下方歷史路線的執行優先順序）

**定位：** 不是建立另一個 LLM，而是讓 ChatGPT、Claude、Copilot 或其他已授權平台上的 AI 能按共同的工程角色與技能完成任務。是否可以真正啟用子代理、執行工具及持久化，依平台實際能力。單一模型按角色分工可完成實際工作，但必須標記單 Agent，不得宣稱獨立多代理。

| 優先 | 工作主線 | 可驗收成果 |
|---|---|---|
| 1 | 平台原生任務啟動與需求理解 | 從最新正式來源選擇適用技能與權限，沒有本地模型依賴 |
| 2 | 專業角色、技能及工作空間 | 按需角色與交接；讀實際 SKILL；獨立專案來源、案例與任務狀態 |
| 3 | 真實工作交付、測試與除錯 | 使用已有授權工具實作、驗證與修正實際問題；保留前後版本與日誌 |
| 4 | 覆盤、案例檢索、技能深化與遷移 | 記錄可重現的根因、修復、限制及引用；人審後增量更新，下一個不同任務觀察應用 |
| 5 | 跨平台可用性、獨立能力評測 | 按實際平台能力驗證；同模型/資源的比較與盲測另列、非日常工作門檻 |

以真實授權任務及實際缺陷為優先。無獲授權外部專案時，可在本 Agent repo 完成有實際價值的改進與驗收，不自動接管 Study1 或其他系統。公開 repo 僅保存去識別化、可泛化工程知識；私人工作空間仍需實際授權，不混用個資、研究資料、Secret 或私人日誌。

**覆盤最低證據：** 任務 ID、正式來源及 SHA、選擇的角色/技能及理由、案例 ID/適用判斷、實際產物及驗收、缺陷及根因、改進前後證據、可泛化原理與限制、候選/已核准狀態、下一次應用結果。檢索命中不等於有效遷移；不因單次結果或合成 CI 宣稱模型增益。無工具時標記限制，仍可完成授權範圍內可證實的工作。

**保留能力及選用工具：** 原七專家、十二技能、工作台、任務池及版本失效、候選 QA/安全、受限功能直譯器、案例庫、Ollama runner、公開基準及私人 holdout 協定均保留。Ollama、本地模型安裝、模型權重微調、擴充通用沙箱及獨立推論測試不作必要工作前提。除非有具體評測需求和適用授權，不再反覆要求本機 probe、增加模型執行器、provider 稽核或同類合成案例。

### 2026-11-15｜NATIVE-AUDIT-001 平台原生使用與真實流程修復（TD-001）

- 已讀回七角色及十二技能原文；共通 context/handoff 說明依賴私人工作區，GitHub-only 路徑缺少公開案例檢索及明確交接。實際執行模式 SINGLE_AGENT_ROLE_WORK / REPO_NATIVE：本輪 ChatGPT 使用現有 GitHub 工具完成讀檔、角色/技能選擇、公開案例 SOURCE_READ、原程式修正、回讀與 CI 查核。不是七個獨立子代理。七角色/十二技能可讀不代表自主使用全部技能已驗收。
- 保留原私人 SQLite，依實際授權選 PRIVATE_WORKBENCH / REPO_NATIVE / READ_ONLY。原 AGENTS 共通條款、START_HERE 與 TEAM_WORKBENCH 已更新，所有角色/技能原文暫保留，循根規則；無持久私有位置不得將私人資料寫公開 repo。repo-native 只用正式檔案、精確 SHA、原交接紀錄及 CI，不製造假私人收據。
- 原 src/workbench_learning.py 新增 public_context/public-context，使用原 CASES 及明確 opt-in TRAINING_CASES，原 _terms 詞彙檢索、有限字元、來源與匹配詞；不建立或讀寫私有 DB，不宣稱驗證必要產物、私人退休狀態、授權或保存 citation。私人命令仍要求 workspace。新增兩項回歸測試；中間 CI cancelled，後續 exact code/docs SHA 7cd8085e6fd9f320fea0e0526cb3b2fd6a354af0 的 CI 43691876099/job 132744079996 已驗證 390/390 PASS（43.728s），兩項 PublicContextTest 皆成功；新純文件 SHA 另行查核。
- 實際案例使用：B001/B002 唯讀缺庫經驗用于無 DB 檢索與拒絕 workspace 設計；P22-CASE-004 版本失效原則用于實際 GitHub head/blob 檢查及精確回讀；不移植 SQLite 原子性承諾到 GitHub。詳細證據、檔案 SHA、角色選擇、取捨及未決見 [原決策紀錄的 NATIVE-AUDIT-001](training/DECISION_LOG.md)。候選 lesson NATIVE-CASE-001 已保存，待不同任務的實際遷移及審查，不自動加入有效案例。
- TP-001 僅完成本輪授權的 GitHub 原生工作兼容修正，不升格較廣私人持久化提案；TP-002–005 原狀態不變。下一步核對 exact CI，再用不同真實授權任務驗證接續、技能應用和覆盤；不要求本地模型，不跨案不部署。

### 2026-11-15｜NATIVE-TRANSFER-002：人類確認機制修復與經驗遷移

- 前一輪 exact head 06837374dd38b1a275a5a52fe0c23ce481acaeab，CI 43692011890/job 132744517975 completed/success；390 tests in 40.884s，全步驟成功。此輪按 TD-001 選擇不同既有功能，SINGLE_AGENT_ROLE_WORK / REPO_NATIVE，讀原政策／技能／案例，使用 GitHub 及隔離暫存可信程式測試，沒有私人工作台或獨立子代理。
- 真實缺陷：原 src/human_confirmation.py blob 0bafdfb39c65d35f76383510bfe3df4cdb4218c1，實際確認字串 'false' 得 explicit_confirmation_received=True，確認 A 後重新選 B 仍保留 A confirmed_text。原功能不會真正傳送或授權外部操作，未觀察到外部事故。
- 原則遷移：SOURCE_READ 讀原決策紀錄 NATIVE-CASE-001（保持 candidate）及 opt-in P22-CASE-004/P21-CASE-006；不依賴特定 UI 正規化，將嚴格確認條件置於核心純函式，舊確認隨改選失效；核心自測不等同瀏覽器／真人驗收。這是本 Agent 在不同任務上的有證據實際應用，不是獨立對照增益。
- 測試前後：隔離暫存 source git hash-object 同原 blob，兩項 unittest 方法修復前六個 failures（五個非 bool truthy 及舊確認）；修復後 2/2 OK。修復 source blob a40069b607e5c102c44196baa944f9c2b2c96521 / commit 04724a59287ee94ea3f0b7233fa74ccc65bcdca2，新增 tests/test_human_confirmation.py blob 4b7d9a0323293e721940b299f9038c4ba5db564d / commit f0e3c09a8c8419cdff11f7560f6ebd926be17641，均已回讀。repo 測試改為 from src import；其餘測試內容與暫存測試一致。CI 43692337646 pending；不能宣稱 392 PASS。
- 詳細角色／技能選擇、案例、交接、修復前後及限制見 [原決策紀錄 NATIVE-TRANSFER-002](training/DECISION_LOG.md)。保留 sent=False、approval_granted=False；literal True 不證明實際人類身分或事件。HTML 示範及跨平台、全新對話驗收尚未完成。未修改 main、Release、外部專案、模型或部署；TP-001–005 不升格。

### 2026-11-15｜NATIVE-UI-003：可編輯確認介面、實際 DOM 驗收與技能深化

- 前一輪 exact SHA 887cda09b0ed4fb82e5f1c79367f83e1ddcf32a4 / CI 43692417375/job 132745909270，392 tests in 42.590s/OK，完整工作步驟成功。核心 Python 修復不重做。
- 實際 Chromium 144.0.7559.96 + Playwright，原 HTML blob 65e8b7aae2bb8f047e02419c683424ef22deae10，暫存 git hash-object 相同；file URL 因環境政策阻止，受控離線 page.set_content 執行同原文。原版 10/13，三項失敗：再次編輯未清舊確認、空白按鈕未 disable、空白預覽保留舊確認。根因缺 input handler。修復 blob 45e79f92c86069ed42c092fee248ef35528507a7（commit e085552958b3eed3e1753f35265f2e9368deeaea）同實測，13/13 PASS；另一套真 DOM click/input 12 條固定驗收原 9/12、修復 12/12，重疊不加總。無網路請求或 page errors；非真人 UAT。
- 原 src/website_intake_browser_test.py 新增 run_decision_review（blob 8bf1943b6d38f92a2b620a547792d0b9b6ed8721 / a1f981fa744151aad8614463a24710cd34c2da6e），既有 CI 入口追加 EDITABLE-DECISION-BROWSER，測試用 ephemeral loopback /result 只保留有限布林結果，CSP、Origin、暫存 profile；原產品仍未送出、未授權。新 runner 完整執行尚待 CI，兩套本機 DOM 結果不冒充最新 CI。中間 CI cancelled/in_progress；預期 unittest 392（另瀏覽器驗收不加進數量）。
- 依 NATIVE-CASE-001、P21-CASE-006、P22-CASE-004 做真實瀏覽器及狀態失效遷移；原 QA test-and-acceptance 與 Developer debug-and-repair SKILL 各補強可見狀態、負例、真 DOM、改選/編輯/取消失效與授權分離。詳細實測、選擇、版本及限制見 [原決策紀錄 NATIVE-UI-003](training/DECISION_LOG.md)。無新模型、無私人工作台、無獨立多 Agent；不修改 main/Release、外部網站或部署。NATIVE-CASE-001 尚未升格。

### 2026-11-15｜NATIVE-REQ-004：需求來源一致性、架構交接與技能深化

- 最新上一輪 exact 2563e54ad5779042e575bae94b9fd7d84f2c5fd1 CI 43692897287/job 132747084217 completed/success，392 tests in 40.018s/OK；EDITABLE-DECISION-BROWSER 12/12、actual_browser_dom_events=true、manual_uat_completed/application_transmitted/external_approval_granted=false。NATIVE-UI-003 完整驗收，無待修失敗。
- 選不同真實缺陷：原 src/website_scenario_eval.py 只檢查 sections、欄位數、部分 trace status 與 review 可編輯性，卻可能放行功能/非功能/架構/交付與使用者原答矛盾、重複需求 ID、未決錯置或 review 對錯提案。新增原 tests/test_website_scenario_eval.py 三組方法 11 個負例，red SHA 35b7f837221d7340d467d8a2f27e2d611f27ce50 CI 43693171112/job 132747884653，395 tests in 38.546s，FAILED (failures=11)。
- 對照技術方案：長期單一規範來源＋版本引用能減少副本漂移但需遷移消費端；原 schema 1 明示副本＋逐值對照保相容及小改動（本輪採用）。在原 evaluator 檢查 13 sections、17 明示副本、REQ-1..13 對來源與狀態、unique 提案 title/review question 及 accept/modify 文字一致。不改 generator、六題預期、schema、七項檢查 key 或 UI；不等於語意評審或驗證任意輸入。
- Green exact 52e9d485a199c1c0481f1c0851e8f1d4c4bad08a CI 43693293456/job 132748261530 全步驟成功，raw 225937 chars，395 tests in 38.207s/OK，三新增方法（11 subtests）及原 EDITABLE-DECISION-BROWSER 12/12 PASS。原 requirements-spec、architecture-design SKILL 更新（原檔各保留其他契約）；後續技能/文件整合 CI 另核對。
- REPO_NATIVE/SINGLE_AGENT_ROLE_WORK；SOURCE_READ 既有 P22-CASE-004、NATIVE-CASE-001、P21-CASE-006，分離來源與授權、不同驗收層；詳見 [原決策紀錄 NATIVE-REQ-004](training/DECISION_LOG.md) 的版本、根因、方案、實測、適用限制及交接。未自動升格候選案例或 TP 方案。無本地模型、無私有工作台、無獨立多 Agent、無外部案／main／Release 寫入。下一步核最新 CI，再選不同實際架構缺陷，不重做通過工作。

### 2026-11-15｜NATIVE-ARCH-005：工作台查詢架構、相容性與遷移取捨

- 上一輪 exact 176805ecbeab82d276f7cd0b8936fa6d2d5d780a CI 43693472498/job 132749094059 395 tests in 39.937s/OK、EDITABLE-DECISION-BROWSER 12/12；NATIVE-REQ-004 整合 VERIFIED，無重做。
- 實際缺陷：原 src/team_workbench.py _latest 把所有歷史全文讀入 Python 才挑每類 head。在 SQLite 3.46.1 隔離原 schema 2,400 rows/12 kinds/每筆約16k chars，五次中位數：原 2400 rows、24.787ms、39356642 bytes Python peak；新 grouped MAX(id) + MIN(id) order + PK join 12 rows、0.720ms、200880 bytes；輸出及順序相等、全部歷史保留。資料庫仍掃歷史，不把 Python materialization 數當 DB 掃描量。
- 技術比較：A 原全量，B 集合式查詢（採用）、C B+複合索引（只於隔離庫試驗，未採用）。約 39MB 實體檔 SQLite mode=ro，七次 warm 無 tracing 中位數 15.576/1.949ms，舊新版相同輸出且 DB SHA256 不變；隔離索引 0.341ms、建索引 4.277ms/增加45056 bytes。B 無 schema/資料遷移或外部依賴、可原查詢回退；C 未驗長期寫入放大與正式庫鎖。微基準非整體 Agent 或通用 SLA。
- Red exact 8576dfb93c37f7634a44a04c8cfd0709fad525eb CI 43701076849/job 132772134294，397 tests in 41.130s，301 != 3、FAILED(failures=1)。Green exact 54694806bbb70229572b1f49041cffc9c29a7856 CI 43701094377/job 132772332813，397 tests in 41.945s/OK，兩新增方法與全部 steps pass、原 browser 12/12。保留原 current_artifacts 依賴、交易與歷史。原 architecture-design SKILL 已深化實際量測、相容性與 schema／索引取捨；最新文件整合 CI 另核。
- REPO_NATIVE/SINGLE_AGENT_ROLE_WORK；SOURCE_READ 適用 B001-CASE-001、P22-CASE-003/004、候選 NATIVE-CASE-001；詳細適用理由、原 schema、PoC、版本、CI 及限制在 [原決策紀錄 NATIVE-ARCH-005](training/DECISION_LOG.md)。未讀寫使用者私人庫，未採用新索引，不升格 TP 或正式案例，未發布／跨案。後續核實 exact CI 後轉向不同真實技能需求，不重複已驗微基準。

### 2026-11-15｜NATIVE-ARCH-006：跨角色輸入契約、容錯與依序守門

- 前一輪 exact 7aa08682b73929aeedeb0303b453464ec5293592 CI 43701309713/job 132772849273 completed/success，397 tests in 43.116s/OK，全步驟及 EDITABLE-DECISION-BROWSER 12/12。NATIVE-ARCH-005 整合 VERIFIED。
- 原 engineering_workflow.route(blob cfd0fd118333cd110501b59fc208651d242820b4) stage not in STAGES 未先查字串，對 JSON list/dict 拋 TypeError 而非 HOLD_UNSUPPORTED。實際隔離 Python 同義前段摘錄及三方案 17 組輸入：原 4 exceptions，局部驗證與集中依序 validator chain 17/17 同結果；集中全量預檢原型 16/17 有不同結果，會遮蔽目標/來源/未知寫入及最小唯讀契約。此非完整替代模組或所有集中式架構比較。
- 增原 tests/test_engineering_workflow.py 兩項方法，red 81cfa7e4e551d22b4f8c345558b7e2d2f466f619 CI 43702025465/job 132775022728，399 tests in 38.459s FAILED(errors=4)。採最小原 route 字串型別 guard，保持 prior target/source/write_outcome、缺欄預設、狀態碼及 mutation_permitted=false；不新增依賴、schema、資料遷移。不把缺 write_outcome 預設 NONE 視為已核准最佳政策，另行盤點 caller 才可收緊。
- Green exact a0d2c1cb7d8c16f62c021f334759f023c58f7948 CI 43702126591/job 132775328752 raw 226710 chars，399 tests in 39.528s/OK，兩新增 methods、全部 steps、browser 12/12 成功。原 architecture-design 加輸入 shape、業務與授權分離、依序守門、相容及回退（dcd5783b660b2d2f9edd1f5fefd9d12140c34ac6）。詳細原案例 SOURCE_READ、技術取捨、版本、前後證據與限制見 [原決策紀錄 NATIVE-ARCH-006](training/DECISION_LOG.md)。
- REPO_NATIVE/SINGLE_AGENT_ROLE_WORK，未用私有工作台/模型/外部系統；候選經驗及 TP 提案維持原狀態，未發布。最新純文件 CI 另行確認；不把程式修復當獨立 Agent 能力增益或正式授權。下一輪不重做本缺陷。

### 決策及跨對話接續（TD-002）

- 唯一有效訓練主檔就是本檔；[DECISION_LOG.md](training/DECISION_LOG.md) 增量保存長期討論、使用者決策、取代關係及來源。深入分析可另存 training/reviews/ 並索引，不另造主檔。已存 [2026-11-15 平台原生訓練覆盤](training/reviews/2026-11-15-platform-native-training-review.md)，涵蓋教材、架構選擇、案例學習及既有網站 Agent 的前次比較。TD-002 於本輪由使用者明確再次確認；待確認 TP-001–005 只見原決策紀錄，不是現行施工命令。
- 新對話先讀 START_HERE、AGENTS 及原候選 PR #8 最新 head 的本節與相關決策，再驗證實際狀態。正式使用 main/release 與候選訓練分開。
- 每次重要討論記錄 DISCUSSION/PROPOSED/CONFIRMED；實際修改及驗收另記 IMPLEMENTED/VERIFIED。改原檔並查寫前 SHA、寫後回讀和 exact CI；失敗清楚回報。
- 歷史段落、舊 NEXT_ACTION 與未採用方案保留為證據，不作執行命令。新使用者明確決策須增量更新本節與決策紀錄。跨專案或正式升版另需授權。

### 教材比對與改善方向

參考使用者提供的《AI團隊實戰營_學員包_第一天_11月份(1).zip》第一天的三角色九技能、共用工作空間、品牌手冊、案例卡、靈感/選題、覆盤與學習蒸餾設計。僅記工程適用的概念，不存課程原件、業務素材或個資。七專家與十二技能是工程延伸，不是教材本身的七角色架構。既有工作台有資料儲存與相依檢查，但無實際模型調用；技能指令、公開合成資料及結構化 PASS 不代表自治能力。

| 差異 | 優化建議（待實戰驗證） |
|---|---|
| 角色與技能 | 保留七專家，按任務選擇角色，不強制全員；針對實戰弱點補 references/templates/scripts/examples/tests |
| 主動學習 | 從明確偏好、需求修正、測試失敗、Bug 修復、QA/UAT 退件、有效架構、部署事故形成候選案例；保留證據與適用限制 |
| 技術探索 | 先擴充 architecture-design，必要時增 technical-research；讀官方文件、比較方案、最小 PoC，供開發使用 |
| 記憶檢索 | 延用 SQLite；分使用者、專案、情節/案例、語意/知識、程序/技能；引入任務 ID、相關性/關鍵字、精簡 context；避免跨案混用 |
| 工作任務池 | 持久化需求、改善項目、優先序、依賴與驗收；週期覆盤根據實際成效，不增加無關規則 |
| 蒸餾 | 同 topic 去重不是語意蒸餾；提出可驗證合併與技能改善，保留歷史、經審核後推廣，使用新任務驗證 |
| 實戰評測 | 保留既有結構評分與安全門檻，另量測實際功能、修復、任務完成與遷移；真實多 Agent 需要執行證據 |

### 歷史工程訓練路線（留存既有能力驗收；執行優先序依上方 TD-001）

| 優先序 | 訓練任務 | 驗收 | 狀態 |
|---|---|---|---|
| P0-1 | B001 社區工作坊：需求→規格→架構→DAG→可執行垂直切片→QA；額滿候補、重複報名、需求衝突、未知寫入復原 | 獨立功能正反測、可重現的修復紀錄；公開合成實作與真實 Agent 評測分列 | LOCAL_FUNCTIONAL_PASS / FULL_CI_PASS |
| P0-2 | B001 案例記錄、蒸餾，遷移到 B002 公用設備借用 | 相關案例被實際取用；新任務功能測試，對照有/無經驗和適用限制 | CONTROLLED_TRANSFER_PASS / LOCAL_FUNCTIONAL_PASS / FULL_CI_PASS |
| P1-1 | 主動回饋事件、分層記憶檢索、技能專業深度、技術探索、任務池/覆盤 | 新工作階段重讀、無跨案混用；測試實際檢索與回饋行為 | P1-1a/b FULL_CI_PASS; P1-1c FULL_CI_PASS |
| P1-2 | 專家獨立協作與交接 | 有授權平台才做真子代理；獨立 QA、交接與整合證據；無平台標單 Agent 分工 | P1-2a LOCAL_ROLE_CONTRACT_EXACT_CI_PASS; P1-2b SKILL_CASE_CONTRACT_EXACT_CI_PASS; P1-2c READY_TASK_DISPATCH_CONTRACT_EXACT_CI_PASS; RESTRICTED_B003_HOST_TOOL_EXACT_CI_PASS; OPTIONAL_LOCAL_INFERENCE_NOT_RUN |
| P2-1 | 隔離合成完整系統：前後端、資料庫、權限、後台、預約、復原 | 可操作成品、端到端功能及安全測試 | P2-1a/b/c/d CONTROLLED_FUNCTIONAL_PASS; REAL_CHROMIUM_DOM_PASS; CLI_MIGRATION_RESTART_PASS; FULL_CI_PASS; MANUAL_UAT_NOT_RUN |
| P2-2 | 未見題獨立前後測、語意蒸餾、必要跨平台同步 | 等模型/工具/資源條件、獨立評審、保留失敗；只有需要且授權才同步 | P2-2a CONTROLLED_TRANSFER_AND_EXACT_CI_PASS; P2-2b DISTILL_EXACT_FULL_CI_PASS; P2-2c DISTILL_EXACT_FULL_CI_PASS; P2-2d DISTILL_EXACT_FULL_CI_PASS; TRUE_HOLDOUT_NOT_RUN |

七專家訓練：System Lead 需求與路由/優先排序；Architect 技術比較、資料模型與取捨；Developer 真正實作/除錯；QA/UAT 獨立正反例與瀏覽器；DevOps/SRE CI/CD、部分寫入與復原；Security 最小權限與隱私；Learning Evaluator 記錄、蒸餾、遷移、前後測。

建議獨立實戰評分（尚未核准為正式門檻）：功能25、需求15、除錯15、架構10、自主規劃10、協作10、經驗遷移10、效率5。重大安全/未授權寫入 0 為必要門檻而非可抵銷分數。核心需求覆蓋/核心功能/必要交接目標100%；已有明確偏好不重問；追蹤復發率、修復輪次、成本時間和遷移正確率，先建立真實基準再比較。保留既有正式安全和品質閘。

### 2026-11-14｜P0-1 B001 實際工程訓練紀錄（可供下一輪檢索）

**資料來源：** evaluations/capability/public_tasks.json B001 R1–R4 (blob 0e422d8d36cb1697396dc753fb98304a9b914120)。範圍只限公開合成代號、本機暫存 SQLite；無真人報名、外網、部署或私有資料。當前聊天 Agent 單角色切換開發、QA 與學習分析；未啟動獨立七專家或 repo LLM runner，不是模型權重訓練或獨立評測。

**需求與架構交接（本輪產物）：** R1 最新額滿候補規則優先，R2 同一 applicant 唯一紀錄，R3 未知寫入先唯讀對帳且不自動重送，R4 正反及競寫邊界。SQLite config → capacity-policy + enrollment 唯一約束/依 seq 候補 → request 唯一 token 與結果同交易 → read-only audit。DAG：需求→交易及識別鍵設計→實作→並行及故障測試→缺陷修復→案例記錄。合成設計假設：SYN-* 格式、單工作坊、固定容量，變更需明確遷移；候補依成功提交順序，不含取消、遞補、HTTP/UI、實際 API 或多節點資料庫。相同 token 已知重播回傳原結果；未知結果不得自動呼叫 register；未找到仍須審查。

**實際程式及驗收：**
- src/b001_workshop.py（Git blob 33452b04c431e23bd6ec3eafb1b9d9cdc5242fbf）
- tests/test_b001_workshop.py（Git blob e187b3c71f0672a8cfef57a2b7d32971c6328050）
- 本機命令：python -m unittest discover -s tests -v（隔離暫存目錄僅含此輪兩檔）；初 8/8 PASS；新增缺庫負測後 8 PASS/1 FAIL；修正後 9/9 PASS（0.233 秒）。此為開發者撰寫、實際執行的功能回歸，非獨立人類 QA。
- R1：1 席、8 併行申請→1 ACCEPT / 7 WAITLIST；零容量及無效容量；順序與持久化。
- R2：8 併行同一人→1 ACCEPT / 7 ALREADY；候補重複、token 重播與衝突。
- R3：before_commit 失敗回退；after_commit 回應遺失後唯讀查得 COMMITTED；NOT_FOUND_REVIEW 仍 retry_allowed=false。
- R4：上述正反測與缺庫負測，9 項共通；未測真正 HTTP/遠端故障。
- 兩檔本機 git hash-object 與 GitHub 回讀一致；程式與測試 commit d531eb09798e69003280cc981a20094969d4f381，完整 CI Run 43561619878 查核時 in_progress，不提前宣告成功。

**案例卡 B001-CASE-001｜observed｜SQLite 唯讀復原不應建立檔案**
- 情境：既有 DB 遺失後，執行 reconcile 唯讀查詢。
- 原始錯誤：sqlite3.connect(path) 先建立空檔，即使隨後 PRAGMA query_only=ON；新增 test_readonly_reconcile_missing_database_does_not_create_file 實際 FAIL，assertFalse(self.path.exists()) 得 True。
- 修復：讀取使用 Path.resolve().as_uri()+ "?mode=ro"，uri=True，在連線時禁止建立 DB；保留 query_only 第二層防護。再次測試 9/9 PASS。
- 可遷移知識：在讀取資源前就限制唯讀權限；不要將「讀取操作沒有顯式寫 SQL」視為無副作用。對交易相關狀態及 request ledger 在同一原子交易寫入；以唯一約束及 BEGIN IMMEDIATE 維持單一 SQLite 庫一致性。
- 適用限制：本機 SQLite 案例，不保證其他引擎、遠端 API 或跨機鎖；B002 應重用原理而非盲目複製報名 schema。下一輪優先驗證缺庫唯讀、原子保留/回退、可用量與併發。
- 學習狀態：已保存公開合成案例，未建立使用者私人記憶、未實際執行自動語意蒸餾、未公開宣稱學習遷移成功；B002 尚未實作。此案例依訓練主檔檢索，不冒稱私人 workbench 已執行。

### 2026-11-14｜P0-2 B002 實際工程及案例遷移紀錄

**來源與前置查核：** evaluations/capability/public_tasks.json B002 R1–R4 (blob 0e422d8d36cb1697396dc753fb98304a9b914120)；先讀本檔 B001-CASE-001、B001 實作及測試、architecture-design、implement-feature、test-and-acceptance、knowledge-distillation 技能。B001 程式 commit d531eb09798e69003280cc981a20094969d4f381 CI 43561619878 與文件 commit 0f07a43006857bf915f1ffe70016ab35d899436b CI 43561661130 均 completed/success。main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57 未變。此輪為聊天 Agent 單角色切換實際工程練習，不冒稱獨立子代理/額外模型 runner 或人類盲測。

**需求、方案取捨及交接：** R1 以 stock-reserved 算可用量，R2 整數正量且 SQLite 64-bit 範圍內，R3 並行不超額，R4 失敗/回退可重現。方案比較：先讀取庫存再於另一交易寫入有競爭窗口；單庫 BEGIN IMMEDIATE + 條件式 UPDATE + 唯一 request token 在同交易管理庫存與紀錄，適合此本機合成需求；正式多節點服務需要另行選擇伺服器資料庫或分散式一致性，不假定目前 SQLite 模式能處理跨機網路。元件：availability-service (can_checkout) → reservation-lock (BEGIN IMMEDIATE/guarded UPDATE) → inventory-view (mode=ro) → rollback-log (原子 request ledger；回退後未留部分紀錄)。DAG：需求→設計→取用 B001 案例→實作→正反/並行/故障測試→案例整理。合成假設：單設備庫存池，固定初始庫存及已保留量，SYN-* token 是請求識別而非真人身分，重播相同 token/quantity 回原結果，拒絕結果亦可記錄為已提交請求，但不占庫存；無歸還、取消、多設備種類、日期區間、HTTP/UI 或部署。不是正式產品核准。

**實際遷移與功能驗收：**
- src/b002_equipment.py blob 843a88dd061ab90b165176a5836bfa4bc0f632d5；tests/test_b002_equipment.py blob e714721b4cf40b0fadfd1331022d511a4667897c；兩檔與本機 git hash-object 一致。
- 本機暫存工作目錄 /tmp/b002_training（僅本輪可信合成原始碼與測試），命令 python -m unittest discover -s tests -v，13/13 PASS，0.144 秒；不是完整 repo 測試或獨立人類 QA。B002 兩檔 commit 20c4e85bd6572831ac78a33b56d4344b376b8572，查核時 CI 尚無 run 回傳。後續依實際 PR head 重新查。
- 初始 stock=10, reserved=3, available=7；借 7 成功，追加 1 拒絕；不合法數量（負、零、bool、小數、字串、None、超 64-bit）不得變更資料；8 路不同數量並行，已保留增量不超過 7，ledger 與庫存一致；8 路相同 token 只保留一次 2 件；相同 token 不同數量拒絕。
- 故障注入：after_inventory（更新後、寫 ledger 前）與 before_commit（ledger 後、提交前）均回復 reserved=3，沒有已提交 request；after_commit（回應遺失）唯讀回讀 COMMITTED/RESERVED，資料庫原始位元組一致。NOT_FOUND_REVIEW 不自動重送。
- 直接套用 B001-CASE-001：mode=ro + query_only；進一步讓 reserve 使用 mode=rw（缺庫不自建），create 使用 exclusive xb（拒絕既有資料庫）。缺庫 snapshot/reconcile/reserve 都實際拋出 OperationalError 且不建檔；mode=ro 寫入拒絕。受控 comparator test_reproduce_old_readonly_pattern_then_compare 將連線暫換為舊 sqlite3.connect(path)，實際重現 read-only 路徑意外建檔，再切回修正模式確認不建檔。這是同一測試中的機制比較，不是未看案例的獨立 Agent 或盲態前後測；沒有聲稱 B002 本輪出現未修復失敗或模型整體增分。

**案例卡 B002-CASE-001｜observed｜讀寫與初始化分離，交易中同時保存決定及資源狀態**
- 來源：B001-CASE-001 + B002 13 個本機功能回歸及受控 comparator。
- 萃取：讀取 mode=ro，既有資源修改 mode=rw，初始化獨立且拒絕既有路徑；避免在復原或修改時意外重新建立資源。先將庫存檢查與保留置於同一交易內，使用資源不變量/條件式更新、唯一請求鍵及 ledger，未知結果先查驗不盲目重送。COMMITTED 僅表示請求決定已保存，需檢查 result 區分 RESERVED 與 INSUFFICIENT。
- 證據：test_missing_database_never_created_by_read_or_reserve, test_initialization_is_exclusive, test_read_connection_rejects_mutation, test_reproduce_old_readonly_pattern_then_compare, test_concurrent_variable_quantity, test_concurrent_same_token, 三個 failure/unknown 測試。
- 限制：本機 SQLite/單庫、合成資料、作者測試；故障為刻意注入。初始建立期間若失敗可能留空檔供人工查核，未驗證 process crash/多機/正式遠端服務；拒絕盲目建立或刪除。不取代原 B001 案例，不寫私人工作台或自行發布通用正式知識。
- 學習狀態：經驗已由目前聊天 Agent 在開發前從主檔檢索並於 B002 實作驗證。沒有自動語意檢索、自動蒸餾或真正多 Agent 學習證據；下輪 P1-1 優先將兩張案例變成可按任務取用的測試化技能與 SQLite 選擇性 context，保留歷史並以新任務檢驗引用及適用。

### 2026-11-14｜P1-1a 任務導向記憶、回饋及案例引用實作

**前置來源與查核：** B002 程式 commit 20c4e85bd6572831ac78a33b56d4344b376b8572 CI 43563255803、文件 commit 388bec5a93dd7958956782108895cf577e6d3b3f CI 43563312827 均 completed/success。main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57 未變。先讀本檔 B001-CASE-001/B002-CASE-001、src/team_workbench.py、tests/test_team_workbench.py、config/skill-catalog.json、learn-from-feedback/resume-project 等技能、docs/TEAM_WORKBENCH.md。保留舊工作台與原本 12 項技能、共七角色，不另建競爭記憶庫。

**實作與使用方式：**
- 新增 src/workbench_learning.py (blob 1e93bb77ff3ab052b5cd6711c3bff28e2d74f982)，及 tests/test_workbench_learning.py (blob 692aa96f2ade3aa23c08d0a1a323e99f08ac329e)，程式與測試 commit 4c104a158a525ed88d340e9f6a8aa61bd205de44。兩檔 GitHub 回讀與本地 git hash-object 完全一致；本機原 team_workbench.py blob 4f2362bb3103513002d76176b26ff56bd8f6068d 與 skill-catalog.json blob c099499befb8ab24dfcbcce6dd454164ccca3ddd 亦與原來源一致。
- setup 原地增量建立 learning_cases/learning_events/learning_uses 三表，經明確授權才執行；原 artifacts/memory/resolutions 保留，兩張公開合成案例進既有 memory 與標籤索引，重跑不重複、不復活退休記憶；同名未登錄舊案例先停查。
- context: 根據 task/skill/query 及英文詞/中文雙字詞交集排名；預設 8000 字元與最多 5 筆記憶（可調 256–20000 / 1–20）；只傳必要且有效的前置產物正文，其他列索引、過期正文排除，超過配額明示 NEEDS_FULL_READ；候選與同主題未解衝突僅列 review_candidates，保留證據與 Scope。字元配額只限制正文及證據 payload，不含 JSON metadata；舊工作台仍回傳專案層級最新產物，task ID 不代表逐任務產物版本。
- feedback: test_failure/test_fix/qa_rejection/requirement_change/preference 五類事件均以候選記憶保存；task/session/event_id/來源，重複相同事件去重、同 ID 異內容拒絕；既有 remember/resolve 人審維持不變。此為 Agent 工作流程主動呼叫，非背景自動偵測或自動核准、蒸餾、模型權重更新。
- cite: 保存 task/session/skill/query/memory_id/decision/evidence，重算可選案例以拒絕無關、退休、候選或衝突案例。區分 applied 與 not_applicable，操作者宣告不是獨立執行證據；history 依 task 讀前後 session 紀錄。context/history mode=ro，不意外建缺庫或隱式遷移。
- AGENTS.md commit ada4cbe02c54d89cccd8de07663716bcff64ebb6；docs/TEAM_WORKBENCH.md commit 784a87ca86cc6657593bf3975bae2474a33aab78，分別接入全技能工作流程及實際 CLI/JSON 操作範例。兩者全文回讀一致。未改正式 main、正式 Release、外部專案或私有資料。

**實際驗收：** 暫存目錄 /tmp/p11_training，僅含回讀一致的舊工作台與 catalog、本輪可信新程式/測試。命令 python -m unittest discover -s tests -v；初 10/10 PASS (1.489s)，增 SYN-REPORT 實際案例遷移試驗後 11/11 PASS (1.619s)，本輪未觀察到失敗；不是整個 repository CI 或獨立人類 QA。11 項：setup 重跑、查詢排名/無關排除、Context 限額/過期規格、回饋去重/衝突、偏好不自動採用、新 Python 子程序讀回歷史和案例、拒絕無關或退休引用、唯讀與缺庫、專案隔離、限額/未 setup、報表缺庫復原實際應用。原工作台/cases 既有全套回歸待同 SHA CI；程式 CI 43564186355 查核時 in_progress，指南 CI 43564264957 pending。

**新任務及新工作階段證據：** SYN-LAB-3 查詢 SQLite 唯讀 缺庫 transaction inventory concurrency，自動排名 B002-CASE-001、B001-CASE-001；排除 CSS 排版，不相關 astronomy 查詢零命中；使用 subprocess.run 啟動獨立 Python 程序的 CLI，從同一 SQLite 檔讀回前 session 引用及同一案例，第二 session 記錄不適用，另一 task 無紀錄。另 SYN-REPORT 合成報表復原任務由詞彙檢索選 B001，真正以 SQLite mode=ro 開啟不存在的來源，OperationalError 且無新檔；記錄 applied 引用及 test_fix candidate。這是開發者編寫的功能回歸及獨立 Python 程序讀回，不是陌生模型盲測、真實 ChatGPT 新對話自動工作或七 Agent 協作。兩張案例之工程原理已實際應用至工作台唯讀設計，但並未證明模型會自主檢索或判斷語意。

**待辦與限制：** 尚無自動事件監聽、語意/向量檢索、逐任務產物分支、實際跨平台同步、獨立真人審查、真實 LLM runner、持久任務池或技術研究技能完整驗收；僅用臨時合成工作區，未替使用者建立私人工作區。下一優先處理 P1-1 剩餘能力：B003 技術探索與規格未決辨識，追加同庫持久化任務狀態/依賴/驗收及覆盤，使用實際新任務和案例檢索驗證，避免堆疊無關稽核。原 B001/B002 案例正文及歷史狀態保留，最新頂部進度以同版 CI 為準。

### 2026-11-14｜P1-1b B003 技術探索、決策 gate 與持久化任務池

**前置查核與來源：** PR #8 起始 b38f863571bfaae79654f7fd40cc9bb57dd348c4；P1-1a code CI 43564186355、最新文件 CI 43564318315 completed/success。main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57。讀 evaluations/capability/public_tasks.json B003 R1–R4（blob 0e422d8d36cb1697396dc753fb98304a9b914120）、本主檔、task-planning/architecture-design、既有工作台及學習工具。實際本機原 team_workbench.py blob 4f2362bb3103513002d76176b26ff56bd8f6068d、workbench_learning.py blob 1e93bb77ff3ab052b5cd6711c3bff28e2d74f982、catalog blob c099499befb8ab24dfcbcce6dd454164ccca3ddd、既有測試 blob 692aa96f2ade3aa23c08d0a1a323e99f08ac329e。此次單聊天 Agent 角色切換，不是真實獨立多 Agent、未見題或模型訓練。

**需求辨識及技術探索：** R1 半開整數分鐘區間端點相接不重疊；R2 非法時段不可視為有效；R3 先釐清未決政策；R4 正反例。未決 D1 為錯誤輸入的產品/UI 政策；跨日、時間範圍、日期/時區未在原題規定。合成原型假設 list/tuple 二元素、真整數（不接受 bool）、start<end；不限定日期或時區，INVALID 是原型內部狀態，has_overlap 對 INVALID fail-closed，不表示已確認錯誤 UI 文案。任務規劃先保存 D1，不阻塞可隔離驗收的 core，正式 UI gate 持續 OPEN。技術比較：單次線性檢查 O(n)，排序後提前停止 O(n log n) 含每次排序成本；小範圍離散分鐘集合 oracle 僅作驗證，非大範圍正式方案。以 0..6 端點所有21個合法區間的三重組合（9,261）比對兩方法與 oracle；兩種皆一致，採低複雜度線性方案，保留排序 PoC。未調用外部研究來源或做實際大型基準；不宣稱普遍性能優勢。

**實作及實際驗收：**
- src/b003_shifts.py blob 82a02ed80a1e4286d9c0b26a8ba6106a61802b2b；src/workbench_tasks.py blob 4ff853335f1a84e66f31c7b07c55369ca7fc5ae6；tests/test_b003_and_tasks.py blob 90cac2efa37ec7ba45a1c66cf0daa1cc653b7368。GitHub 三檔與本機 git hash-object 一致。source/test commit adddfe3bf8c13cbaf7f0ed1d238bb887da5a21f3，CI 43566849542 查核時 in_progress。
- 同一授權 workbench.sqlite3 明確 setup 新增 task_pool/task_decisions/task_events；add 先確認依賴/decision ID 已存在、拒絕循環與無驗收；review 真正 mode=ro 取得依賴、next_ready、running_review、全部決策內容與來源、未決問題、驗收次數、失敗及歷史；start 原子領取，8 路並行只1成功；finish 必須全 checks PASS/FAIL 與證據，失敗退待辦且保留事件，未通過不解鎖下游。resume 需舊 owner readback、明確確認及證據，舊 session 不可再 finish；決策 resolve 需明確確認、答案及來源，不覆蓋歷史、不授權外部操作。任務依賴/已完成狀態目前不可動態修改或重開，尚未實作依賴變更後失效傳遞、完整逐任務 artifact 版本，以及自動排程；resume 的確認是操作者聲明，不會自動驗證舊程序已結束。
- 本機 /tmp/p11b_training（可信合成源碼，原工作台/學習模組/catalog 雜湊相同）python -m unittest discover -s tests -v；初 20/20 (9新+11既有) PASS 2.500s，審查後補已決政策答案/來源回讀及中斷任務明確 resume，新增負例及回歸後 21/21 (10新+11既有) PASS 2.443s。未觀察到初版測試失敗；上述為審查發現的補強。新測試含端點/重疊、非法 fail-closed、PoC oracle、DAG/未決 gate、驗收失敗及重試/owner、跨程序唯讀重讀、中斷接續/舊 owner 拒絕、8路競寫、原記憶/案例相容及缺庫負測、專案隔離。
- 另外執行實際合成 B003 三 stage（tempfile.TemporaryDirectory）：session-1 B003-spec R3 PASS（依原題記錄未決 D1）；session-2 B003-core R1/R2/R4 PASS（實際 subprocess 重新執行21個測試）；session-3 獨立 Python CLI review 回讀 completed=2、attempts=2、failed_attempts=0、next_ready=[]、B003-ui PENDING blocked_by=[B003-D1]、D1 answer/source=null。原 DB bytes 完全不變。另以學習工具 query SQLite 唯讀 缺庫 recovery reconcile 取得 B001-CASE-001，於相同暫存工作區保存 applied 引用及證據，history 回讀一致；未建正式私人庫。這驗證新程序與真實功能操作，非真實 ChatGPT 跨對話自主調用。單元測試中模擬 D1 confirmed=true 只驗證機制，從未成為真實產品核准。
- 更新 .agents/skills/architecture-design/SKILL.md (aa89182cd3d0496a2fe25d08050597b824459e4c)、task-planning/SKILL.md (af732a79936dfe9ca84904f75aea74f206d2fa4a)、resume-project/SKILL.md (245848f568b307bca27759c0fcb330c263751229)、docs/TEAM_WORKBENCH.md (0460c0dc6e895069d9e8fd17047bc91e0294de9a)，全部全文回讀一致。保留原工作台及七角色/12技能，未改 main、Release 或外部專案。

**案例 B003-CASE-001｜observed｜產品政策未決與可測原型分離：** 已知區間規則可執行測試；對不明確產品錯誤政策，先在持久任務池記問題/依賴，不將內部 INVALID 決策當正式 UI。使用有限域 oracle 比較兩方法，明確記錄適用邊界。前一 session 的未決狀態、實測驗收及決策來源必須隨接續重讀；中斷任務不得因聊天切換自動接管。證據：B003 10 項新測試、21/21 本機回歸、三 stage 2/3 DONE 且 UI 尚 pending；已記本主檔，不自動提升記憶基礎或加入私人工作區種子。限制：合成原型、不含日期/時區、實際排班 UI、真人審核、獨立子 Agent。可於後續完整系統設計採用適用原則。

### 2026-11-14｜P2-1a 設備借用網站整合實戰（第一個切片）

**前置來源及範圍：** PR #8 起始 56e72db9e443c24b8b800e72dceb9abac7266cff，P1-1b code CI 43566849542、最新主檔 CI 43567003958 均 completed/success。main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57，release/current_release.yaml blob 6babe416f2ed652509b44d90d3eb98637a0886f3 未授權正式升版。以使用者 P2-1 合成訓練指令、B002 實測案例、原工作台為基礎；自訂獨立合成實戰規格，非外部專案或已核准產品規格，不代替新網站真人訪談/正式授權。

**需求與取捨：** Python stdlib HTML/HTTP + 本機 SQLite，減少訓練外部服務依賴；固定10件設備單庫存池，借用1–10件，兩個合成會員與一個合成管理員，會員能看自己的申請及可用庫存；管理員只讀全體申請，不可借用。臨時帳密每次服務啟動隨機產生，記憶體 session 30分鐘、登出刪除；重啟不保留 session。非正式產品，不含註冊、真實帳號、密碼資料庫、歸還/取消、庫存編輯、日期/多設備、正式 HTTPS/限流/生產維運。服務硬綁 127.0.0.1，不允許外網/真實收件。不保存臨時憑證輸出至 repo；只以臨時合成 DB 執行。

**實際可執行成果：** src/p21_equipment_site.py blob 28c38042df6bf60c5dea9c6fca7e2125594f9956、tests/test_p21_equipment_site.py blob 00a54e3a66837d1ff3f332ac2e08ec1f882c614e；均與本機 git hash-object 一致，程式/測試 commit c5accaab8a60ffd1e3b05c0c6f586768896a7198，CI 43567839044 查核時 pending。HTML login/dashboard/reserve/logout/admin；HTTP 依 Host/Origin/session/role/CSRF 檢查，Cookie HttpOnly/SameSite=Strict、CSP、no-store、HTML escape、SQL參數化、限制輸入與長度。資料庫獨立初始化 exclusive xb、查詢 mode=ro、更新 mode=rw；BEGIN IMMEDIATE、條件 UPDATE、(owner,token) 唯一 request ledger 同一交易。相同 payload/token 重播回原決定，變更數量拒絕；未知 SQLite 結果回503並要求先看唯讀 dashboard，拒絕自動重送。管理員只有檢視，不宣稱完整管理 CRUD 或全面安全。

**重現命令（已授權本機合成環境）：**
- Repo 根目錄執行 `python -m unittest discover -s tests -p test_p21_equipment_site.py -v`。
- 手動啟動：Windows PowerShell 選獨立、空的合成資料夾，使用新檔路徑，例如 `py -3 -m src.p21_equipment_site --database "$env:TEMP/agent-p21-synthetic-demo.sqlite" --initialize --port 8765`（若檔已存在，不覆蓋；選新的路徑，或明確要續作時才省略 --initialize）。只能在有權允許 loopback 的環境，開啟程式輸出的 127.0.0.1 URL；使用本程序產生的臨時合成憑證，勿貼到公開 repo／日誌，停止用 Ctrl+C。會員登入後 Dashboard → Quantity → Reserve → Dashboard；管理員登入後開啟 /admin，查可用量及全體合成記錄；測登出、另一會員不可見他人 token、會員不可訪問 /admin。不得為了測試修改或繞過環境安全政策。手動操作尚未實測。

**功能與安全驗收（實際）：** 暫存 /tmp/p21_training，Python 3.13.5，`python -m unittest discover -s tests -v` 6/6 PASS（3.080s），後續工作台演練重新以獨立 Python subprocess 跑 6/6 PASS。測試真的啟動 ThreadingHTTPServer 並透過 http.client 實際 HTTP、SQLite 查詢/寫入。六項：會員登入/借用/本人列表/他人隔離/管理員全體唯讀/庫存不足；未登入401、錯密碼401、會員進管理401/403、Origin/Host/CSRF 拒絕、管理員不可借；重複 token 不重扣、變更數量/冒充 owner拒絕；8路並行每次3件，3件申請成功、5件庫存不足，總保留9；注入庫存更新後拋錯回退且 ledger 無殘留，唯讀回查檔案位元組一致，缺庫GET/POST 503且不建檔；無效數量/注入字串拒絕、登出/session到期拒絕。這是作者撰寫實際 HTTP 端到端測試，不是獨立 QA/瀏覽器 DOM UAT。
- 實際 Chromium/Playwright 測試已嘗試，啟動瀏覽器後首個 Page.goto 到 127.0.0.1 隨機 port 失敗：net::ERR_BLOCKED_BY_ADMINISTRATOR。未繞過政策，未完成任何 DOM 表單步驟。BROWSER_ENV_BLOCKED，不能以 HTTP PASS 取代瀏覽器 PASS。下輪可在明確允許的既有候選 CI/本機測試環境建立可重現瀏覽器驗收；無需付費 API 或外部部署。

**同庫工作台實際演練與七角色產物：** 原 team_workbench.py、workbench_learning.py、workbench_tasks.py 本機 blobs 與 GitHub 前版相同（4f2362bb3103513002d76176b26ff56bd8f6068d、1e93bb77ff3ab052b5cd6711c3bff28e2d74f982、4ff853335f1a84e66f31c7b07c55369ca7fc5ae6）。以 TemporaryDirectory 建獨立合成工作台，明確 setup；handoff 實際保存 requirements、specification、architecture、plan、implementation、qa、security-review、learning-note、deployment-plan 共9類產物，最後以 context 回讀。七角色為當前聊天 Agent 按工作方法切換，沒有實際啟動獨立子 Agent。SRE 只交付到本機限制及停機/發布禁止之計畫，並未部署。
- 任務池 spec/design/build/qa DONE；browser PENDING（失敗事件記錄環境阻擋），release PENDING blocked_by browser,D1（另行外部部署禁止 gate）。三階段 s1/s2/s3，5次驗收，1次FAIL，4/6 DONE。新 Python CLI review 讀回 next_ready=[browser]，DB bytes 不變；未建立使用者正式私人庫。
- query SQLite transaction inventory concurrency rollback idempotency ledger recovery reconcile mode=ro → B002-CASE-001、B001-CASE-001（實際檢索）。兩者以 cite applied 記錄 HTTP rollback/readonly/concurrent test 證據並回讀；feedback test_failure 將 Chromium 環境阻擋保存候選記錄。B003 未決 UI/發布 gate 原則取自主檔，未冒稱由 seed 自動找出 B003。
- P21-CASE-001 候選學習：單機核心交易原先通過不代表整合權限與 UI 已通過；網頁必須在 HTTP 層從 session 決定 owner，不接受表單的角色/owner；ledger 唯一鍵以 owner+token 避免跨帳號讀寫；分開記 HTTP 與瀏覽器驗收，環境阻擋不可視為產品通過或繞過安全。證據上述6測試與1瀏覽器阻擋；本機合成適用，非全面生產資安審計/獨立盲測，未自動升格公共正式規則。以下 P2-1b 優先完成瀏覽器與管理作業切片、追加安全負測和可重複工作台演練，不擴張無關稽核。

### 2026-11-14｜P1-1c 任務池修訂失效、重開及跨階段復原（使用者指定加強）

**前置查核：** 最新候選起始 df58c6613cafaeddfdfb79a08f1508166ddb0622；P1-1b source/test adddfe3bf8c13cbaf7f0ed1d238bb887da5a21f3 CI 43566849542、最終 56e72db9e443c24b8b800e72dceb9abac7266cff CI 43567003958；P2-1a source/test c5accaab8a60ffd1e3b05c0c6f586768896a7198 CI 43567839044、最新 df58c66 CI 43567913525，四者均 completed/success。原 workbench_tasks.py blob 4ff853335f1a84e66f31c7b07c55369ca7fc5ae6 及本機 team_workbench/learning/catalog/B003 tests 與 GitHub 狀態一致。依使用者指定優先加強現有任務池，不回退 P2-1a、不同步外部專案。P1-1b 的歷史限制「尚未實作重開、依賴修改和失效傳遞」由本節實作更新。

**實際缺陷及修正：** 舊版 test_legacy_session_reuse_is_rejected 在失敗驗收回 PENDING 後，以相同 session 再 start，本應拒絕但實際成功，1/1 FAIL（AssertionError: ValueError not raised）。此為同 task 舊 session 可能重新成為持有者的風險。新實作禁止 START/RESUME 歷史中的 task+session 重用，以 revision（初始1、受影響任務每次+1）、原有 SQLite BEGIN IMMEDIATE、當前 state/session 同時守門；revision>1 時 start/resume/finish 必須提供匹配 expected_revision（revision=1 暫保原呼叫相容）。已完成的驗收歷史不刪除、不授權任何外部操作。
- revise 必須帶匹配的 expected_revision、明確 confirmed、來源/evidence；可增量改 title/deps/gates/checks，或只重開重驗。拒絕未知依賴/gate、循環/空驗收；從最上游向傳遞下游原子更新 revision 與狀態，DONE/PENDING→PENDING、RUNNING/RECOVERY_REQUIRED→RECOVERY_REQUIRED，保留原持有者及事件。無關獨立分支不更新。新增 REVISE/INVALIDATE 事件含舊/新 revision、狀態、持有者、根任務修訂前後定義。新 PASS/FAIL results 包含 revision/checks（舊事件原樣保留）。
- RECOVERY_REQUIRED 禁止舊 session finish/resume；依目前 DAG 的 recovery_blockers 阻止未查清失效下游時重新啟動相關上游。recover 需核對相同 revision/舊 session，確認舊操作者停止與部分操作已處理，帶新 reviewer session 與證據；只釋放 PENDING，不能復活舊 PASS。未失效 RUNNING 仍可明確 review/resume 至新且未用過的 session。review 真正 mode=ro、列 recovery_review、recovery_blockers、revision 以及歷史。既有已決政策不直接覆蓋，新政策另建 decision/gate。
- setup 在同一庫原地增加 revision 欄位，保留原任務/記憶/歷史；舊 RUNNING 遷移為 RECOVERY_REQUIRED/revision2，追加 MIGRATION_FENCE；重跑不重複。升級前備份並停止舊操作程序，不支援新版/舊版程式混寫同庫。未修改使用者真實私人庫。

**執行及證據：**
- src/workbench_tasks.py blob 24bd30557271aa2c39b907ed0b494bb28046acf8、tests/test_task_revision.py blob 801608abc6ee9000e86989212540f38bbd899348，GitHub 與本機 git hash-object 一致；source/test commit 19d11e2d5b82e4a66ca87c4b4b9034d1496f6acc。暫存 /tmp/p11c_training 使用 /tmp/p11b_training 舊源碼及測試（原檔雜湊已核對）；python -m unittest discover -s tests -v 最終35/35 PASS（7.386秒，14新增+21既有B003/learning回歸；非完整repo本地回歸或獨立人類QA）。開發中31項測試曾因同優先級預期順序誤寫為 qa,other，實際排序為 other,qa，修正測試預期後與新增 recovery blocker 得33/33，加入注入回退與真實程序中斷測試後35/35。保留實際舊版缺陷測試，不刪減驗收。
- 14新增涵蓋：舊 session 重用；連鎖重開且獨立分支保留；RUNNING 下游隔離/復原/阻止相關上游；過期 revision 和 ABA；非法 DAG/gate/無確認原子拒絕；8路同 revision 修改僅1成功；finish 與 revise 競寫不留過期 DONE；8路 resume 僅1成功且原 owner 被拒；新程序唯讀重讀；模擬舊 schema 遷移；3個真正 CLI 程序同時 revise 回傳 0,2,2；重複修訂不釋放隔離的 owner；SQLite 觸發器注入下游寫入失敗後整體回退、所有狀態與歷史一致；實際啟動 CLI 領取後退出、新程序確認接續、過期完成請求 exit2、有效完成 exit0。
- 另行真實跨版本演練：使用原 /tmp/p11b_training CLI 建立合成庫 spec DONE / build RUNNING，三筆舊事件；新 CLI setup 後 spec DONE rev1 / build RECOVERY_REQUIRED rev2，舊3事件逐筆一致，新增 MIGRATION_FENCE；確認舊 subprocess 已退出，recover→start 新 session→finish，最終兩任務 DONE、build rev2。合成目錄自動清理。此為真實本機版本遷移/程序行為，非用戶正式資料庫升級。
- 操作手冊 docs/TEAM_WORKBENCH.md commit 64ae53ec0cb23f5cc63d46060a2897e7c5232aee；task-planning SKILL commit 18577d8b11a987fc59bc83fd6cc1a88c95012faf；resume-project SKILL commit d8ea3eb3425ae7dcf93e3f3c40551d62579cadce；全文回讀一致。code CI 43568659877 查核時 in_progress，最終以實際最新 SHA 重新查核。

**案例 TASK-CASE-001｜observed｜需求修訂必須使舊驗收與舊寫入者失效：** 用當前 revision + 單次任務 session + transaction 守門，而非只用 session 字串；留存先前結果，不把歷史 PASS 當目前版本合格。失效執行者不可直接復活；先停止/對帳並 recover 後從正確前置依賴重驗。適用證據為上述14項本機功能負向測試與真實跨版本演練。這是候選訓練案例，不自動升級為正式 Release/私人記憶。**限制：** 修改需求文件或 handoff 不會自動觸發 revise；操作者須依正式來源明確呼叫並同步適用產物。SQLite 狀態守門不會終止 OS/外部 GitHub/GAS 或已執行寫入；停止及部分操作證據需外部查核，不得盲目重送。修訂 DAG 時仍需查核舊工作接觸資源及原依賴，不只新圖。未實作分散式租約或混版本保護、逐 task artifact 分支；沒有獨立 Agent/盲測或真實私人庫。P2-1a 瀏覽器阻塞未解除，續作仍按 P2-1b 原方向。


### 2026-11-14｜P2-1b 設備借用生命週期（第一增量，測試結果待核）

**已核前置：** Draft PR #8 起始 04bbf07e015bf16f431eb5d8e5e16db48bdb6cd1；CI 43568793377 completed/success；P1-1c source CI 43568659877 completed/success。延續 B002/P2-1a 與 TASK-CASE-001；不變更外部研究網站、正式 Release 或 main。

**本輪合成規格假設（非正式產品決策）：** 保留原 RESERVE=保留/借出合成語意；會員僅能取消本人 ACTIVE(RESERVED) 項目，管理員僅能標記歸還，整筆釋放、不可部分歸還、不新增實際交付狀態。兩個 terminal 狀態互斥且不可重開。原請求與決定保持不變，另存 lifecycle actor/action_token/owner/target_token/result；交易內依唯一目標約束只釋放一次。相同 actor/action token 及相同 payload 重播原決定，不同 payload 拒絕；已終止/查無/原始不足回 NOT_ACTIVE。本人從 session 決定 owner，不接受會員指定他人；管理員明確目標 owner，不能代取消或借用。原 Host/Origin/CSRF/session guard 保留，頁面顯示原決定、現況、成功操作者與 action ID，僅 ACTIVE 顯示對應操作。未知 SQLite 結果 503 要求唯讀核對，不自動重送。
- src/p21_equipment_site.py：commit 912230bb833f3b772a4708eb6fd255f847eeae8b，blob 78113d8b4b6791dc1c114b1cfc210dc159c382ad，已完整回讀比對。
- tests/test_p21_equipment_site.py：commit 0c0cbc3a93e05b2d5b014c8bb92d9933089af4a1，blob fd39c090affcfbe4094d3cc6d14b88656e487a06，已完整回讀比對。保留原六個測試，附加四個測試：取消/歸還/稽核隔離與重播、未登入/越權/CSRF/跨來源/原不足與 token 衝突、8路 cancel/return 競爭預期只一成功、故障注入回退與缺庫唯讀/不自建。這些是已提交的測試條件，尚非實測 PASS。
- 原有資料庫不做隱式遷移。此候選僅新建獨立合成 DB；舊 schema 啟動/生命週期讀取拒絕，禁止覆蓋舊檔。稽核目前只有成功操作 ledger，尚無時間戳、失敗審計、完整生產稽核政策；沒有實際出入庫、部分歸還、外部部署或真實個資。
- 檢核命令：python -m unittest discover -s tests -p test_p21_equipment_site.py -v；本輪尚無本機執行證據，CI source-only 43570995375 先前 in_progress，新增測試版本 exact CI 待取，禁止用舊版測試或歷史 PASS 替代。瀏覽器政策阻擋未解除；revision-aware 任務池完整演練、真實獨立 Agent 未執行。下一輪先查最新同版本 CI、修復再處理上述缺口。

### 2026-11-14｜P2-1b 第二增量｜故障復原與命名空間驗收

- 起點：PR #8 head 3365297f731afdd7dba2f31508fcb744b6b4c746；CI 43571054944 completed/success，已回讀 verify job 132375323523 的 Offline unit tests、品質安全守門及其他步驟。0c0cbc3 的 run 43571017490 cancelled，不作成功證據；後續含同程式/測試的 head CI 成功。
- 單 Agent 分工（非實際獨立子 Agent），以公開隔離合成程式為實作對象，原 10 個測試保留；tests/test_p21_equipment_site.py commit 4f3e8d9602d0b71ac835cbae0cb603375663ebf1，blob da0ddb42412a1b991bdf17e7aead81e11ca66c64，新增 test_actor_and_owner_token_namespaces（相同 target/action token 的不同 actor/owner 並行、重播及 admin payload conflict）、test_unknown_after_commit_read_only_reconciliation（cancel/return 真交易完成後注入 OperationalError，HTTP 503；GET 對帳無二次 release、庫存零、ledger 唯一且資料庫 bytes 不變）、test_legacy_schema_refuses_lifecycle_without_mutating（舊 schema 避免隱式重建及寫入）。新增測試已遠端回讀，CI 43571651587 exact-SHA CI in_progress/pending。未另聲稱本地執行或瀏覽器 DOM 驗收；故障注入為 synthetic，不是實際網路故障。
- 新發現（靜態原始碼核對，尚未重現）：release 在找不到 ACTIVE 目標時直接回 NOT_ACTIVE，沒有保存負向 token 決定。若先對不存在的目標操作，之後同 owner/target 被建立，再重送同 token 可能轉為成功，與原「相同 payload 重播原決定」契約不一致。先用新合成回歸重現，後續保留成功操作互斥、拒絕記錄和獨立唯讀對帳；不以新測試代替修復。舊 schema 測試只驗證拒絕保護，不等於顯式遷移完成。尚無真實資料、真人 UAT、外部部署、模型自治評測或正式 Release。 

### 2026-11-14｜P2-1b 第三增量｜拒絕決定重播與顯式舊庫遷移

- 起點：PR #8 b9412a02a6b0ebe8f63eecdcafe160f37fc101d8，CI 43571713215 completed/success，保留原13組設備網站測試。現階段僅 Agent 候選分支及暫存合成資料。
- RED：將前版 Store initialize/reserve/release 原方法摘錄至本機隔離暫存 SQLite，取消（member）與歸還（admin）各自重現 NOT_ACTIVE → 建立原本不存在的 4 件借用 → 同 token 變成 CANCELLED/RETURNED、reserved=0，而應仍 NOT_ACTIVE、reserved=4。不是遠端失敗 CI，勿冒稱整個舊版測試套件執行。
- FIX：src/p21_equipment_site.py commit 68206d17298303fa414e3742023cb94677f0989d, blob e09024bf973623f0a664012853c2af279fa72685。選擇獨立 action_attempts (actor,action_token) 的完整合法決定及 payload，保留 lifecycle 成功狀態 (owner,target_token) 唯一約束；同 token 不重新判定、不改原結果，相異 payload 400；庫存、成功 ledger 與新決定同一交易。合法 NOT_ACTIVE 409 也持久化；未授權/非法輸入不當作有效業務決定。dashboard 顯示登入者自身操作決定，UNKNOWN after commit 以唯讀對帳，不自動重送。舊資料庫在正式寫入/生命週期查詢拒絕；原始 basic view 仍可唯讀查看舊庫。
- Migration：兩種原始 user_version=0 合成 schema（P2-1a 兩表、P2-1b 三表）均支援，先停所有舊 writer，明示離線確認；只讀來源 snapshot、integrity_check、表結構、每列合法性與庫存和有效借用相符；保留 requests/lifecycle 歷史、成功 token 決定，寫入同目的檔系統暫存 v1，再完整回讀對帳，以 os.link 排他建立新路徑，不覆蓋來源/既有目的檔。故障 before publish 不留可用半成品；只新增候選庫，不自動啟動/cutover。原來源檔是切換前的回退依據，切換後若新版已有新寫入必須先對帳，不得直接退回舊檔而丟失資料。拒絕 WAL/SHM/journal、未知版本與非合成格式。舊版從未保存的拒絕決定不可追溯；遷移後勿重送舊未明 token，先依已保存狀態唯讀查核。未測驗 power-loss durability 或 Windows 檔案系統；無真資料、正式服務或資料庫寫入。
- 合成使用入口（停止來源舊程序後）：python -m src.p21_equipment_site --database NEW.sqlite --migrate-from OLD.sqlite --confirm-source-offline 。成功只輸出版本/筆數；確認新庫完整性/庫存/歷史後另行啟動候選站：python -m src.p21_equipment_site --database NEW.sqlite 。未知發布結果先唯讀確認目的檔及內容，禁止覆寫或重送。CLI 完整進程測試仍待做；僅 local Store methods 已實測。 
- GREEN 本機：將修復後完整 imports+Store excerpt 從遠端原始碼轉錄，字元/bytes 13780，FNV-1a c555baa8 與遠端一致；本機 py compile 與 6/6 smoke groups PASS：兩種拒絕重播及新 token 正例、8路拒絕競寫/rollback/actor 隔離、兩表遷移、三表歷史成功重播及庫存、offline confirmation/故障回退/no overwrite/invalid inventory/version/sidecar、雙路遷移排他建立。驗證舊庫 bytes 不變、新庫庫存及紀錄；此為 Store 層實測，非整 repo 或 HTTP/瀏覽器完整驗收。
- tests/test_p21_equipment_site.py source+test commit 64a5f2ed8fe5dff429fe38d8edf191c6532b7c51, blob 594e3728837608007c4a92046889c5d679b84a5f。新增3項 HTTP 拒絕決定/失回應/競寫與5項遷移正反測，共21項，原13項未刪，完整 source/test 遠端 blob readback。CI 43576453447 completed/success；不以舊版成功取代本版。 
- CASE P21-CASE-003｜observed (Store local): 冪等契約必須包含合法負向決定；分離 terminal state 與 all accepted action decisions，以 actor 級 token/payload 衝突驗證、原子交易、唯讀對帳避免歷史請求在後續狀態變化中重新執行。資料遷移用原始檔保留+明確離線+快照檢查+新庫稽核+排他發布，不能把版本欄位變更當遷移完成。案例為公開合成訓練紀錄，不聲稱自治模型或獨立專家已驗證。下一步跨階段 revision-aware 工作台演練及允許環境的瀏覽器驗收。

### 2026-11-14｜P2-1 跨階段完整演練：報表需求修訂、交接、復原與重驗

- 起點：Draft PR #8 a16cd7234f529815c9ca670b62c7aa7005248627，CI 43576629567 completed/success；不重做既有設備網站及遷移。使用公開合成資料及 CI 暫存 SQLite；單 Agent 依角色分工，自行制定兩版訓練需求（非使用者正式產品核准），不是獨立模型或人類驗收。
- System Lead/Architect：R1 報表僅有效借用數量、會員只看自己、管理員加總、唯讀；R2 保留 R1 並新增取消/歸還/不足的數量、登入者自身 NOT_ACTIVE 次數、管理員專屬全庫存。使用 Store.view 單一唯讀 snapshot，庫存一致性與資料隔離。沒有新增 HTTP endpoint 或正式產品功能。
- Developer：src/p21_equipment_report.py commit 08fc8098763fa19ee99eb2b5ae62955f0e2cf584 blob ff4a738918fc07eab95b240a59d234053d08228d。report_v1 是刻意保留的可執行基線，report_v2 依新需求新增狀態統計及權限範圍；實際 Store reserve/release 產生 fixture。三角色 v2 驗收：member active=2,cancelled=4,returned=0,insufficient=0,denied=1；member2 active=1,cancelled=0,returned=3,insufficient=8,denied=0；admin active=3,cancelled=4,returned=3,insufficient=8,denied=2,stock=10,reserved=3,available=7。會員沒有整庫存欄位，未知 actor 拒絕，缺庫不建立，設備資料庫 bytes 不變。報表函式本身沒有登入認證，呼叫者須由既有認證邊界提供 actor。 
- 實際工作池及交接演練：建立 intake/spec/arch/plan/impl/qa/security/deploy-plan/activate 九項相依任務，另有獨立 inventory-audit；R1 逐階段交接並回讀實際產物內容及 dependency ID；report_v1 真功能驗收 PASS。子程序實際 start deploy-plan、保存 staged-plan.json（舊 implementation/qa IDs）並 exit 0，不作外部部署。修訂 intake 至 r2 同時使 9 項任務失效；獨立 inventory-audit 仍 DONE/r1。明確另行 handoff 新需求，使六類舊下游產物 current=false；stale handoff、舊 worker finish/resume 皆拒絕。RECOVERY_REQUIRED 未解前阻擋上游；查核子程序 exit 0、回讀 staged ID 並移除隔離暫存檔後 recover；新 Python CLI 進程重新 review 再領取新任務。
- RED/GREEN：執行 report_v1 對新版完整字典驗收，確實 AssertionError（非合成宣告 FAIL）；task pool 記 FAIL、阻擋 QA；新 session 實作 report_v2，實際相同判準 PASS，再執行三角色精確字典、未知 actor、缺庫不建立與 SQLite bytes 不變測試。更新 implementation 及 QA、security、deploy-plan 交接；最終 9 DONE、1 activate PENDING（LIVE 未決）、1 failed_attempt retained、無復原阻塞；舊 implementation/qa artifacts 保留。測試內 role 流程均由固定可信合成測試驅動，非自治多代理。
- Learning Evaluator：實際使用 workbench_learning context 找回 B002-CASE-001，由 report_v2 使用原 Store.view read-only snapshot、庫存不變及一致性約束驗證適用性，記 cite applied；requirement_change/test_failure/test_fix 三筆事件保留 candidate，不將回饋自動升格。history 回讀確認事件及 citation；未將此合成政策當永久個人偏好。
- QA/SRE：tests/test_p21_cross_stage.py commit 9adf5634765b88830d9426c6dd83da1f82b45959 blob f7d5857d3ecd00cace677e8cdd8808481559a338，source/test readback verified. Exact-SHA full CI 43605726496 verify job 132479932899 completed/success；原始 logs 2026-11-14T14:37:07Z 明列 P21-CROSS-STAGE: v1 accepted; 9 invalidated; stopped worker recovered; v1 rejected on v2; v2 accepted; 9 DONE; LIVE blocked; 3 feedback events; B002 case applied；test_full_revision_handoff_recovery_and_revalidation ... ok；Ran 330 tests in 36.170s / OK；Candidate quality baseline and safety gate success. 全部證據為遠端 CI 實際執行，不聲稱額外本機執行（本機 git DNS 不可用）；無真人資料或真實外部操作。
- **P21-CASE-004｜observed｜需求變更後的雙相依鏈與重新驗收**：task revision/state 及 artifact dependency/current 分別有效，但不是同一交易；確認來源變更後兩者皆需修訂並回讀，不能只拿任一 PASS 當施工依據。曾執行但失效 worker 先核實實際停止、盤點部分成果，再 recover；保留舊 PASS 和 FAIL，使用新 revision/session、實際新版測試及最新產物重驗，獨立已驗證工作不重做。適用於本機單工作台合成工程，未驗證中途雙索引同步中斷的自動復原、外部程序停止/寫入回退、真正多 Agent、跨平台、正式部署或真人 UAT。此案例記原訓練主檔，非正式政策自動升級。下一步設備瀏覽器/CLI smoke，之後陌生任務工程遷移。

### 2026-11-14｜P2-1 跨階段一致性：雙索引原子修訂與中斷復原

- 起點：Draft PR #8 f1106ed027b76cf0144f39ebe528367cd205977f，CI 43605933260 completed/success。沿 P21-CASE-004 實際查核同一 SQLite 內 task_pool / artifacts 不同交易的風險，僅隔離合成工作區及本候選分支，未碰使用者私人 DB、正式專案或部署。
- RED：tests/test_workbench_revision_sync.py 實際啟動子程序，以舊 standalone revise 或 handoff 提交單邊後 os._exit(23)。task-first：task revisions 更新、3 項失效，舊 requirements/spec 仍 current、architecture context READY，甚至可重新 handoff 舊內容；artifact-first：spec 過期但四個 task 仍 DONE。原始 CI 日誌兩個 REVISION-SPLIT-RED marker 證實，非純靜態推測。
- 修復：src/team_workbench.py blob a923db7a9e5761b416e7efbbe0a004cb088b6ba1 提取 _handoff_in_transaction；src/workbench_tasks.py blob e58d862dd16e4e364b53f8ece12f918eb025fc52 在 revise 增加 requirement={expected_artifact_id,content,source_ref}；同一 connection/BEGIN IMMEDIATE 核對 task revision 與当前有效根 requirements ID，確認唯一 change session、DAG 合法性，寫入 requirements、task revisions/失效狀態與 root REVISE event 的雙 artifact IDs；任一錯誤全部 rollback。revision-status CLI 以唯讀 snapshot 查 COMMITTED / NOT_OBSERVED、still_current（僅對應根 revision 與最新需求）。不自動重試。已更新完整跨階段案例採用新路徑。
- RECOVERY：兩種既有 split 狀態皆以重新核對兩索引及獨立確認 R2 合成來源，使用當前雙版本及新 session 原子修訂，不猜測哪個索引是真理、不抹除歷史。提交前於 artifact INSERT 後真實 os._exit(23)，兩側保留舊值、integrity_check ok；DB trigger 注入 task event error 同時回退 artifact/revisions/history；完成提交後 os._exit(23)，唯讀 receipt 確認 COMMITTED、bytes 不變，舊版本重送拒絕。四路競爭僅一個 commit，錯 artifact ID/空內容拒絕。
- QA：新增 tests/test_workbench_revision_sync.py 9 項（blob e70731ed46129e74186e55e8e0ae2f2c8576ad2d）；更新 tests/test_p21_cross_stage.py（blob 308c79c91cdbb31c2ed1bf2f8764cce688edb2a4）。Exact code/test head f6ad1e35eaef281a09eec3ce102fffd2e1c35eec；CI 43606395473 job 132481951934 completed/success，raw logs 9 tests ... ok；REVISION-SYNC-GREEN: combined revision, stale guard, receipt, revalidation；兩個 REVISION-SPLIT-RED markers；P21-CROSS-STAGE marker 與 9 DONE / LIVE blocked 保持；Ran 339 tests in 38.776s；品質安全守門 success。較早被取消的 run 43606348140 不作通過證據。本機 GitHub DNS 不可用，沒有聲稱本機整 repo 測試；實際執行證據為 CI。
- 操作手冊 docs/TEAM_WORKBENCH.md blob 9650577e9ee463e1065a65a7b0b6b376ca4a7fa1，明確 root requirement revise+requirement、receipt 唯讀回讀、已 split 的人工來源確認流程及限制，readback verified；guide head 433e7ac53421016d0107d3749e16741bbc27eb1e CI 43606430195 in_progress at this read。
- **P21-CASE-005｜observed｜同資料庫的相依索引變更應原子提交，未知結果先查憑據**：雙版本防競寫，狀態／產物／事件同一交易，使用實際程序退出與錯誤注入驗證，不只測正常路徑；已存在的不一致狀態不能由最新日期或較大 revision 推測正確需求，須獨立確認來源再用新修訂恢復。此為可信合成工程案例，非獨立 Agent 盲測。限根 requirements，standalone API 仍可繞過，尚未全域強制或原子綁定每階段 handoff/finish；未證實跨資料庫、外部服務、舊版混用、Windows/斷電或真正獨立 Agent。下一輪優先設備 UI/CLI 完整實戰及陌生任務經驗遷移，必要時再補 opt-in 強制綁定。

### 2026-11-14｜P2-1b 候選：任務—artifact 版本綁定

- SOURCE_VERSION: PR #8 基準 e3b364ba782c4da52d054c1d0ff9911576b20bbd；保留最新 CLI/瀏覽器工作及 P21-CASE-005 歷史。公開根需求既有 task pool 的 standalone 覆寫拒絕；新增明確 bind-artifacts，核對完整任務 revision、根 ID、catalog 依賴與 DAG；重開受影響 task，保留無關分支及歷史。綁定 PASS 與 artifact CAS/前置 ID 同交易，producer 非 DONE 則產物失效。根修訂只走 combined revise。
- TEST_PLAN: tests/test_bound_artifacts.py 七項負面及跨階段測試；保留舊版本 split 重現，改用歷史寫入方式模擬。基準後 CI 需以新 SHA 讀回，未確認前不得稱成功。
- LAST_VERIFIED_STEP: 基準與正式主檔讀取；候選實作、測試尚待新 SHA CI。NEXT_ACTION: 查 CI 原始日誌與安全守門，修正實際失敗；補拓撲擴充及真正 stage PASS 程序退出。
- BLOCKERS: 綁定須明確採用；受信任新版 API，不防直接 SQL/舊程式混用，不保證語意正確、外部同步或真 Agent 能力。WRITE_OWNER: lily4318；SYNC_STATUS: 原候選分支，不合併 main、不 Release、不改外部專案。

### 2026-11-14｜P2-1d 設備網站真正瀏覽器、CLI 遷移及端到端驗收

- 起點：Draft PR #8 898ea184e31a62403e6ecfa6124bb3566381f1f1，CI 43606595848 completed/success；僅公開合成設備網站與 CI 暫存 SQLite，未碰真人資料、私人工作區、外部服務、正式部署或 Release。本機 Chromium 實際探測 ERR_BLOCKED_BY_ADMINISTRATOR，GitHub DNS 不可解析；採原有 GitHub Actions Chromium 環境，非本機全測或人工 UAT。
- RED：新增 src/p21_equipment_browser_test.py（blob efceea5361fed81d92355ce6633ebf2630a14046），以本機 loopback Chromium/Node CDP 真 DOM 表單事件與頁面導航，接入 src/website_intake_browser_test.py（blob b9c96e177aba41dea7d5a7a78d49c1971fc125f9）原 CI 瀏覽器入口。基線 f7112614f79de0e8ca6a4327c1796a5c861047c0/run 43606845560/job 132483410360 原始日誌：既有六個 intake browser case PASS，equipment 的 native login 出現 Invalid origin。含 CLI 的 e3b364ba782c4da52d054c1d0ff9911576b20bbd/run 43606931057/job 132483727720 同樣失敗，但 343 unit tests OK。先前 HTTP tests 人工指定 Origin，無法發現瀏覽器實際表單政策不相容。
- FIX：0874b68d75b3c1bf00b2c309cfa52d70a5eade02 改 Referrer-Policy: no-referrer → same-origin（原生 POST 的 Origin 可能受 no-referrer 影響，未直接記錄原封包的 Origin 值，不宣稱已捕獲 null）；仍拒絕非完全匹配的 Origin，保留 Host/CSRF/session guard，不放寬授權。1fab759a4dcff17071a6c1c40768a66b1415d580 增加獨立負向測試，null/缺失/外部 Origin 拒絕、有效 same-origin 成功。src/p21_equipment_site.py blob 723cbd45c6d11792e38aa35732b791679950f7a0，tests/test_p21_equipment_site.py blob a105f1b802cb62cfe128b27a8d7e7dade8ddcae3。
- CLI：tests/test_p21_equipment_cli.py（blob 80690617f95277257a4339c55a1602b250ccf3d8）四項以獨立 Python CLI subprocess 實際執行；首次 init/缺庫啟動拒絕/已存在不得覆寫；兩表、三表 legacy → v1 遷移、啟動/登入/唯讀 admin 查詢/停止、原檔 bytes 不變、可從保留舊快照重新遷移；錯參數/缺來源/目的檔存在拒絕；新增借用後重啟新版、舊 session 失效、資料及庫存持久化（舊 3 件、新 5 件）。原始日誌 P21-CLI-CUTOVER 與 P21-CLI-RESTART markers；前置回退限未有新版業務寫入，驗證保留資料快照與再遷移，沒有執行歷史 legacy server binary；新版已有寫入時不得直接退舊檔。
- GREEN：並行任務—artifact 綁定提交整合後 head 0f4f536d4c3daf05304add614d24e2563b42b1ef，已回讀保留上述 5 blobs 及並行工作歷史；CI 43607088233/job 132483961970 completed/success，raw log P21-EQUIPMENT-BROWSER: {"status":"PASS","actual_browser_dom_events":true,"roles":3,"stock":10,"reserved":0,"manual_uat":false}；三角色原生登入/錯誤登入拒絕、借用/取消/歸還、獨立會員資料隔離、管理後台及登出/非法數量/庫存不足測試均成功；4 CLI tests 和 test_native_form_referrer_policy_and_strict_origin ... ok；Ran 351 tests in 39.918s；品質／安全守門 success。取消的 43607050068、43607070881 不算成功；最新整合 head 全 CI 為驗收證據。沒有把並行綁定功能冒稱本輪獨立開發。
- **P21-CASE-006｜observed｜HTTP 正測不能替代真正瀏覽器，遷移成功不能等同可逆回退**：原生瀏覽器安全政策影響標頭與實際流程，應先 RED 背景重現，再保留 fail-closed 安全邊界做最小修復，並回歸正常表單和非法來源。用真正瀏覽器 DOM 與獨立 CLI 程序驗證角色、持久化和資料完整性；遷移與啟停、切換、寫入後復原分開驗收，不以保留舊檔作為 post-write rollback 證明。CI 實際可信合成測試不等同人工 UAT、Windows/斷電、跨資料庫或獨立真模型盲測。下一輪優先移轉工程經驗到陌生任務，保留 concurrent binding 進度及其限制。

### 2026-11-15｜P2-2a 文件版本審閱系統：受控工程經驗遷移及案例庫匯入

- 起點 Draft PR #8 fd71076758d4873344145eff93581824eb466d7d / CI 43607268933 success。自行制定公開合成 CLI 文件審閱需求，非使用者正式產品決策。編輯者新增 immutable version、審閱者核可當前指定版本、發布者只變動本地已核可版本指標；舊內容不覆蓋。可信本地 actor 標籤不是認證服務，不得用於真人文件或實際外部發布。
- 架構與實作：src/p22_document_review.py blob 948deb53c5f0c8abd4b6f17d23eac4af987998a7，commit f747eea3a6d668270e67d5ad0cc887b0856de352；versions/state/approvals/decisions SQLite schema，BEGIN IMMEDIATE，expected revision、actor scoped token+exact payload、合法正負決定與狀態同交易、mode=ro readonly receipt；init 排他、CLI init/action/receipt/snapshot。Baseline 是同作者刻意移除 exact revision approval、negative receipt、atomic commit 三個控制的 ablation，保留正常流程及角色檢查，不是實際無記憶獨立模型。
- 實測：tests/test_p22_document_review.py initial blob ebb58b96ad8cd8e3053666ad76c12ce299157b01，commit 36c03547b84a43c5c41c9aa93388c31839f56041，CI 43666793523 job 132667997029 completed/success。相同十項規格預期值：baseline 6/10，improved 10/10；baseline 失敗 stale_approval / denied_replay / future_revision_replay / fault_atomic，另外 happy/competing_edit (6 workers)/role_guard/token_conflict/readonly_missing/published_history 兩版皆過。原始日誌 P22-TRANSFER marker；新增三組整合測試 ... ok；Ran 354 tests in 37.877s。此為同作者受控方法比較、規格導出 oracle，不是獨立評審、模型增分或陌生私有 holdout。
- 學習與交接：在暫存工作台明確匯入先前 master P21-CASE-003/005/006，實際 learn.task_context 檢索，讀 requirements/spec/architecture/plan，採用 003（否定結果重播）、005（原子 state/receipt），006 判定 not_applicable（此次無瀏覽器／遷移）；保存 citation、實作/QA/security/deployment-plan handoff，兩筆 RED/GREEN feedback 保持 candidate。原始 P22-LEARNING marker 3 retrieved, 2 applied, 1 not_applicable, 2 feedback。P22-CLI：實際子程序完成 edit 後 os._exit(23)，其他程序只讀 receipt、資料 bytes 不變，後續核可和本地發布可在新程序驗證。
- 可重用案例庫：src/workbench_learning.py commit e63dc55a68d698abb5a806d919e65cccc0bc3239 blob 4a23d25f0de3a9fb5421753ed4cfbb636dde50da；預設 CASES 仍 B001/B002，新增 TRAINING_CASES 三份已驗證 P21 案例的標籤/適用限制/來源 CI；需明確 setup(include_training_cases=True)，不自動升格 feedback、不變更使用者私人 DB。CLI 在已授權/已初始化工作區可使用 JSON 參數 {"include_training_cases":true}，命令 python -m src.workbench_learning setup --workspace <workspace> --input <json-file>；同一顯式 setup 可重複而不覆蓋既有或退休案例。整合回歸測試 blob da6cb92fe8a27220838b844cf81df70549a70d76，候選 bfe4299a99833d62c0f6586e8207281a72cb9053 CI 43666877892 in_progress, unit success at this read；default 2→explicit 5、重複匯入、非 boolean 拒絕及實際檢索。新版本驗收不可借用初版 CI。
- **P22-CASE-001｜observed｜版本特定核准與持久否定決定的受控遷移**：新資料版本不繼承舊核准，認證/作者角色與資料版本/操作狀態分開；合法的否定結果也需持久化，未知提交先只讀查核；狀態與稽核事件在同 DB 交易。相同規格 oracle 對 baseline 及 improved 執行，保留反例及已過項，引用不適用案例的理由。適用本地文件審閱 CLI 與相似狀態工作流；不聲稱多文件、網路認證、外部發布、真多 Agent、語意蒸餾或盲測成效。下一步改做資料匯入/驗證/轉換等不同架構之工程任務，擴張方法遷移廣度。

### 2026-11-15｜P2-2b 檔案匯入與可重現轉換（候選，尚待 CI）

- 起點：Draft PR #8 a26bd595115bfb9b425db399c8c91281000484c3，CI 43667013361/job 132668532801 completed/success；原始日誌 354 tests in 37.160s/OK、P22-TRANSFER、P22-LEARNING、P22-CLI，原品質守門成功。先前 opt-in 匯入已包含於同版通過。
- 自行設定公開合成文具數量 CSV 任務（非使用者正式產品規格）：固定 header、唯一 R 四位數 ID、三類固定類別、1–999 數量、UTF-8、64 KiB／1000 列上限、整批拒絕非法資料；固定測試 oracle 為 folder=7,paper=5,pencil=0, rows=3。這不是 SQLite 狀態機，也不是獨立前後測或模型能力增分。
- src/p22_file_intake.py commit 44fdba9d35c1950b671ffb3fa4a4943a71f5c1e9 blob b9dcf906ecabd9df9d25d95f58c323dd0a097f07：解析整份資料後 canonical JSON、input/result SHA256、單一 bundle 保存內容與憑據；同目錄暫存/檔案 fsync/排他 hard link，不覆寫既有輸出。reconcile 僅讀且重新計算完整 bundle；COMMITTED / NOT_OBSERVED / CONFLICT，unknown 禁止盲目重送。只適用受信任本地目錄、穩定輸入及支援 hard link 的檔案系統；未驗證斷電、Windows、敵意目錄或外部系統。
- tests/test_p22_file_intake.py commit 9bc7b39cf9576e3e4f34492e80cd8ff251ac27c0 blob af3cae62fed16fc338ac9cf6924f54e5ec25d483，六組方法：精確 oracle/可重現、14 個無效輸入拒絕、唯讀衝突及發布前故障、八路競寫、獨立程序退出後重新查核、真實工作台匯入與引用交接。預計 P21-CASE-005 僅遷移原子可見性原則（非直接套 SQLite），003 無 actor decision ledger、006 無 browser/migration 判不適用；回饋保持 candidate。程式與測試已由遠端完整讀回；CI 43667672400 pending at check，所有新測試結果仍未確認。不得標為 P22-CASE-002 observed 或已通過。
- WRITE_OWNER: 原 Draft PR #8 候選分支。沒有改 main、正式發布、研究網站、真實資料或外部服務。

### 2026-11-15｜P2-2b 功能驗收、復原邊界與工程蒸餾

- 原始候選為 088c8264d4e622ba3bb09e8212e220c91ed05caf；先前 CI 43667672400 cancelled（無 job），非失敗或成功證據。完整 CI 43667714699 job 132670734319 completed/success，下載完整原始日誌（初次未完成時暫時 404，完成後讀取成功）。六個 test_p22_file_intake 方法皆 ok；P22B-LEARNING: 3 cases considered; 1 principle transferred; 2 not applicable; feedback candidate；P22B-FILE-RECOVERY: process exit after publication; exact bundle reconciled read-only；Ran 360 tests in 39.988s / OK；所有 workflow steps success（browser、privacy、policy、quality safety gate 均成功）。無實際功能失敗須修正；Node.js 20 actions deprecation warning 留作維護，不放寬守門。
- 額外本機隔離實測：將完整 src/p22_file_intake.py 4471 bytes 轉錄至暫存目錄，git hash-object=b9dcf906ecabd9df9d25d95f58c323dd0a097f07 與遠端 blob 相同。兩份不同 CSV 同時發布到同一 output：1 PUBLISHED、1 EXISTS；唯讀分別 COMMITTED/CONFLICT，輸出不變。獨立 subprocess 於 os.link 前或實際 link 後、finally 清理前 os._exit(23)，分別 NOT_OBSERVED/COMMITTED，兩次殘留 staging 內容均完整且查核不改變；僅清除測試自有暫存檔。輸出符號連結拒絕，來源 bytes 不變。不是整 repo 本機測試，未驗證 power-loss/Windows/非本地 FS。
- **P22-CASE-002｜observed｜來源綁定的不可覆寫檔案發布與唯讀復原**：先整批驗證，再產生 canonical output，將原始輸入 hash、內容與結果 hash 放入同一可驗證 bundle；單一檔案排他發布避免資料/憑據分離。發生未知結果先對原始輸入完整重新計算並比對 bytes；區分 COMMITTED/NOT_OBSERVED/CONFLICT，禁止覆寫與盲目重送；暫存檔殘留不能當作發布失敗，先驗證其來源、使用及狀態才處理。遷移 P21-CASE-005 原子可見性原則，非直接套用 SQLite 交易；P21-CASE-003/006 不適用。適用穩定、可信本地目錄及支援 hard link 的檔案系統；不聲稱敵意路徑防護、來源並行修改、斷電耐久、外部服務或自治多 Agent。來源：上述 exact CI 與獨立本機故障注入。
- 可重用經驗庫：src/workbench_learning.py commit e66720d6e45e68804f1bfde7c84fc5a8f0dcfa10 blob 8d9531f7e1c2595bf44952a0fbe45df1caf96dbe，explicit opt-in TRAINING_CASES 新增 P22-CASE-002，預設 CASES 維持 2；不寫私人工作區，不自動升格 feedback。tests/test_p22_document_review.py blob bdc859c5555223b2edf7133c6833438d529fc44e 更新 explicit corpus 6 筆的預期值（不刪原驗收）；tests/test_p22_file_intake.py blob fe43243f95887ccd365400a042cd16c712066dba 新增 3 組（不同來源、真正發布邊界程序退出、舊 5→6 案例增量匯入/保留舊 ID/跨程序檢索），code/tests head fe48c8b5f7983022b3a581980c404456fc824477 遠端回讀確認。新 CI 尚未核實，不將預期 363 筆當成功結果。curation 是證據導向的運作案例整理，不是獨立模型語意能力評測。
- WRITE_OWNER: 原 Draft PR #8 候選分支；未修改 main、外部研究專案、部署或正式發布。下一步讀最新 exact CI，驗證案例庫匯入及新測試，保留歷史。

### 2026-11-15｜P2-2b 蒸餾整合驗收及 P2-2c 跨架構報表匯出（新候選）

- P2-2b exact code/test head fe48c8b5f7983022b3a581980c404456fc824477 / CI 43667923887/job 132671442278 completed/success（363 tests in 40.489s）；latest docs-integrated head 989244c889c307dac676399e02fba9711794126b / CI 43667964691/job 132671715291 completed/success（363 tests in 38.328s）。完整原始 logs 回讀成功，P22B-DISTILL 舊 5→6、原案例/ID 不變、跨程序檢索，P22B-CUTOVER link 前 NOT_OBSERVED/後 COMMITTED、staging bytes verified，P22B-FILE-RECOVERY；所有 workflow steps success。無實際 CI 失敗需要改動舊核心。預設 2 筆、explicit opt-in 6 筆，P22-CASE-002 已驗證檢索；案例不是權限或模型能力證明。
- P2-2c 自訂公開合成需求（非使用者產品核准）：從本地 SQLite 既有資料庫用 mode=ro/query_only + BEGIN 讀單一快照，檢查唯一 metadata revision、1000 列上限、SYN-四位數 ID、類別/狀態/整數數量；R1 只輸出 completed quantities，R2 再加各狀態筆數；不輸出逐筆 ID 或 pending/rejected 數量。獨立於實作的固定測試 oracle：paper=5,folder=7,pencil=0；complete=2,pending=1,rejected=1。選擇 ZIP 而非 CSV→JSON，將 report.json 與 manifest.json 固定內容/順序/時間戳，manifest 含 canonical logical snapshot SHA256（非原始 DB 檔 hash）、報表 hash、source/policy revision。排他 hard link，禁止覆寫及盲目重送；以相同來源/政策再計算完整 ZIP 比對。來源不可讀/版本不符時拒絕查核，不誤報 NOT_OBSERVED；不同政策需新檔，舊成果保留。快照時點一致，不保證發布時 live DB 未變更；hash 不等於匿名化；只做合成資料，可信穩定路徑，不做實際部署或授權認證。
- src/p22_snapshot_report.py commit 124c46289801bbe1485594316ecfd78f780f66a1 blob 92cf3188a0d00eb67f8cfba82f6db59136a53927；tests/test_p22_snapshot_report.py commit 5366ea6029dc8003ff80af20ed7d055d14c723c1 blob cdbe9ac119e2d8a72b170b0f3ed0a887c131f1a4。六組方法：固定 oracle/隱私欄位/可重現 ZIP；R1→R2 政策和來源 revision 改變；8 類非法來源及缺庫/未知政策；不同政策並行競寫與毀損；CLI 程序退出唯讀復原；實際 learning context/cite/handoff/feedback。擬採用 P22-CASE-002（單一檔案成品/憑據的原則，改成 ZIP）及 B001-CASE-001（SQLite 唯讀缺庫防護），P21-CASE-006 不適用，回饋保持 candidate。測試為同作者需求導出 oracle，非獨立前後測、真實多 Agent、外部系統或完整 requirement revision-aware task invalidation。新程式及測試遠端讀回，43668190276 pending/unverified；尚未宣告功能成功、未將 P2-2c 案例升為 observed。 
- WRITE_OWNER: 原 Draft PR #8 候選分支；main、Release、真人資料、外部研究專案與部署未動。下一步核實 exact integrated CI，再做必要修正與蒸餾。

### 2026-11-15｜P2-2c 報表功能驗收與新案例蒸餾

- Exact integrated head c1f5a605976925dd3ff281894f4e7ceb7be5fb2e / CI 43668235893/job 132672315245 completed/success；完整原始日誌回讀，六個 test_p22_snapshot_report 方法皆 ok，Ran 369 tests in 37.430s/OK，P22C-REVISION（R1 成品不符合 R2；舊來源 revision 拒絕；新來源獨立規格 oracle 檢查）、P22C-TRANSFER（P22-CASE-002 與 B001-CASE-001 applied，P21-CASE-006 not applicable，R2 正確），P22B-DISTILL 仍成功，所有 workflow steps 包含品質/安全/privacy/browser success。沒有實際失敗需要修改報表核心。
- 固定合成規格 oracle：R2 完成數量 paper=5, folder=7, pencil=0；complete=2,pending=1,rejected=1；資料庫原 bytes 不變，ZIP report/manifest 檔案內容和 CRC/邏輯 snapshot hash/報表 hash 匹配，重複輸出 byte-identical；舊 policy/不同來源 revision/競寫/毀損/缺庫與八類非法資料拒絕，程序退出後另一 CLI 唯讀對帳成功。範圍為受控開發者自訂規格與測試，非獨立模型盲測或真實營運。
- **P22-CASE-003｜observed｜雙版本綁定的可重現報表及資料最小揭露**：來源 revision 與報表 policy revision 必須分開；對既有本地 SQLite 以唯讀交易取得一致快照、僅匯出規格所需彙總；以固定 ZIP manifest 將邏輯快照 hash、報表 hash、兩個版本綁定；舊成品保留，新版排他發布，不將缺少/過期來源誤當 NOT_OBSERVED。未知結果需以相符快照及政策重算比對；舊成品不符合新政策不代表舊成品錯誤。將 P22-CASE-002 排他成品/憑據及 B001-CASE-001 缺庫唯讀原則遷移至 SQLite→ZIP。適用合作式本地來源與可信穩定路徑，不保證發布當下 live source CAS、沒有歷史快照的對帳、匿名化、敵意路徑、斷電或 Windows。來源：上述 exact CI。 
- src/workbench_learning.py commit d5cf02264b38bd05a8691c32aafeaee850c77fd7 blob 68543564c6263cf0e8a883f7ccb123fa6c0a6017：P22-CASE-003 加入 explicit opt-in TRAINING_CASES；預設 2 筆不變，擬由 6→7，無私人工作區寫入，不自動升格 feedback。tests/test_p22_document_review.py blob 3985b935ac9884a65a132a18cf1aba8095f6a226 更新完整 opt-in 7 筆預期；tests/test_p22_file_intake.py blob d7dcfe0cf1fbe32819948158295f0fbc79e0168b 固定歷史 5→6 fixture 不混入未來案例；tests/test_p22_snapshot_report.py blob 805eb91cd7a4dbf8b6ae534f1f7c26231d3980e1 增加 6→7 保留舊資料/ID、冪等匯入、跨程序檢索、無關查詢排除；另用 SQLite WAL 讀取中另一連線實際提交 R2 的測試確認 R1 快照一致而非 live CAS，驗證過期舊來源查核拒絕、R2 新報表。新測試尚未實際驗收，預期 371 tests 不計入通過。Code/tests head d4b1a86e7694d3bd84c74eaed65de2b1f71d65bf 遠端回讀；43668423715 in_progress/unverified。下一步核查 exact integrated CI，非自動 promotion。
- WRITE_OWNER: 原 Draft PR #8 候選分支；main、Release、外部研究專案、真人資料及部署未動。

### 2026-11-15｜P2-2c 蒸餾驗收與 P2-2d 版本變更的任務—Artifact—實際成品聯動

- Exact integrated head 193ed127b2a12ee8c31744c2fbf10f4666d6de45 / CI 43668465656/job 132673166596 completed/success；完整 raw logs 371 tests in 40.725s/OK，P22C-DISTILL 6→7 保留舊 ID/內容、冪等 explicit opt-in、跨程序檢索、無關查詢排除，P22C-SNAPSHOT 真實 SQLite WAL 寫者於 R1 讀取中提交 R2 且 R1 一致，P22B-DISTILL 舊歷史 5→6 fixture 仍通過；全部 workflow steps success。P22-CASE-003 可實際檢索，沒有既有 CI 功能失敗，不修改已驗收規則。
- 本次自訂合成情境：使用既有 src/workbench_tasks.py bind_artifacts/revise/revision_status/start/finish/recover 與 team_workbench current_artifacts，不新增第二套任務或 artifact 資料庫。根 requirements 存 source_revision + policy_revision + logical snapshot SHA256；同 source revision 不允許更動內容後假冒同一來源。明確 confirmed change 經既有雙版本原子 revise 使 intake/spec/arch/plan/impl/qa/security/deploy-plan 與 activate 重開，audit 獨立保留；RUNNING 被失效時擋 recover 前的上游工作。根要求 ID 決定 report-root-ID.zip，所有版本保持獨立且排他發布，舊 worker 無法將舊路徑接受為新 generation。QA 以外部於程式實作的固定 synthetic oracle 明確比較字典，錯誤回傳 FAIL 並保留紀錄；security 檢查允許彙總欄位，deploy-plan 再核對各前置 evidence root_id/zip_sha256 且 LIVE gate 保持未核准。所有 PASS 須經 bound finish 檢查 exact session/task revision/prerequisite artifact IDs；不是自動外部部署。
- src/p22_snapshot_report.py blob 4cc8830262148a211bc22ce759e255032e29b4d0 commit 9a643e6809f09fe2c424f7db493ced2979fda589：最小抽取 _publish_bundle，讓已驗證快照的 bytes 排他發布，避免先核對來源再重讀不同快照。src/p22_report_workflow.py blob ae51677d4b8adaf84d88d189a547d7bbc94bbf93 commit cc4734d72e0e274fddda1d13c12c186f2f854f58：新工作台 initialize、confirmed revise、verify、complete_stage，實際 ZIP 及 SHA 綁定。未知已有檔僅在明確 reconcile_existing=True 時唯讀比對，拒絕盲目覆寫；不保證檔案和 DB 原子交易，舊 worker 可留下舊 generation 成品但不能通過新任務驗收。要求來源/工作台穩定可信且合作寫者，外部修改沒有自動偵測，當前快照不等於 live-source CAS；generic API 舊程式/direct SQL 不受此專用流程強制。初始化多交易、部分完成需 review；不接管既有私人工作台或正式資料。
- tests/test_p22_report_workflow.py blob ec3d31f268b3625a137bd1fb76aae2588245d89a code/test head 39800776eb2979ce762f8f71fa379a584dd52596：四個實際功能測試方法（1）先改報表政策再改來源，三個 ZIP generations 依固定 oracle R1/R2/R3 重建，八階段重新驗收，audit 及歷史檔保留、LIVE blocked；（2）實際 publish 後注入 root revise，舊 worker PASS 拒絕、RECOVERY_REQUIRED，回讀舊檔後明確 recover 並重新產生新 root/hash；（3）未知已有檔不能直接盲目重送，明確 read-only reconcile 及實際錯誤 QA oracle FAIL 保留，新 oracle PASS；（4）同 revision 改資料拒絕，修訂新來源後復原，實際 retrieve/cite P22-CASE-003。前一測試提交 ba91a0a26fd8a1d53f73ada8e2b860ab6d192386 CI 43668788619 in_progress at check；最新 43668815796 pending/unverified。程式與測試已回讀，預期 375 tests 尚非 PASS，P22D-* marker 尚待實際 CI，未蒸餾新的 observed case。
- WRITE_OWNER: 只原 Draft PR #8 候選分支，main/Release/外部研究專案/真人資料/部署均未動。訓練是單 Agent 控制流程與實際合成程式測試，不是獨立子 Agent 或真實模型學習成效。

### 2026-11-15｜P2-2d 跨階段驗收及工程蒸餾

- Exact integrated HEAD 8639a359491b9eb923e64efa1db1f8c51b0d628b / CI 43668854174/job 132674236212 completed/success：完整原始日誌（220851 chars）回讀，375 tests in 38.045s/OK，所有 workflow steps success。先前 ba91a0a26fd8a1d53f73ada8e2b860ab6d192386 / CI 43668788619/job 132674032499 同樣 375 tests in 38.643s/OK；39800776eb2979ce762f8f71fa379a584dd52596 / CI 43668815796 cancelled，不計 PASS。沒有實際 CI failure 需修正。
- P22D-REBUILD：政策變更再來源變更，3 個實際 ZIP generations，R1/R2/R3 oracle 通過、舊 ZIP bytes 與三代 QA history 保留，所有 8 相關 stage/artifacts reaccepted、獨立 audit 保留、LIVE gate blocked。P22D-STALE：檔案成功提交後注入根需求修訂，舊 worker PASS 拒絕、明確 recovery 後新版成品與新 root/hash 綁定。P22D-RECOVER：既存檔明確唯讀比對，不盲目重送；錯誤 QA oracle 實際 FAIL、正確 PASS、後續閘門保留。P22D-TRANSFER：同 source revision 內容異動拒絕，P22-CASE-003 實際 retrieve/cite。均為單 Agent 自訂合成情境、真實程式執行而非真人或獨立模型驗收。
- **P22-CASE-004｜observed｜跨交易邊界的世代綁定、任務失效與安全復原**：root artifact 綁來源 revision、logical snapshot hash、policy revision；明確修訂時根需求與相依任務失效在同一工作台交易更新；舊世代檔案保留，輸出以 root ID 區分；任務 session/revision/prerequisite artifact IDs 與實際成品 exact bytes/hash/QA 綁定；檔案先成功但 worker 驗收失效時，保留舊檔與證據、明確對帳與復原後才生成新版，不能宣稱跨檔案／工作台 DB 原子性。適用可信本地受控流程，不等於自動來源偵測、通用 API/direct SQL 防繞過、分散式交易、獨立模型 QA 或斷電耐久。來源：上述 exact CI 43668854174。
- src/workbench_learning.py commit 57781cb67f24ec11e12b2a532f9eead8dccfabfe blob 7574a41d567586ef1f754142b3fc2c693aa07982：新增 explicit opt-in P22-CASE-004；預設 2 筆維持、預期 opt-in 7→8，不動既有私人工作區或自動升格 feedback。tests/test_p22_document_review.py blob 4b22cf46320cf23a902798ec25224b23592ea448 比對完整現行案例鍵；tests/test_p22_file_intake.py blob 86603b62d1b0bc06893d6286e5e7151b647d34a1 與 tests/test_p22_snapshot_report.py blob 12009ff268e4f6e83ca154750aaccddd3c4dca28 凍結歷史 5→6／6→7 驗收集合而非修改原期望。第一次更新後 PR head 暫時滯後，停止寫入並讀回分支 blob 及 PR head 相符後才續作，沒有盲重送。
- tests/test_p22_report_workflow.py blob bff74193d382af63f5f66b9880fd97e2ea6d72c3 head 1220f618e9ffc9bd812e7b31b83d6c1ca1416dac：新增 exact 7→8 case migration/ID/content preserved/idempotent opt-in/跨程序檢索/無關查詢排除，以及 real subprocess os._exit(23) 於 ZIP publish 後 task commit 前；預期唯讀 verify COMMITTED 但 impl RUNNING、QA blocked，明確 resume 新 session、舊 session refuse、只讀 exact reconciliation 後完成 acceptance 且 bytes 不變。這兩個新測試尚未實際 CI 驗收，預期 377 tests 不計通過；43669048037 pending/unverified。全部相關檔案遠端回讀成功。
- WRITE_OWNER: 只原 Draft PR #8 候選分支；main、Release、外部研究專案、真實資料及部署未動。下一步核實蒸餾整合 CI，再優先準備 P1-2 真正獨立執行評測；保留歷史與權限邊界。

### 2026-11-15｜P1-2 本地獨立角色呼叫準備（轉向真實模型，不冒稱已執行）

- P2-2d 蒸餾 exact integrated HEAD 90561afaa9b899fc0dc4796e0939e3427537a49c / CI 43669080334/job 132675094766 completed/success；完整 raw logs (221467 chars)，377 tests in 42.176s/OK，P22D-DISTILL 7→8、舊案例及 ID 保留、冪等跨程序檢索和無關查詢排除；P22D-PROCESS-CUT 真實子程序在 ZIP publish 之後 task commit 之前 os._exit(23)，檔案 COMMITTED、impl RUNNING、QA blocked；明確新 session resume、拒絕舊 session、唯讀對帳且未重寫原檔後完成驗收。P22D-REBUILD/TRANSFER/STALE/RECOVER、歷史 P22B/C 與全部 workflow steps success。前 code/test head 1220f618e9ffc9bd812e7b31b83d6c1ca1416dac / CI 43669048037/job 132674851163 同樣 377 tests in 41.381s/OK；無實際 failure。
- P1-2 執行環境查核：原 PR #6 HEAD 09c9f9d852ec7ab6a468dd241af72b87a40237cb 為 open draft，changed files 包含 llm_runner_preflight、provider evidence、dual source、requirements eval 等；PR #8 既有 src/llm_runner_preflight.py（blob ed613b323260761188ca0e24c3604308877b37bd）只稽核設定雜湊而不 inference，src/capability_execution.py（9956b59303c4fc66b2928ee93c59c351a755317b）只 prepare/ingest AST；docs/TEAM_WORKBENCH.md、docs/WEBSITE_HOLDOUT_EVALUATION.md、AGENTS.md、七角色檔及 agent-ci.yml 所讀適用節不提供實際模型執行授權。當前聊天工具 inventory 未見獨立 subagent/model inference 工具；本機 sandbox command -v ollama/codex/claude/llama-cli/docker/podman/bwrap 無，ollama/llama_cpp/transformers Python module 無，預設本地模型快取 dirs 未見，127.0.0.1:11434/1234 無可連線服務。僅限當前環境，不推定使用者 Windows 或其他私有環境。未讀秘密、未啟動額外服務、未下載模型、真實 inference=0。
- 自訂 P1-2 首個實跑入口：src/p1_local_role_runner.py commit fc9a9bde85245f89c595fc566a50c6309380472b blob dd40d6ccd2ab1d82e18e193df82b7e4a167cab8d。官方 Ollama API chat/tags/FAQ（https://docs.ollama.com/api/chat、https://docs.ollama.com/api/tags、https://docs.ollama.com/faq）核對。只連固定 127.0.0.1:11434，不經代理/redirect/remote endpoint；probe 只 GET version/tags，不推論；run 需明確 operator offline-local confirmation、已安裝非 cloud model tag + exact digest，只接內建 public B001–B005 packet，無 reference/gold、無真人/私人資料。七角色固定 DAG，分開 stateless chat request，QA 在 developer 前、只收到 lead 交接；其他角色接明確上游 handoff，不給工具，不執行輸出原碼。保存新私人目錄 packet/run/每 role request,response,receipt SHA、model tag manifest digest/version、時序及 token metadata；不完整/未知 response 保留現況、禁止自動 retry。此為實際模型呼叫介面，不是單 Agent 手工角色文字模擬，但本輪未呼叫；固定 DAG 不代表 autonomous routing，同一模型的分離請求不等於七個具自主工具的 Agent，local endpoint 與 digest 不構成獨立 provider 及 offline attestation，須使用者關閉 cloud 並隔離外網。角色擷取輸入有長度與 context 限制，真實模型可能截斷/失敗；不得假設所有模型可正確完成。
- tests/test_p1_local_role_runner.py commit c76630433a8d1dba5b92556e6d758e3a20109e95 blob 2c01e9064b796885f311b07bdc209be2ce24e715：三個 offline fake transport 契約方法（無明確同意、cloud tag、錯 digest 拒絕；7 次獨立 request、QA 盲於程式、exact receipt hashes、無 tools；遺失回應保存已觀察資料、無重試）。新檔 readback；43669302039 pending/unverified；預期 380 tests 不是成功證據。CI 不執行模型或候選原碼。
- Windows 手動啟動（待 runner exact CI PASS 後）：從原 PR 候選分支下載對應 SHA ZIP/解壓，於含 src 根目錄開 PowerShell，先 `py -3 --version`、`ollama list`、`py -3 -m src.p1_local_role_runner probe`。probe 回 LOCAL_ENDPOINT_RESPONDED_NO_INFERENCE、version 與已安裝 name/digest；無可用模型或 endpoint 時停止，不自動下載。確認 Ollama 已關 cloud（見官方 FAQ）且可斷開外網後再執行 `py -3 -m src.p1_local_role_runner run --task B001 --model "<probe 實際 name>" --digest "<probe 實際 64 位 digest>" --output "$env:LOCALAPPDATA\\SystemBuilder-P1-Pilot-001" --confirm-offline-local-model`（新私有目錄不能已存在；先核對 ACL、不共享）。成功僅為 LOCAL_ROLE_RESPONSES_CAPTURED_REVIEW_REQUIRED；新 session/role 證據私下審查，不將 raw 內容傳公開 PR/CI。不得執行模型生成程式。之後依既有 capability_execution importer 格式整理模型實際輸出，隔離執行與 independent review 仍另行授權；不能以本地 raw receipts 自證真正模型能力提升。
- WRITE_OWNER: 原 Draft PR #8 候選分支；main、其他 PR（含 PR6）、Release、外部研究系統與正式資料未動。未啟動付費 APIs、外部部署、真實模型或真人盲測。

### 2026-11-15｜P1-2 優先：實際模型技能選擇、案例檢索及獨立評測

- User priority（本輪最新）：解除實際獨立多 Agent 執行及盲測阻礙；驗證七專家能否自主應用現有技能及案例，不啟用未授權付費 API 或外部部署。P2 合成工程訓練已完成足夠基礎，僅為實際失敗與必要缺口補測，不能反覆用同類罐頭測試代替真實模型訓練。
- P1-2a exact integrated HEAD 4afb04bc3f27a932012cca2abf50266ad765b182 / CI 43669358290/job 132675721505 completed/success，完整 raw logs (221931 chars)，380 tests in 38.147s/OK，三個 test_p1_local_role_runner 方法全過、P22D-DISTILL/PROCESS-CUT 與全部品質／安全／瀏覽器 steps success；前一 code/test CI 43669302039 cancelled 不計 PASS。無實際 failure。此為假 transport 契約，並非七個已執行模型。
- 重新查核 current sandbox：command -v ollama/codex/claude/llama-cli/docker/podman/bwrap 均無輸出；Python ollama/llama_cpp/transformers modules absent；loopback 11434 與 1234 connect_ex=111，無可用服務；tool inventory 未見獨立模型/subagent 介面。不能存取使用者 Windows 主機；沒有新增下載、付費 API、Secrets、部署或實際模型呼叫。不得推定其他私有環境亦無模型。
- P1-2b source：src/p1_skill_case_selection.py blob 63490d7e203f6974da0035b50d4a6d08125cea17 commit ba802211f801ce270271665ccebac8fbce726337；src/p1_local_role_runner.py blob e9f71658a774d7e4bb2a03e3ce76d63c34c3bea7 commit 2f035acb0d4c5123a4d053d174ea1bbb35e7e7e9。原 fixed 7 call mode 保留；新增 --case-mode default/curated（兩者同 14-call 預算）。每角色獨立 first response 選擇該角色 catalog 允許 skill ID、自擬搜尋 query 及 reason；host 核對 allowlist，由 catalog 讀實際 SKILL.md，使用新 public-case-workbench 與既有 learn.task_context 檢索最多四個 observed case、排除 candidate/conflict，保存完整 material。第二次 response 用選擇技能、案例與既定上游交接，明示每筆 case 的 applied/not_applicable/理由；只允許已實際取回 ID，透過既有 learn.cite 持久保存 model-declared applicability、hash 及 raw routing/work evidence，不自動 promotion。無 prerequisites 或未完整讀取一律 candidate，不冒稱既有工作台的正式 Artifact 已完成；未執行 model-generated code、無任意工具、無動態路由，固定角色 DAG；單角色可能只有一個 allowed skill，不能據此評估 skill choice quality。所有結果仍須人類或獨立功能 oracle 驗收，沒有真實推論證據。
- tests/test_p1_local_role_runner.py blob e75c3b00b999bfa46c61fc3add0b5cd21312d024 code/test head 9e255a9ca9618dbb0c35f7cc1b5f8c4a3cbb3239；新增兩組方法：default/curated 每組 14 fake transport requests、真實 SQLite case lookup/cite、P22-CASE-004 只在 curated 可見、QA 未見開發內容、缺 prerequisites candidate、raw SHA receipts；越權 skill 或虛構 case ID fail closed。已回讀，新 CI 43688099674 in_progress/unverified，預期 382 tests 不是已通過數量。
- 實跑分階段優先序（不另授權）：① 本地 Windows 已安裝模型 probe 無 inference，核對版本/digest、cloud disabled/斷外網、具適當記憶體及資源上限；待 exact CI 後一次 B001 run，保留失敗，不盲重送。② 在相同公測題、模型/digest、runner/source、OPTIONS 下，分開新目錄 --case-mode default（原 2 cases）和 curated（8 cases），每個 14 requests；記錄模型實際 skill/query、case applicability、candidate outputs 與證據，人工檢查是否選對技能／判對案例，控制上下文和實際 token 時間差；這是公開 dev ablation，不是 blind 前後測或絕對能力分數。③ 真正盲測所需：沿 docs/WEBSITE_HOLDOUT_EVALUATION.md 與 src.website_holdout_compare 的已驗收 seal/匿名/雙評閱/仲裁機制，由未參與訓練的獨立作者私人建立至少五題並封存，評閱者不接觸版本/彼此結果；現有 protocol 專評網站規格，不直接評七角色程式功能；本 runner 目前只接受 B001-B005 公開題，不得以之冒稱獨立 holdout，需要另行接入已封存合成題、獨立功能 oracle/安全沙箱及兩位獨立評審。④ 只有取得真正模型呼叫及獨立驗收後才量測 gain；自主角色分派（不同於角色內選技能）與受限工具執行另外驗證。保留正式 release、安全與隱私獨立觀測。
- Windows minimal pending probe（無下載/付費/推論）：PowerShell 執行 ollama --version、ollama list、py -3 --version；或候選版 CI verified 後從 exact SHA repo 解壓根目錄執行 python -m src.p1_local_role_runner probe；僅回傳 model name/digest/version，保留原有模型、不要貼秘密。若本地沒有符合的模型，停止并核對硬體／授權再決定，不猜測存在。Case-mode run 前須確認網路隔離及模型本地，不將控制旗標視為網路證明。正式測試與盲測尚需真實 execution/independent author/review，不用同一聊天模型虛構。
- WRITE_OWNER: 原 Draft PR #8 候選分支，main/Release/其他 PR/外部系統不動；不寫正式個資、私人 holdout 或付費服務。 

### 2026-11-15｜P1-2c 自主專家分派、QA 退件與任務重新調度

- P1-2b exact integrated HEAD ba136ed439841209385e961b432fddd0534fc9c6 / CI 43688167223/job 132733012963 completed/success，完整 raw logs (222450 chars)，382 tests in 40.071s/OK，P12-SKILL-CASE（每組 14 fake transport requests，真實 SQLite lookup/citations，default/curated 隔離），兩組 skill/case tests 與所有 workflow steps success。無實際 CI 失敗；保留前版可用 runner。不是實際模型推論。
- 新 src/p1_dispatch_runner.py（blob e2ff893b0596196d14a8f2dd8c77bdf777fa2ffc，commit c679f784c8e0b60275f95e06aef0df18c9b84b60）：沿用 local._http/_model/_answer、p1_skill_case_selection、team_workbench/workbench_tasks，非第二套任務資料庫。以內建公開 task packet、新 private workspace 及 8 個候選工作節點（七角色，QA 分 oracle/review）執行。主管每輪收到當前 ready tasks、state/revision、退件 findings 及預算，模型選 task 或 STOP；host 以 allowlist/candidate dependency/revision/hash 拒絕越權或過期交接。每個節點仍有獨立 role skill/query 選擇及真實案例檢索，保留候選內容與原始請求/回應/receipt hashes。QA oracle 只有 intake，先於 implementation，開發可讀 oracle；獨立 QA review 取得 oracle 與 exact implementation revision/hash 後對照，模型只可 REJECT（具體 findings 必填）或 REVIEW_READY（仍非功能驗收）。
- QA REJECT 走 tasks.finish FAIL，保存被退 revision/hash/具體 findings；在明確 pilot 預授權限內 tasks.revise implementation，重開開發及相依 QA/security/recovery/learning，舊 candidate bytes 保留，原 oracle/architecture/intake 不失效，下一輪 developer 收到退件理由。Task pool unbound，candidate-captured PASS/DONE 只表示候選回應已捕捉，非正式 Artifact 驗收；沒有呼叫 bound accepted artifact commit，不冒稱 model-written code valid。限制 12 次 dispatch、2 次修復、最多 3 次 QA review（每輪通常 3 calls，QA review 另 1，最多 39 calls），上下文 byte cap，STOP/預算耗盡皆需覆核；未知 reply 保存現況拒絕重送，沒有自動 resume 或跨檔案/DB 原子性。固定 DAG 只允許 ready-order 動態選擇，非任意工作圖/平行 subagent 或實際外部工具。No paid API, deployment, private existing workspace or untrusted candidate execution.
- tests/test_p1_dispatch_runner.py（blob 58b8a361dc579627bd5b7406bb57823059dbee2f，code/test head 8b6d7ad1522f01f29e8f270980aa60503f28ff15）：三個必要 transport-contract 方法，驗證模型選擇 QA oracle 先於 architecture；一次 QA REJECT→real task pool generation 2→review ready，保留舊 candidate 且原 oracle revision 1；反覆退件停止、model STOP；越權選 task／回應遺失停止且拒絕同路徑重送。All scripted transport, no model performance. 遠端 readback，43688378116 pending/unverified；預期 385 tests 不計實際 PASS。 
- 下一步不重複相似合成應用。最新 exact CI PASS 後，優先已授權 user host 的只讀 probe（ollama --version, ollama list, py -3 --version）及實際離線試跑。新入口（需先核對實際 model name/digest、cloud-disabled 並斷外網，使用從 exact SHA 解壓的 repo 及新的私人資料夾）：`py -3 -m src.p1_dispatch_runner --task B001 --model "<actual local tag>" --digest "<actual 64-char digest>" --output "$env:LOCALAPPDATA\\SystemBuilder-Dispatch-001" --case-mode curated --confirm-offline-local-model`。不要在 CI 或本聊天冒稱已推論。實跑後才能評估模型 routing、skill selection、case applicability、QA rejection 修復有效性。真正未見題仍需獨立封存及功能 oracle、受限 sandbox 和盲態審查；若 runner 不可用，先解除此阻礙，不再持續增加其他應用測試。
- WRITE_OWNER: 僅原 Draft PR #8 候選分支，不修改 main/Release/其他 PR/外部研究系統，不下載模型、不啟動付費 API、不外部部署、不寫正式資料。

### 2026-11-15｜P1-2 受限功能驗收與真實模型執行阻礙

- P1-2c exact integrated HEAD 53f2f44f88d617797cfed8a4ef746c5280e56130 / CI 43688435072/job 132733951433 completed/success，完整 raw logs (223085 chars)，385 tests in 46.839s/OK；三個 dispatch tests、P12-DISPATCH、P12-SKILL-CASE 及所有 workflow steps success。無既有 failure 需要修正；依舊為 transport fixtures、非真實模型能力證據。
- 環境實測：command -v ollama/codex/claude/llama-cli/docker/podman/bwrap 無結果；/usr/bin/unshare 存在；未見 ollama/llama_cpp/transformers/wasmtime Python module，loopback 11434/1234 connect_ex=111；預設模型 cache paths 未觀察到；tool inventory 未見實際 inference/subagent executor。未下載模型、未啟動外部 API/部署、未取得使用者 Windows 主機存取權；不將 unshare 存在視為已驗證 native-code sandbox。目前真實模型呼叫 0。
- 本輪自行選定既有 B003 公開志工排班重疊案例（public_tasks.json blob 0e422d8d36cb1697396dc753fb98304a9b914120），而非新增合成應用。src/p1_restricted_functional.py blob 955b279de16247ae15a538d8d888942e466231ce / commit 8846ef9a4c20878bb8657d22b82226dd3915fb0b；受限純函式 has_overlap(existing, proposed)，明確 pilot policy：既有最多 32 筆、immutable tuple pair、exact bounded integer、start<end；錯誤輸入由 host 拒絕，僅評有效 input 的 candidate boolean；不能宣稱候選支援非法輸入、完整 B003 產品政策或通用系統功能。AST 逐節點 allowlist（只允許單 def、if、for item in existing、布林/整數比較、index 0/1、local assignment、return），不 compile/eval/exec/import/call candidate code，無網路、檔案、任意工具；source 6000 chars、AST 240 nodes、3000 steps upper bounds。固定 12 個 public oracle 由候選外預先定義，測空資料、相接、左右重疊、包含、相等、多筆及負數；exact source SHA/oracle SHA/case results，標記 public slice，非私人 holdout 或獨立人類評審。不宣稱為任意 Python sandbox。
- src/p1_dispatch_runner.py blob ebebbe04930dd3c46e67e873fe6cf0f9f958faf9 / commit cfe4528a9e8e4efe025382b833e62624b52ce983：explicit --functional-b003 只允許 B003，其他模式不變。將受限 function contract 傳入模型任務，不傳 oracle 測試值；Developer 產出 plain candidate source，QA review 時 host interpret exact upstream revision/sha，獨立於 model verdict 產生報告並保存。host failure 即使 model REVIEW_READY 也依既有 tasks.finish FAIL / tasks.revise 重新分派 implementation 及相依任務，提供實際 failure findings；保留舊版與原 oracle。host PASS 也只為固定 public slice、非功能全面通過/正式 Artifact 或部署認可。功能 tool 由 host 在既定 QA 關卡執行，不是模型自主執行任意工具。
- tests/test_p1_dispatch_runner.py blob 1abe0bfef5eced5555b359d85e936b3c9f933727 / head f957b8a85dc7e981184daf05a70ec34b513b5f16：三個必要 tests（真實 bounded interpreter 12-case oracle 區分 correct/incorrect；拒絕 unsafe AST/dead branch/invalid input/excess steps；fake model REVIEW_READY 但第一版實際功能失敗、host QA 退件後第二版受限函式實際通過，檢查兩代 report hashes、原真實能力 claims false）。readback，43688881282 in_progress/unverified；預期 388 tests，尚不得計入 PASS。程式執行的是受限 AST 語意，不是在 public CI import/exec 未知 Python。
- 真實實跑路徑（待 exact CI PASS）：Windows 既有 Ollama/Python read-only probe（先前已提供 ollama --version / ollama list / py -3 --version；不要求反覆執行已可取得的結果）。若本地模型已安裝，利用 exact SHA checkout、`py -3 -m src.p1_local_role_runner probe` 取得完整 name/digest；確認 cloud disabled/本地離線、私人新目錄及資源預算。首輪 `py -3 -m src.p1_dispatch_runner --task B003 --model "<observed tag>" --digest "<observed digest>" --output "$env:LOCALAPPDATA\\SystemBuilder-B003-001" --case-mode curated --functional-b003 --confirm-offline-local-model`，最多 39 chat requests、兩次修復，不自動重跑。驗收 evidence 私人保留 exact candidate/functional reports/repair history，不將本地聲明當獨立 provider 認證。當前無可用模型，不能依測試替身宣稱七專家實跑。後續真正盲測沿既有 protocol 凍結獨立題目與外部 oracle，需 verified sandbox 才能跑任意模型產出的 native Python/完整系統；獨立作者與雙評閱者仍未取得。 
- WRITE_OWNER: 原 Draft PR #8 branch only；main、Release、舊 PR、外部研究專案、真實資料不動；不啟用付費 API 或外部部署。

### 2026-11-15｜TD-001／TD-002 重新定位及最後工程基準

- 本輪 exact engineering head d2ca12006988100a500a6a6fea0f41cd73de5f85，CI 43688939298/job 132735394546 全部步驟成功；完整 logs 223987 chars，388 tests in 39.030s/OK，P12-FUNCTIONAL 12 項公開固定 oracle 實際受限語意運算、P12-HOST-QA 模型替身 REVIEW_READY 仍被真實 host fail 退件並於 revision 2 通過。此為受限工程證據，不是模型實跑或盲測成績。
- 使用者明確確認 TD-001（決策原文及分析見 training/DECISION_LOG.md）；TD-002 跨對話接續與決策保存同步。舊本地模型優先路徑被取代，所有程式、案例、測試及歷史保留不刪；不啟用付費 API、部署、跨專案寫入、不合併／發布。後續優先已授權平台上的實際工作與可遷移知識，按實際證據標示協作模式。此輪只變更文件，不宣稱新架構已通過真實工作驗收。

### 每次續作及更新協定

1. 當使用者提出訓練、續作、改善、分析、方向討論時，定位本 repo；先查 main、當前訓練 PR #8 的實際 head、最新 CI/PR，再讀該 head 的 START_HERE.md、AGENTS.md、本檔頂部及 training/DECISION_LOG.md 的有效決策，按需讀索引 review／技能／程式／測試。新候選轉移時保留本路徑並更新導航；不得用固定 SHA 當現況。
2. 以使用者最新決策、實際程式/測試與同 SHA 證據為準。歷史文件與舊對話只供導航；本節的建議不授權付費模型、外部寫入、合併、部署或正式發布。
3. 依 TD-001 優先在現有已授權 AI 平台完成有實際價值的工作、讀適用技能／案例、驗收及覆盤。缺本地 runner 不構成日常工作阻礙；沒有獨立子代理時標記單 Agent 分工。受控合成測試只在真實缺口或必要回歸時使用，不重複施工。缺特定工具或權限時只阻塞受影響步驟，不能擅自替代部署或跨專案寫入。
4. 每次實質訓練後更新本檔頂部 SOURCE_VERSION、LAST_VERIFIED_STEP、COMPLETED、NEXT_ACTION、BLOCKERS、WRITE_OWNER、SYNC_STATUS 和路線狀態；記錄真實測試命令/CI、失敗修正、產物與限制。每次具有長期價值的討論同步增量保存至原 decision log；重大分析存 reviews 並索引。區分 DISCUSSION、PROPOSED、CONFIRMED、IMPLEMENTED、VERIFIED、SUPERSEDED、REJECTED 及未執行／阻塞。使用者確認、實作及驗收分開。寫前核對版本，回讀同分支檔案、核對同 SHA CI，失敗明確回報，保留 Git 歷史；不複製訓練主檔。
5. 若候選 SHA 改變，分開記錄最後已測程式 SHA 與目前文件 SHA。單 Agent 實作/合成測試、真實 LLM 執行、獨立子代理、獨立盲測、正式 Release 均分開報告。未經授權不自行修改模型權重或宣稱已修改。
6. 本檔為訓練方向的持久化入口，`docs/CURRENT_STATE.md` 與 PR/CI 紀錄保留實際工程歷史；有衝突先查證並更新本節，不另建重複進度來源。


## 目的與邊界
此計畫聚焦本 Agent **能否完成系統開發**，非持續增加供應商來源稽核。要訓練的能力依序為：需求理解、架構取捨、可執行任務計畫、程式實作、QA Debug、跨七角色實際交接、從錯誤修正策略。適用 Repository 只有 `lily4318/reliable-system-builder-agent`；所有公開案例皆是合成，不帶外部正式專案原碼、資料、個資、API Key 或部署權限。

本 PR 與尚未合併的 Draft PR #4（目標分流）、#5（角色交接）及 #6（真實模型 runner/來源）**平行且不互相依賴**。本候選不替三個 PR 做合併決策；任何未來整合須按當時 main 解衝突、同 SHA 跑全套回歸及另行人工審查。

## 選用公開評測工作台（歷史工程操作手冊，不是 TD-001 日常前提）

```bash
# A. 出一題給真正的 Agent，公開輸入不含參考架構與解答
python -m src.capability_prompts --task-id B001 --output output/agent-task-B001.json
# 其餘四題：B002 B003 B004 B005

# B. 驗證題庫、5 份參考提交之格式，不呼叫模型
python -m src.capability_workbench validate

# C. 示範工具本身的自測；100 分只是「自行撰寫參考」通過機械評分
python -m src.capability_workbench evaluate \
  --min-structural-score 100 \
  --output output/self-authored-structural-reference.json

# D. 在有權執行的獨立 Agent 環境，讓 Agent 完成題目並輸出提交 JSON。
#    以下只對已存在的本地檔評分，沒有任何模型／API 呼叫。
python -m src.capability_workbench evaluate \
  --submissions /secure/offline/agent-submissions.json \
  --output /secure/offline/capability-structural-report.json

# E. 舊有政策與事故復原保護仍需通過
python -m unittest discover -s tests -v
python -m src.agent_eval evaluate
python -m src.independent_acceptance evaluate
python -m src.quality_gate check
```

### 2026-11-14 補強｜五題離線任務準備與成果匯入（不呼叫模型）
```bash
# 產出 B001 至 B005 五份「題目及提交格式」，沒有 gold / 參考程式
python -m src.capability_execution prepare \
  --output-dir output/capability-taskpack

# 只有真正取得已授權執行器的成果時，才另行執行下面這個離線匯入：
python -m src.capability_execution ingest \
  --packets-dir output/capability-taskpack \
  --bundle /secure/agent-run-bundle.json \
  --output-dir /secure/capability-review-001
```

**執行器查核現況：** repo `main` 與本 PR #7 只有題目產生器／結構評分器／GitHub Actions，沒有可證明已授權的 LLM 或七個子代理 runner；GitHub 環境／變數端點也無可用資料，無法判定其他私人執行環境是否存在。因此本輪只建立**離線接收介面**，沒有執行 B001–B005 的真實模型解題，也沒有替你配置或呼叫任何付費 API。

`prepare` 使用不可覆寫的新目錄產出 `B001.json`…`B005.json` 和 `manifest.json`，將各題 prompt SHA-256 與公開題庫 SHA-256 鎖住。它無法啟動 Agent，`real_agent_executed=false`。私有 `bundle` 頂層格式為：
```json
{
  "schema_version": 1,
  "kind": "externally_supplied_agent_outputs_unverified",
  "attempt_label": "attempt_2026B001",
  "results": [
    {
      "task_id": "B001",
      "status": "completed",
      "packet_sha256": "取自 manifest.json 的 B001 值",
      "run_id": "agent_run_B001_0001",
      "model_id": "declared_model_version",
      "submission": {"task_id": "B001", "requirements": [], "architecture": {}, "plan": [], "implementation": {}, "qa": [], "handoffs": [], "risk": {}, "claims": {"real_agent_invoked": false, "model_weights_trained": false, "system_deployed": false}},
      "implementation_source": "def enrollment_status(capacity, enrolled, applicant):\n    return 'NOT_IMPLEMENTED'\n"
    }
  ]
}
```
上方 `submission` 只示範 JSON 形狀，未填的部分**不會得分**。完整欄位說明可從任務包 `submission_shape` 取得。若單題無法執行，改用 `{"task_id":"B001","status":"blocked","packet_sha256":"...","reason_code":"NO_AUTHORIZED_RUNNER"}`，不得虛構結果；其餘未提供的題會明示未完成。

匯入會檢查所有題目 prompt SHA、重複 task/run ID、申報模型 ID、假冒參考答案、未核驗的模型／部署主張和程式長度；對任何 `implementation.path` 一律重寫為新私人目錄的 `implementations/Bxxx.py`，並用 AST 做**靜態**分析，不 import／exec 候選碼，不建立正式執行權。若未通過輸入驗證則不建立結果資料夾；若通過才存 `submissions.json`、原始候選程式與 `report.json` 供人工檢視。現階段無論自述模型名稱或 run ID 多完整，`actual_agent_model_execution_verified=false` 且 `program_semantics_verified=false`。請勿將私人原始碼／日誌上傳公開 Repository 或 Actions artifact。

CI 僅驗證離線題目產生與**合成**匯入協定；合成正例即使結構 100 分、程式實際回傳錯誤，也不會被標成真正程式正確率。只有另行核准的 runner、實際執行紀錄、隔離程式測試及獨立人類審查才能建立真實訓練基線。

要生成候選提交，需在有權使用的真實 Agent runner 取得每題的最終結果後，將它整理為 `{"schema_version":1,"submissions":[...完整提交...]}`；格式見 `src.capability_prompts` 的 `submission_shape`。重要：`--submissions` 僅是**讀檔評分**，不會啟動 Agent，也不會證明 JSON 的來源真的是該 Agent。要聲稱真實 Agent 成績需另保存 runner 的執行 ID、模型與提示詞版本、源碼 SHA、工作紀錄、時間與人工審核。

## 題庫與情境

| 題目 | 核心情境 | 預期應學會 |
|---|---|---|
| B001 社區工作坊 | 先前與新規格衝突、額滿候補、重複報名、未知寫入 | 接受最新需求、設計狀態與驗收邊界 |
| B002 公用設備借用 | 可用量、保留庫存、並行競爭與回退 | 系統模組拆分、資料一致性與復原 |
| B003 志工排班 | 時間端點相接、非法區間、模糊政策 | 辨別未決問題與驗收邊界 |
| B004 文化中心藏書 | 只做離線補貨建議、不得自動採購 | 需求取捨、函式設計與權限限制 |
| B005 餐食領取 | 合成取餐碼、已領、查無、角色交接 | 限制重複行為、跨角色工作規格 |

總計 **5 題、20 項編號需求**。這是公開、作者設計的開發集，不是隱藏測試或獨立 blind holdout。固定預期元件名稱與結構是**自動評測用參考標籤**；同樣好的替代架構可能被機械檢查扣分，必須人工複審才可作公平的能力比較。

## 七角色訓練任務與產物

| 角色 | 需要展現的技能 | 可量測提交產物 |
|---|---|---|
| System Lead | 正確理解新需求、衝突、驗收與優先權 | `requirements[].acceptance` |
| Architect | 將需求拆成有界線的元件、資料流、相依 | `architecture.components/links` |
| Developer | 提交可測函式、風險可控的最小代碼 | `implementation.path/function` |
| QA/UAT | 每條需求都有成功和失敗案例 | `qa[].kind/requirement_id/expected` |
| DevOps/SRE | 工作相依、失敗與回退方案，未知寫入先對帳 | `plan[].depends_on`、`risk` |
| Security | 保持最小授權、公開案例無敏感資料 | `risk` 與必要的否決條件 |
| Learning Evaluator | 找出弱點，版本前後比較及人類審查 | 統一評分器與失敗案例報告 |

`handoffs[{role,input,output}]` 記錄七個角色的交接**預期產物**。它只能驗證文件是否齊全，不能證明七個獨立 AI 實際接力工作。

## 評分維度與方法

| 自動結構維度 | 配分 | 實際驗證 |
|---|---:|---|
| 需求追溯 | 20 | 所有 R 編號與非空、具體驗收文字 |
| 架構 | 15 | 預期元件責任、元件連結及資料流結構存在 |
| 工作計畫 | 20 | 角色 owner、需求覆蓋、有效依賴與 DAG 無循環 |
| 程式靜態檢查 | 10 | 受控路徑中的 Python AST 有對應函式和 return |
| QA | 20 | 每個需求至少一個正例及一個負例 |
| 七角色交接 | 10 | 七位專家各自有可追蹤輸入與輸出 |
| 基本安全 | 5 | 未知非冪等寫入不重送、人工正式核准、風險匹配 |
| **總計** | **100** | **只代表結構符合公開評分準則** |

**刻意不量測的能力**：L​​LM 語意推理、架構實際合理性、真正程式語意正確性、非預期需求泛化、執行多個子代理、部署、真人 UI、模型權重更新。這些不可能只靠簡短 JSON 及 AST 得知。評分結果將永遠顯示 `real_llm_or_seven_agents_invoked=false`、`actual_program_correctness_evaluated=false`、`independent_holdout_evaluated=false`、`formal_release_authorized=false`。真實執行證據必須由另行核准的執行平台獨立提供，而不是由提交 JSON 自我宣告。

`src/capability_reference.py` 是公開、可信、自行撰寫的極小參考函式；CI 使用這些函式的可信單元測試驗收參考語意。對 Agent 提交的任意 Python 程式，評測器**只用 `ast.parse` 讀取靜態形式，不 import、不執行**，避免在有網路或 Secret 的 CI 中跑不可信代碼。

## 選用獨立能力訓練與改善前後比較流程（非日常工作前提）

1. **凍結基線**：保存 Agent 所用模型的實際版本、Prompt／Role SHA、工作台 SHA、公開題庫 SHA、指令與資源限制、工具權限、執行時間和成本。先用固定題目取得真正模型至少 3 次獨立輸出，保留失敗案例。
2. **獨立人工觀察**：兩位審查者盲態評閱需求是否正確（尤其衝突與含糊處）、架構取捨、錯誤後修正；建立理由與仲裁，不只看元件名稱是否匹配。開發者不可一邊改評測題目一邊宣稱成績上升。
3. **隔離程式執行**：在另外授權、無外網、無 Secret、唯讀掛載、限制 CPU/記憶體/時間且可銷毀的沙箱，將 Agent 寫的程式跑「未向模型提供的功能測試」，記錄成功率、錯誤型態和修復輪次；**不可只在 GitHub Actions 直接執行不可信程式**。
4. **專家協作追蹤**：若平台真正支援子代理，保存每位角色的輸入與輸出、交接損失、是否被 QA 找出問題及最終整合結果；不支援時分開記為單 Agent 模擬分工，不能把角色文字當工具執行。
5. **修正策略**：針對最低能力維度改善角色 Prompt、交接契約、程式工作步驟與測試邏輯；維持安全與授權底線，不擴充無關的供應商身分稽核。
6. **真正未見題測試**：由未參與 Prompt 開發的人另建隔離題庫、封存原始 SHA、標註與測試版本；前後候選在同一成本及工具條件下比較，分別報告結構分數、人工架構分數、可運作功能測試比例、Bug 修復輪次、七角色交接成功率和安全違規。只有到這步才可討論 Agent 是否真的進步，仍非模型權重微調。
7. **人工 Release 決策**：只有在審查者和 Owner 對 PR、CI、真實資料處理及部署門檻分別授權後才進正式 Release。本候選不做任何外部部署或自動合併。

## 成功門檻的建議（未核准、不是已測結果）
- 每項新公開任務應有完整驗收與雙向 QA 追溯；公開自我參考的結構回歸保持 100 分，只檢查工作台未退步。
- 待可執行真模型後，第一輪目標是產生完整輸出和可回讀來源，下一輪看實際功能測試和人工架構評分；不事先假定準確率或宣稱改善百分比。
- 不可信程式通過靜態 AST **不能**當程式已成功；沒有已核准隔離環境，就只保留為 `CODE_EXECUTION_UNVERIFIED`。
- 人類審查安全違規一律阻擋，且任何 UNKNOWN 非冪等請求皆以唯讀對帳優先。

## 歷史基準設計時的狀態（非現況；以頂部為準）
**已設計並可在此 Repo CI 執行**：公開合成需求、參考產物、任務生成 CLI、結構評分器、受信任參考程式與單元測試、既有政策及復原基準。**仍沒有**：實際模型生成的系統成果、真正子代理執行、未知程式的隔離沙箱、獨立 holdout、真實部署驗收。以上項目不得借用之前 PR #6 的 runner／模型來源檢查狀態，或以任意合成 PASS 冒充完成訓練。
