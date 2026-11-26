# TD-003｜完全新手的環境準備與人機協作交付
狀態：使用者明確要求此能力，候選實作與待驗收路徑。適用新建、維護、排錯等涉及第三方工具的工作。既有 TD-001/002、TP-006、正式需求、資源與外部操作授權完整保留。不是要求每位使用者都學會程式，也不是每位新手均須註冊四個平台。CLI 是 Agent 可用的離線輔助、非使用者必要步驟。

## 1. 核心能力與蒸餾
**Beginner-First Guided Delivery｜零技術門檻的人機協作交付**。將帳號、登入、安全、外掛連接、目標/權限、方案及必要人工設定視為實際工作之前置責任。預設完全新手、使用日常繁體中文；解釋此刻需要的名詞、目的和影響。由 Agent 承擔可安全且獲授權的工作，人類保留密碼、身分驗證、條款、授權、付款與正式啟用的控制。不得要求使用者把需要由 Agent 解決的工具選擇和設定問題自行研究。不得承諾所有平台一定支援自動操作。符合既有規則一（逐步指引）及規則三（可編輯確認），是具體化而非另建相衝突的技能。

## 2. 分階段、有條件的支援
1. 先用原需求訪談、已知狀態和選型，不先註冊所有帳號。公共 Agent repo 可唯讀取用不等於新手必須 GitHub 註冊才能討論需求。只在已釐清適合方案及必要服務後，建立所需服務清單；候選方案可改選，不因缺工具強迫購買。
2. 查當前介面/已安裝可用工具/授權連接、帳號是否已有、身分和目標是否相符，不問已知資訊。能用真唯讀 metadata 證實就先做；不足時只問一個必要問題，例如「你有可以使用的 GitHub 帳號嗎？」可回答不知道。
3. 確實沒有帳號時，從官方入口教登入/註冊、驗證、自行保管密碼與雙重驗證；已有帳號跳過註冊。若註冊伴隨新組織、預設資源或計費確認，分清影響並由使用者操作，需另確認資源變更的不得先做。未同意必要政策、條款或額外權限可拒絕；不規避管理者限制。
4. 按當前平台介面教連接。ChatGPT 原生 Settings > Plugins（部分介面 Apps）→ 選已核實的外掛 → Install plugin（若顯示）→ Connect（若提示）→ 選正確供應商帳號 → 看清授權範圍，由本人確認 → 返回 ChatGPT。ChatGPT 工作空間與供應商帳號/組織是不同層次；安裝、連接、授權、工具支援和正式操作各有不同證據。不要把連接等同建立/部署。不要求每個人購買 ChatGPT 方案，實際可用度受方案、地區、裝置與管理者政策限制。
5. Agent 驗證最小非敏感 metadata：實際工具呼叫、正確帳戶/組織/目標、要求的讀寫能力與限制、實際免費方案、剩餘配額及報價。確認看得到不代表可以寫；寫入權限仍需 C3 獨立授權或適用 task_scope，禁止用測試寫入證明未授權寫權。來源聲稱/使用者回報、工具 schema、實際讀回、實際寫入驗收分開。
6. 按需引導 C2/C3 及安全設定，實行已授權的 Agent 操作。未知/部分寫入先唯讀對帳。C4/C5 真 HTTPS/遠端功能與回復，C6 真人驗收；保留合成資料、預算及正式啟用 gate。
7. 卡住時先停止相關步驟而非重走全流程；其他不依賴該阻礙的已授權工作仍可進行。重新進入對話查原正式來源和可用的最新安全紀錄，重新驗證會變動的權限/目標，不要求每次重註冊。

