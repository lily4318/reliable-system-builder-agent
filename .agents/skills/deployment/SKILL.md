---
name: deployment
description: "部署、處理 CI 或版本。devops-sre 角色；交付 deployment-plan。"
---
# deployment｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：implementation、qa、security-review。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
先核對實際部署環境、權限與同 SHA 測試；準備備份、回退、版本、操作順序。人工設定附逐步 UI 欄位與檢查。未另獲授權只交部署計畫；不啟用真人收件、不盲重送。

### 四平台線上部署與驗收（TP-006 / NATIVE-CLOUD-016-STACK-SELECTION）
依 [多平台選型及實戰指南](../../../docs/CLOUD_ARCHITECTURE_SELECTION.md) C0–C6，先確認原資源身份、tool permissions、plan/remaining cost、source SHA/CI、backup/rollback；C3 單獨可編輯明示授權，禁止將 selection/advisory/需求確認視為外部部署授權。按 Pages artifact/URL、GAS scriptId/version/deploymentId/exec、Worker version/D1 schema、Supabase project/migration/front URL 取得實際讀回、遠端正負測、持久化與復原。未知/部分寫入先 READ_ONLY_RECONCILE；不盲送，不自動升級或正式啟用。無實際工具/授權時明確缺件與最少人工操作。

### TD-003｜完全新手的環境準備
讀 [新手引導](../../../docs/BEGINNER_ACCOUNT_ONBOARDING.md)。需求與必要平台先確認，按既有帳號/連接/真唯讀/權限/費用使用 src.account_onboarding 或同契約分流；只教目前必要的人工操作，附官方入口、預期與停點，使用者自行登入驗證與審閱同意。成功由真實可用工具回讀，失敗排除或安全替代；不讓新手自行研究、不重複註冊、不要求 CLI、不以連接授權部署。

### Version-bound CI evidence 完整性（TD004-OFFICIAL-03 / EP-14）
先核 real run/attempt、checkout SHA 與 PR head/merge diff、必要步驟結果，再核產物 ID/expiry/digest、明示 expected file set；失敗可留下 diagnostic 但不是候選部署物。統計由逐案例重算、拒絕錯型/負數/重複，保留實際完整日誌。從獨立可信來源取得完整報告 hash/context 再查每檔 byte hash，不能信同 artifact 自帶摘要、不能把 checksum 當簽章或 CI 結果。原 src.ci_evidence_bundle 離線 verifier 僅驗 supplied evidence 且不授權部署；新 CI_EVIDENCE_BOUND marker 原始 log 另核。source drift 或未知提交先唯讀對帳；回退以已核實版與新 revert/forward-fix，不 force push、不重送未知 POST。真 deployment artifact、簽章/attestation、remote bytes、UAT/Release 另門檻。見 [深度覆盤](../../../docs/training/reviews/2026-11-15-ci-artifact-integrity.md)。


