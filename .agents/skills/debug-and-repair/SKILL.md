---
name: debug-and-repair
description: "功能壞了、幫我除錯。developer 角色；交付 repair。"
---
# debug-and-repair｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：依任務所需。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
重現錯誤，最小失敗測試，定位根因及受影響模組；必要時交 SRE 與 Security。修正候選程式並跑正反測；未知 POST 不重送。記錄修復前後、仍未解限制，不重做已驗證成果。

### 互動狀態修復
若確認後的資料仍可修改，將確認綁定當前內容；任何編輯、改選或取消都要讓舊確認及其可見預覽失效。空白草稿拒絕確認、非空白重新啟用，但不能自動核准。分開檢查核心狀態與介面事件，以固定的真實正反例重現原缺陷、最小修復並重跑相同檢查。案例見原決策紀錄 NATIVE-TRANSFER-002 及 NATIVE-UI-003；不把本機 DOM 成功或 literal True 當成人類操作或外部權限證明。

### GAS Web App 公開存取與瀏覽器工作階段（GAS-ACCESS-SESSION-001）
已開放存取但非部署者無法開啟時，不先重部署、改程式或放寬 ACL。先唯讀核正式 /exec、deploymentId/version、access（ANYONE=已登入，ANYONE_ANONYMOUS=含未登入）、executeAs；使用同一 URL 在乾淨無痕／獨立瀏覽器設定檔測所需匿名或僅一個合法非部署者帳號，另驗不應有權限的管理與資料功能。多帳號工作階段為待核來源的排查假說（原官方實讀宣稱已撤回，使用前查當前正式文檔）；若乾淨 session 成功而原環境失敗，先排 session/multi-login，單帳號或獨立 profile 優先，再知情同意下清除相關網站 Cookie/資料（可能登出、清掉偏好）；無痕也可能受第三方 Cookie 限制，不單以此判定部署失敗。都失敗再查 Workspace、OAuth、應用層/後端 ACL 與實際錯誤。不接受 cookie/token、不公開資料源、不盲重部署或誤升權。依 [原案例及待核參考連結](../../../docs/training/DECISION_LOG.md#gas-access-session-001gas-已開放存取但其他帳號無法開啟2026-11-16user_reported_recovery--official_doc_corroborated--index_candidate)；使用者回報清除 Cookie 後其他帳號恢復，根因未獨立重現；不可當正式跨帳號 UAT。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 repair；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。

### GAS 多層故障定位（GAS-DIAG-002）
先核目標/正式 URL/未知 mutation/越權及版本，再比較同一合法訪客的原與乾淨工作階段，不以不同帳號或無痕成功確診 Cookie。頁面能開不等 RPC 正常；google.script.run 非同步，核 success/failure handler、亂序、支援參數型別、Console/Network（脫敏）及 Executions Failed/Timed out；依 scope/執行身分查下游權限、配額。timeout/回應遺失不證未寫，依原 receipt/唯讀對帳，不能盲重送；不收 cookie/token/raw HAR、研究資料。詳 [實作與來源](../../../docs/training/reviews/2026-11-16-gas-diagnosis.md)，不擅改真站。


### TD-004｜SQL結構化除錯及實際計畫（TD004-SQL-DEBUG-01）
先固定engine/version、schema與可重現輸入和獨立業務真值。分類SQLSTATE，不依本地化文字；同碼再看schema/table/constraint/column、GET STACKED DIAGNOSTICS detail/context與原callsite，欄位可空且可能含個資，僅授權內部診斷、公開/客戶端用安全代碼，不通用吞23505或把NOTHING/零列當成功。同ID重播另核payload/actor及未知結果先唯讀對帳。慢查詢先讀EXPLAIN，EXPLAIN ANALYZE真執行、有副作用或未授權不做；隔離測JSON實際與估算rows/loops、buffers、資料分布與stats，成本非毫秒、每loop平均別誤乘/重加。高度相關欄位可試extended statistics但不能推廣到所有條件。重複掃描可用集合重寫，核每個鍵/NULL/缺格、來源不變及前後真計畫，不盲加index或提高timeout；57014別一律判逾時/安全重試。保留最小失敗反例/修正及原始CI，限制與證據見[原覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。非正式負載或原T-SQL。


### TD-004｜開發環境差異與最小故障定位（TD004-DEV-ENV-01）
同源程式在不同工作區失敗，先核實際exe/version/cwd、PATH順序、Python prefix/import及Node env-file/已有env、NODE_OPTIONS預載入與npm lock，再判原始碼問題。正反例同固定小輸入，帶空格路徑、錯venv、缺模組、污染import、版本不符、缺.env、lock drift；用明示exe/最小env/還原manifest最小修復，核輸出/lock bytes/副作用，禁止盲裝套件或刪全域設定。只輸出必要非敏感版本與分類，不記錄完整env/secret。CI或browser啟動不等於應用故障；查process/ready及有界去敏stderr，不盲拉timeout或重跑，不降gate。真VSCode GUI與Windows另驗，詳原覆盤。


### TD-004｜啟動失敗不冒稱功能失敗（TD004-CHROME-STARTUP-01）
IDE顯示/程序PID/portfile/HTTP與實際DOM、檔案副作用分層，缺receipt先查實際退出碼與安全分類日誌，在原deadline fail closed，勿直接讀不存在或格式錯誤的receipt。固定新profile與cwd，一次一變因；root拒絕改普通uid可修該環境的啟動層，不代表遠端根因；Chrome136資料目錄限制亦需核版本及實際適用。使用者真PC不動、不收raw env/argv/日誌，既有browser acceptance不降。保存red（包括測試器本身錯誤）及正例完整驗收；新候選測試真子程序退出/缺檔/非法port與去敏碼，完整CI待查。原[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。