## 3. 每次人工指引的顯示契約
只呈現**當前最小可完成步驟**；必要時將整段流程作為可選參考，不能一次貼大量命令迫使新手自行找進度。每步給：
- 為什麼要做、在電腦/手機/哪個網站操作、哪個帳號／目標、官方入口；先確認使用者看到的頁面，不要求重複已做事項。
- 點選位置及中英常見名稱、欄位中應輸入何種類型、不要填什麼；不在畫面不確定時編造按鈕、截圖或固定標籤。
- 預期畫面與成功證據，僅需回覆完成、非敏感狀態、錯誤碼或遮蔽截圖。任何密碼、驗證碼、復原碼、OAuth token/client secret、API key、service-role key、完整私人 billing/資料內容不得要求貼入對話、repo 或 log。
- 看不到選項、錯誤或權限不同時停止哪個動作、如何安全查核，必要時提供「已完成／找不到／出現錯誤／暫不授權」；不自動送出/核准高風險操作。
- 明確區分「你現在做」「我接著做」，觀察實際結果後才進下步。若需要使用者授權更動、註冊付費或公開資源，提供可編輯完整範圍與另行確認。若使用者無能力或不願進行，提供可行替代（例如手動一次性必要設定、已連接適合服務、候選離線工程）；不是借道繞過權限。
- 不要求使用者自行執行 Python、終端機或安裝本機模型才能使用 Agent；只有平台確實缺必要能力且已自行同意的最窄替代路徑，才逐步講解相關工具。

## 4. 四平台完全新手的具體路徑
各平台 account/security 與 connect recipe 可由 src.account_onboarding.route 取得；ChatGPT 外掛目錄和供應商的登入介面以使用當下官方資料為準。以下不是已實測所有註冊畫面，也不是現在要求真人操作。

| 平台 | 官方入口與準備 | 連接後的驗證、停點 |
|---|---|---|
| GitHub | https://github.com/signup → 登入/驗證 → Settings → Password and authentication → 自行保管雙重驗證/復原碼；Free/權限核對。既有 github_signup 原手冊保留。 | ChatGPT 搜 GitHub，若提供 Only select repositories 只選所需。無 repo 時先由本人確認獨立 repo 名稱/visibility/管理權限，不能選全部私有 repo 以便測試。真 repo metadata、canonical id、可見性、tool scope。原 C1 已證 Pages 設定/dispatch 介面缺口；需要人工設定只在網站 artifact、安全、CI 與獨立部署授權之後逐步帶領。 |
| Google/GAS/Sheets | https://accounts.google.com/signup → 需要時選個人帳戶，登入後 https://myaccount.google.com/ 核對；已有個人帳戶不要求付費 Workspace。 | ChatGPT Google Drive（只選必要服務）；如果所選服務要求全部必要權限，使用者審閱是否接受，不假稱只核准部分仍可工作。真 Drive profile/readback 並明確區分 Sheets 與 Apps Script 管理。無專用 GAS deploy 工具時先查替代；Apps Script dashboard 的 API access 影響所有已授權應用，Google Cloud API/OAuth 設定另確認，由使用者親自操作，禁止無必要開啟。 |
| Cloudflare | https://dash.cloudflare.com/sign-up → Email/Password → Create Account → 驗證郵件 → 正確帳號/安全/方案核對；只需合適免費服務，不要求買域。 | ChatGPT Cloudflare；讀 whoami、accounts、Workers/D1 metadata。原 C1 已觀測 GET subdomain 404 code10007 與 billing 403；開 Workers & Pages 首次可能初始化 workers.dev，不在唯讀引導階段點進去，先說明/確認。Billing/Subscriptions 可由本人唯讀查免費方案；不索取廣泛 token 來讀帳單；寫入及初始化另授權。 |
| Supabase | https://supabase.com/dashboard → 依當次畫面 Sign up/可信登入 → 驗證 → 查看組織；管理平台帳號非網站會員。若需要新組織/專案，確認 scope/free quote 之後才做。 | ChatGPT Supabase，選正確組織。實際 list_organizations/list_projects/get_organization 讀 plan。原 C1 實測 Free/空清單；不推論所有其他使用者都有此結果。free quota/quote、寫入、project/migrations/Auth/RLS/backup 另驗，前端另選。 |

Google Account 中文官方建立帳戶頁當次抓取失敗（驗證/反爬頁）；Supabase Dashboard 直接網頁抓取亦無可讀 UI，平台官方概覽確認入口，故以上 signup 欄位與提示不能宣稱逐畫面實驗。遇變動須依真人頁面或官方指引，不假造圖。ChatGPT 設定路徑及帳號/連結差異已核官方 Help Center。來源日期 2026-11-15。

