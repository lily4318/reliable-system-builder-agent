# 紙上｜WEB-EDITORIAL-01 本機操作與復原指南

**僅合成、僅 localhost、候選實作**。依 [使用者已確認規格](training/reviews/2026-11-15-editorial-website-spec.md) 和 [ADR/工作包](training/reviews/2026-11-15-editorial-architecture.md)。正式部署、真人資料及外部發布均不在授權內。不要求安裝 AI 模型、API Key 或付費服務。

## 1. Windows 本機啟動

1. 打開 [Draft PR #8](https://github.com/lily4318/reliable-system-builder-agent/pull/8)，切換候選分支 candidate-skill-team-integration-20261114，從 Code → Download ZIP 下載候選原始碼，解壓至新資料夾。確認含 src/editorial_site.py、src/editorial_store.py 及 examples/editorial-site/。若要精確驗收，使用主檔所列已驗收 commit 的 ZIP（GitHub commit 頁 Browse files → Code → Download ZIP），不得用過期分支替代。
2. 在檔案總管該根目錄的網址列輸入 powershell、Enter。執行 py -3 --version；CI 使用 Python 3.12。若未安裝，按 [本機工具操作指南](WEBSITE_HOLDOUT_WALKTHROUGH.md) 取得 Python，不需 Ollama。只在已授權私人本機位置保存測試庫；不要使用實際研究/業務資料夾或共享 repo。
3. 新建資料夾及初始 DB。以下路徑須是全新、自己可控、無既有 DB 的位置。第一次 init 會提示三個合成帳號 author-a、author-b、editor 的各自密碼（至少12字元）；輸入本機自行設定的合成密碼，不貼到聊天室或提交 Git。已存在 DB 會拒絕，不重做 init。

    $folder = Join-Path $env:LOCALAPPDATA "EditorialSynthetic01"
    New-Item -ItemType Directory -Path $folder
    $db = Join-Path $folder "editorial.sqlite"
    py -3 -m src.editorial_site init --db "$db"
    py -3 -m src.editorial_site verify --db "$db"

   預期看到 EDITORIAL_INITIALIZED 與 EDITORIAL_INTEGRITY_OK；若 BLOCKED，先查檔案路徑、權限及 schema，不刪除、覆蓋既有檔案。
4. 啟動：py -3 -m src.editorial_site serve --db "$db"
   預期 Local synthetic site: http://127.0.0.1:8777/ 。於 Chrome 打開精確網址。若埠被占用，加 --port 8778 並使用新顯示網址。不能使用 0.0.0.0、外部網址、反向代理或隧道。不要直接雙擊 HTML。
5. 先以匿名讀者看公開刊物；登入 author-a，新增純文字文章，儲存草稿後點提交審核；登出改用 editor，查看送審稿、輸入退回理由或核准，核准後另點發布。改用匿名頁查公開文。author-a 可建立新修訂、改稿、送審；新稿核准不覆蓋舊公開版，只有發布才正式切換。editor 可下架；作者可再建立修訂並重新審核。author-b 無權查看或修改 author-a 私稿。操作及理由可從授權工作台歷史回讀。
6. 結束：關閉頁面，在 PowerShell 按 Ctrl+C 停止。下次沿用同一 DB 直接 serve，不重新 init。本機 session 30 分鐘到期，登出即刪除 session，登入憑證由合成使用者自持。

## 2. 資料與權限設計

- 公開 API GET /api/articles（q, category, page，20/page）、/api/article?id=... 僅回已發布 pointer 綁定之 PUBLISHED revision。原文不可從草稿或審稿 API 洩露。
- GET /api/bootstrap、/api/workspace、/api/receipt?token=...；POST /api/login、/api/logout、/api/action。所有 POST 限精確 Host/Origin、JSON、CSRF，認證由伺服器 session 取得 actor，拒絕偽造欄位。純文字 DOM，不把任意 HTML 插入頁面。
- 資料庫 schema 2（候選開發時加 per-revision counter、audit review reason；早期未正式交付的 schema 1 不可直接開啟，無任意遷移）。同一篇文章最多一份未完修訂、最多一份 PUBLISHED；公開指標與版本同交易。操作收據綁 actor/token/payload digest，合法同請求回原決定，異 payload 拒絕。拒絕狀態有收據但不增加有效業務事件。故障未提交則不留半套業務紀錄。
- 系統只用當地合成環境，非正式認證架構：localhost HTTP 不設 Secure cookie；如公共服務必須重新評估框架、HTTPS、Secure、rate limit、服務器、資料策略、資安測試、部署和真人 UAT，不能將此 demo 直接上線。瀏覽器同主機 cookie 不隔離 port，不信任共用或敵意 localhost。不要同時用多個啟動埠操作真資料。

## 3. 結果不明與復原

網站收到網路錯誤或服務端不明回應，會保留 action token 與原合成帳號於本頁 sessionStorage（僅操作識別，非登入密碼/session token），暫停新的業務寫入；用原帳號登入及點「唯讀查詢收據」。已觀測：依收據顯示原結果，不重送；未觀測不表示舊工作必然停止。先停止舊本機 server、另行唯讀核對原 DB/狀態及原 token，再決定人工處置。禁止自動重送或直接用新 token 掩蓋未知操作；關閉分頁會清掉該頁 sessionStorage，因此請先保留顯示的操作識別碼。未觀測時目前沒有自動解除封鎖，需確認舊 writer 停止及狀態後人工重新開始。這是本機 SQLite 受控語意，非端到端分散式 exactly-once。

## 4. 備份、還原與回退

1. 為維護/回退先 Ctrl+C 停止 server；保留原 DB 與原 commit。選新檔名：

    $backup = Join-Path $folder "backup-01.sqlite"
    py -3 -m src.editorial_site backup --db "$db" --target "$backup"
    py -3 -m src.editorial_site verify --db "$backup"

2. 新路徑還原，絕不覆蓋來源：

    $restore = Join-Path $folder "restored-01.sqlite"
    py -3 -m src.editorial_site restore --db "$backup" --target "$restore"
    py -3 -m src.editorial_site verify --db "$restore"
    py -3 -m src.editorial_site serve --db "$restore"

   預期 EDITORIAL_COPY_VERIFIED / EDITORIAL_INTEGRITY_OK；重新登入（還原清除舊 sessions）並核對公開內容、文章狀態、歷史及帳號隔離。若任一步失敗，保留來源及未通過的目標作查核，不將部分成品當成功，不盲重送。備份含合成帳號 hash 及資料，不上傳 repo。不要以舊備份覆蓋已有新版寫入，回退前另保存當前 DB、核對 schema/相容性及資料差異；原本機目標不支援任意 schema migration。
3. 真外部部署/回退另需確認環境、權限、HTTPS、重建或受控 migration、資料備份、CI exact SHA、真 UI UAT 與正式人審授權。本輪只交本機運行及回退方法，無外部 URL、無部署。

## 5. 可重現測試

    py -3 -m unittest discover -s tests -p "test_editorial_*.py" -v
    py -3 -m src.editorial_browser_test
    py -3 -m unittest discover -s tests -v

瀏覽器 runner 用已安裝 Chromium/Chrome（可指定 --browser "<Chrome.exe 路徑>"），在暫存合成 DB/獨立 profile、無外部網路、loopback CDP，僅測試模式載入測試腳本；日常使用沒有測試回報入口、不要使用 --no-sandbox。CI 同 SHA 證據見原訓練主檔。分開本機 CI、真瀏覽器自動化、真人 UAT、外部部署等驗收；沒有真人或外部證據不可冒稱完成。