### 本機版本啟用失敗與復原（必要專家深化，2026-11-16）
不同於 CI diagnostic artifact 完整性，本機實際使用兩個版本化教學 HTML/CSV ZIP，獨立 controller pin 與實際 subprocess 退出前/後的版本讀回，驗證未知結果先對帳、拒絕 stale retry、回退目標亦重新驗 bytes。POSIX 同一檔案系統的暫存指標 flush/fsync → os.replace → directory fsync 可縮小部分切換範圍，但不等於跨系統交易或斷電保證。先確認真 active 指標與內容，不因程序錯誤碼推斷 mutation 未發生；若舊版資料/產物不完整則停，不盲回退；有新版寫入時依原 migration/restore 契約處理。訓練程式只驗單一可信 writer、受控目錄，無並行 CAS、真部署、runtime service health、data migration 或外部 UAT；不可直接作部署程式。詳 [實作與限制](../../../docs/training/reviews/2026-11-15-ci-artifact-integrity.md#2026-11-16-本機版本啟用與復原訓練)。

### GAS Web App 公開存取與瀏覽器工作階段（GAS-ACCESS-SESSION-001）
已開放存取但非部署者無法開啟時，不先重部署、改程式或放寬 ACL。先唯讀核正式 /exec、deploymentId/version、access（ANYONE=已登入，ANYONE_ANONYMOUS=含未登入）、executeAs；使用同一 URL 在乾淨無痕／獨立瀏覽器設定檔測所需匿名或僅一個合法非部署者帳號，另驗不應有權限的管理與資料功能。多帳號工作階段為待核來源的排查假說（原官方實讀宣稱已撤回，使用前查當前正式文檔）；若乾淨 session 成功而原環境失敗，先排 session/multi-login，單帳號或獨立 profile 優先，再知情同意下清除相關網站 Cookie/資料（可能登出、清掉偏好）；無痕也可能受第三方 Cookie 限制，不單以此判定部署失敗。都失敗再查 Workspace、OAuth、應用層/後端 ACL 與實際錯誤。不接受 cookie/token、不公開資料源、不盲重部署或誤升權。依 [原案例及待核參考連結](../../../docs/training/DECISION_LOG.md#gas-access-session-001gas-已開放存取但其他帳號無法開啟2026-11-16user_reported_recovery--official_doc_corroborated--index_candidate)；使用者回報清除 Cookie 後其他帳號恢復，根因未獨立重現；不可當正式跨帳號 UAT。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 deployment-plan；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。

### GAS 多層版本同步及唯讀對帳（GAS-DIAG-002）
分開核目標 Git SHA/完整轉換後文件/HEAD/固定 versionNumber/deploymentConfig/WEB_APP URL+access+executeAs/真 runtime；先界定候選來源與 active release，HEAD 可合法未發布。getContent HEAD 與指定 version 分讀；deployment GET 核 scriptId、version、entryPoint；updateContent PUT 全量替換，非 patch，須完整 manifest+文件、備份、獨立授權、寫前與寫後對帳；未知結果停相關寫入。更新原 deployment 可維持 URL，禁止盲建新部署；原 owner 變更/跨網域與資料相容 rollback 另核。詳 [GAS-DIAG-002](../../../docs/training/reviews/2026-11-16-gas-diagnosis.md)，離線 advice 不代表真 GAS 操作或部署核准。


### TD-004｜可重現開發工作區及工具鏈（TD004-DEV-ENV-01）
設定與runtime分離：先核實際OS/CPU、cwd、解譯器/Node/npm版本、command path與IDE/terminal/task/debug各有效scope，不能只看VIRTUAL_ENV或IDE狀態。Python每project重建venv（不複製），以完整解譯器路徑及sys.executable/prefix/base_prefix、版本、套件來源檢查；注意PYTHONPATH/user site/目前目錄，-I只限其語意不是sandbox。Node核--env-file與既有process env順序、NODE_OPTIONS/preload；以明示最小env和trusted absolute tools避免繼承不必要設定，勿任意讀出.env或完整環境。npm ci核package.json/lockfile與實際runtime/flags，離線local dep測正反、拒絕drift，勿盲用install改lock/升版；陌生repo先review tasks/extensions/lifecycle並限制Workspace Trust，不把ignore-scripts/venv/offline等同安全沙箱。POSIX真實驗、原教材及GUI限制見原覆盤。未授權不修改使用者電腦或全域設定。


### TD-004｜瀏覽器程序就緒與有限診斷（TD004-CHROME-STARTUP-01）
區分spawn（cwd/exe/uid/env）、子程序存活、ready receipt、loopback HTTP/CDP、真頁面與下載五層；DevToolsActivePort缺檔是症狀，不是同一根因。確認實際版本與執行身分、獨立暫存profile、絕對路徑/明示cwd、最少環境變數；Chrome136起非預設profile才可遠端偵錯（正式Chrome），不接管真人profile、不公開port、不為方便新增--no-sandbox。CI原15秒deadline內查退出碼、缺/無效receipt與埠範圍，持續排空stderr但只輸出有限固定分類，不打印環境/argv/raw stderr/token；DBus等訊息本身非必然致命。原HTTP/CDP、真UI與CSV、CSP、安全與quality gates不得降級。失敗只清理本次擁有的程序/profile、保留去敏證據；不得殺全部Chrome或盲目重跑。隔離Linux root拒絕已實測，普通uid可達CDP但本地navigation失敗、遠端原偶發根因未證；exact ef74dea1ab700ae62e12785b8b87bfefdfa78e12候選診斷補強已回讀，完整CI另核。見[原覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜IDE設定範圍、外掛固定版本及復原（TD004-VSCODE-EXTENSION-01）
先確認實際IDE/commit/OS/architecture、profile、local/remote host與workspace scope；一般workspace覆蓋user，但語言專用設定跨scope優先，最後組織policy；區分含註解JSONC、multi-root、remote與profiles，不能將簡化模型等同IDE。先用內建功能，必要外掛核publisher.extension@version、engine/platform、相依與可信獨立digest/簽章，推薦清單不是lock；auto-update/Settings Sync與remote各自確認。未授權不安裝。核准隔離試驗可用分離user-data-dir/extensions-dir/profile與合成workspace，Portable Mode例外；不等於OS sandbox，不盲--force或關簽章/Trust。禁用外掛是診斷，不撤銷既有檔案、設定、登入或外部寫入；保存前後bytes與權限，確認停止本次擁有的程序，未知/內容drift先唯讀對帳，明確恢復已知after-image再核實際功能，不整個清除使用者設定。原本機合成實證與限制見[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜AI工具預算、用量未知與精確核准（TD004-AI-CODING-REVIEW-01）
執行前核實際方案、provider計量單位/價格/配額與上限、是否有超額支出，提示一次可能引發多模型請求、Actions/外部工具另計，無授權預算不呼叫。保守預留每attempt最大單位，結果未知保留預留並停後續/重送，可信對帳後才釋放差額；重播/超額/錯型拒絕。合成整數budget僅single-process fixture，不是持久化計量、真API或供應商價格。平台budget hard stop及usage receipt仍應優先使用，付費/外部工具需另授權。工具變更核精確scope/review(before, after, target)，保留相關檔案與回讀、獨立功能驗收，unknown先唯讀對帳。詳[原覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜.NET SDK、IDE工作負載及建置相依性（TD004-DOTNET-BUILD-01）
先查實際dotnet --list-sdks/--list-runtimes、dotnet --version、exe/architecture/cwd、MSBuild版本、targeting/host packs及VS instance/workloads（Windows用官方vswhere等），不能用SDK代替IDE或runtime。global.json鎖SDK與rollForward/allowPrerelease，不鎖TFM或套件；CLI從cwd搜尋祖先，MSBuild resolver按solution/project位置，注意不同入口。.vsconfig為元件清單、不是完整版本鎖或安裝授權；安裝/修改工作負載涉及磁碟、管理權、重啟及授權，先核精確相容、生命週期、原配置與使用者批准，不偷裝。固定NuGet.Config/來源映射、packages.lock.json與真lock restore，在受控目錄用本地feed/獨立cache驗；build --no-restore分離restore驗收，不忽略失敗源或任意清全域cache。官方2026-11-18版本核對.NET8/9已EOL，VS2022不正式支援net10 targeting；合成舊target僅教學，非正式部署建議。詳原[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜範本註冊、隔離生成與安全恢復（TD004-DOTNET-TEMPLATE-01）
先核現有SDK版本、template identity/來源與適用版本；dotnet new install本機目錄僅在授權隔離環境可用，隔離HOME與template hive（debug開關依版核對，非公共穩定API）、快取、cwd與輸出，關閉非必要更新，不下載第三方。dry-run看計畫不等於安全/功能驗收；實際生成到新目錄，碰撞不得盲用--force，保留既有bytes；核實postActions及分開restore/build。自製範本uninstall只解除註冊，不刪已生成專案或撤銷腳本副作用；未知/競寫依原唯讀對帳。只清理本次owned臨時目錄，無真人環境操作。詳原覆盤。

- TD004-DOTNET-TEMPLATE-01 實際紅測：.NET10 CLI可先生成檔案再報post-action 105（即使continueOnError=true），不得以非0推斷未寫入；明示核對exit/實際檔案與副作用，再決定是否只補已核准action，禁止盲重送或--force。實際最終回歸另核原覆盤。


### TD-004｜原生ASP.NET Core本機功能驗收（TD004-DOTNET-CONSOLE-MVC-01）
預裝SDK需同時核.NET及ASP.NET Core ref pack/runtime，用SDK內建範本而非第三方下載；驗實際build與DLL，分launchSettings、ASPNETCORE_URLS、環境及實際binding，受控HTTP用127.0.0.1:0取得真port，不將localhost:0、port猜測或ready log當HTTP功能成功。固定owned process及逾時、真HTTP請求、finally只終止本次程序；合成HTTP非TLS/正式部署或安全sandbox。詳原覆盤（CI待驗）。


### TD-004｜DI組裝前置及PRG驗收（TD004-DOTNET-MVC-LAYERS-01）
不要依賴Development預設驗scope；應依實際host明示ValidateScopes/ValidateOnBuild、驗錯誤註冊在開始listen前拒絕及正常host真HTTP。DI驗證不涵蓋所有factory/open generic/動態解析，亦不等於完整dispose證據。303表示後續GET/HEAD查資源，RedirectToAction預設302、307/308保留method；顯式核Location、實際GET/刷新與state，不自動follow不可信外站。沿既有loopback、owned process、超時及版本守門。詳原覆盤（CI待驗）。