### 常見故障的接續
| 使用者遇到 | Agent 下一步 |
|---|---|
| 我已有帳號／連接 | 直接核 current identity/正確目標，不重註冊或重連。 |
| 不知道有沒有帳號 | 優先查當前可用連接，再問一個最小問題；必要回官方登入頁採安全復原，不問密碼。 |
| 找不到 Plugins/Apps 或服務 | 核目錄、方案/地區/工作空間與裝置。具體指出缺失；使用支援介面，或可編輯選型/最少人工替代，不自動要求付費。 |
| 連到其他帳號或看不到目標 | 停止存取，核 ChatGPT account/workspace 與 provider account；如支援 Connect another account 再選對象，必要時檢查 repository/org access，重新讀回。未授權不得讀錯帳號的資料內容。 |
| OAuth 拒絕或管理者停用 | 分辨拒絕、管理者政策、服務必需 scopes；尊重使用者拒絕，不誘導全開，不反覆嘗試。 |
| 顯示已連接但工具查詢失敗 | 定位錯誤碼、服務暫時故障、scope、資源存在性或 API allowlist；修必要步驟後才重驗，不以 installed/connected 圖示冒稱已實測。 |
| 出現付費/信用卡/試用 | 先停止；報當前畫面上的資費（非憑證）、是否需要此資源，提供免費替代或獨立預算確認。 |
| 想停止或移除連接 | Settings → Plugins/Apps → 選 app/帳號 → Disconnect（若提供）；若需供應商撤銷權限，在官方設定頁操作，先說明可能影響其他整合。與已存對話/資料刪除、真正關閉服務或帳單是不同操作，不宣稱一鍵清除或停止計費。 |

## 5. 可執行的 Agent 離線路由
`python -m src.account_onboarding < profile.json`：只讀 stdin，stdout JSON；bounded 16KiB、duplicate key 拒絕、exact enum，不讀連接、無網路、無寫入、無憑證。human_walkthrough 原 GitHub 三個 recipes 行為保持，signup 重用原 recipe。四平台路由是現行 cloud 選型的接續工具，非替代 provider connector、原工程 gate 或對使用者的 UI。Agent 可按原碼使用，不需要使用者安裝。
例如 `{"required":["github","supabase"],"states":{"github":{"account":"ready","connection":"connected","readback":"verified","capability":"supported","cost":"free_confirmed"},"supabase":{"account":"missing","connection":"missing","readback":"unknown","capability":"unknown","cost":"unknown"}}}` 返回 GUIDE_SIGNUP supabase，不重做 GitHub。required 只含已選方案必要服務，依實際先後排列；沒選則空 list/states。五欄是 caller 聲明/最新證據分類，非程式驗證：account unknown/missing/security_pending/ready；connection unknown/missing/connected/wrong_account/denied/unavailable；readback unknown/verified/failed/wrong_target；capability unknown/supported/unsupported；cost unknown/free_confirmed/not_free_or_uncertain。改帳號、目標、權限、工具、方案或跨對話證據失效，重置適用欄 readback/capability/cost unknown，實際重新查核；不得僅由使用者「完成」填 verified。先處理任何 wrong_account/wrong_target，拒絕 permission_denied、不連線/不可用、費用不明各有 HOLD。全字段 ready 僅 READY_FOR_C1_EVIDENCE_REVIEW, 所有 verification/deploy/write/payment/c1_pass 旗標固定 false。狀態分類與小步流程是依使用者意圖的候選工程設計，不是獨立測得的 UX 改善。recipe 提供全步驟供 Agent 選出當前一項，程式不自行保存逐步進度、不操控真人畫面；Agent 在授權私人工作空間留非敏感 checkpoint、實際完成證據及未決，或於當前對話確認，不能公開記錄私人帳號。沒有私人工作空間就不另建；跨對話重新核對，不要求重註冊。

## 6. 驗收
- B01 未選型時不要求帳號；B02 已有/未知帳號、已連接、不重複註冊；B03 四套 signup 和 connect 都有 action/check/blocked；B04 wrong account/target 優先停、矛盾狀態與 permission denied；B05 工具缺失、連線失敗、GAS capability gap；B06 quota/成本 unknown/非免費；B07 多服務逐項接續、不要求不需要的 account；B08 malformed/duplicate/oversize/forged authorization fail；B09 所有 ready 仍不授權。執行 `python -m unittest discover -s tests -p 'test_account_onboarding.py' -v`。以上為合成確定性路由/結構回歸，不是真人 onboarding 或模型增益。
- B10 真新手驗收（待）：選一個實際需要的架構，用現有或由本人自願建立之帳號，Agent 不假定任何先備知識，逐步陪同且驗每步；測「已有帳號」「從未有帳號」「連接後錯帳號/不可用/費用不明」的真實適用分支；不為達測試數而建立多餘帳號、製造付費/錯帳號或要求真人回報秘密。記錄必要人工步數、卡住點、是否能自助回復、最後實際 metadata evidence；驗收要有人類評閱是否能理解，不用單元測試冒充。原 C1 真 Supabase 連接後讀回及 GitHub/Cloudflare/Drive 調查是動機/局部真證據，不是 B10 或 A07 獨立新對話。原 CLOUD-A C2/C3 待確認；可以在實際訓練步驟使用新協定，外部資源另行授權。

## 官方來源
- OpenAI [連接及管理帳號](https://help.openai.com/en/articles/20001494-connecting-and-managing-app-accounts-in-chatgpt)、[權限](https://help.openai.com/en/articles/20001495-managing-app-permissions-in-chatgpt)、[故障排除](https://help.openai.com/en/articles/20001497-troubleshooting-plugins-and-apps-in-chatgpt)
- GitHub [帳號入門](https://docs.github.com/en/get-started/onboarding/getting-started-with-your-github-account)、[第三方 App 安裝](https://docs.github.com/en/apps/using-github-apps/installing-a-github-app-from-a-third-party)
- Google [建立帳號](https://support.google.com/accounts/answer/27441)、[Apps Script API 權限](https://developers.google.com/apps-script/api/how-tos/enable)
- Cloudflare [帳號建立](https://developers.cloudflare.com/fundamentals/account/create-account/)、[Workers Dashboard](https://developers.cloudflare.com/workers/get-started/dashboard/)
- Supabase [平台](https://supabase.com/docs/guides/platform)、[計費](https://supabase.com/docs/guides/platform/billing-on-supabase)


## 7. 原始 CI 驗收
- 離線實際驗收：exact f3dc2575d7a17e1b1b39ebd1f3127ce58ef83c65 / [CI 43715589058](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43715589058) job 132816301983 completed/success；raw log 241919 chars；16 個 onboarding test methods 全 ok，完整 466 tests in 49.191s，既有 EDITORIAL_BROWSER_PASS。四平台 signup/connect、既有帳號跳過、wrong target 全局優先、拒絕/失敗/不可用、GAS capability gap、費用停點、多服務、malformed/duplicate/size/forged approval、全部 ready 仍不授權等均實際跑過。舊 450 tests 保留；沒有建立真新帳號。文件整合 exact eebba69537bb8ed00308b9054c8a6dd8578f67c1 11份檔案已回讀相符，文件版本 CI 43715814303 另查。B10 真新手獨立操作仍 pending，不能由受控測試推論理解度或真 UI 成績。

## 8. 真實跨對話接續及既有連接支線證據（B10 partial, 2026-11-15）
- 原文件 CI exact 0dbb7fc000a589fa0a94eb89f5a99ed6c5a3a2ee / [43715920202](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43715920202)，466 tests/OK、16 onboarding methods、EDITORIAL_BROWSER_PASS；前一整合文件 CI 43715814303 success。
- 實際原訓練接續：default main 主檔及決策 GET 404，Agent 查原 PR #8 最新 head 後重新核對正確目標、原主檔與 CI 日誌；get_repo metadata 成功，已有 GitHub 連接無須真人重註冊／重連，人工帳號步數 0。此為 Agent 自己修復真實來源查找問題及取得 readback 的證據。未開外部資源或部署；不宣稱真人新手理解度、帳號安全/成本或 Pages 授權已核、B10 或 A07 獨立驗收已完成。
- 交付給完全新手的當前說明：這一步只是確認既有 GitHub 運作；不需你按任何設定。若要自行核對，可開上方 CI 網址，查看 verify 結果是否 Success；若看不到，僅回報頁面非敏感錯誤，不更動權限。下一次確有必要真人操作時才按第3節交付並取得人類評閱。若選 CLOUD-A，先另確認 C2/C3，不先點 Pages Save。
