---
name: test-and-acceptance
description: "測試網站、驗收功能。qa-uat 角色；交付 qa。"
---
# test-and-acceptance｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：implementation。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
獨立閱讀規格、實作與驗收；針對成功、拒絕、競寫、重複、異常及復原執行適用功能測試；對 UI 實際操作，檔案及同 SHA CI 回讀。失敗交 Developer 修正；無真實 UAT 不聲稱通過。

### 互動確認的實際 DOM 驗收
不能僅憑純函式、HTTP 成功或靜態 HTML 字串判定 UI 通過。先固定原始需求與精確檔案版本，使用可用的真實瀏覽器執行選擇、修改、確認、確認後編輯、空白拒絕、重選、取消及取消後重新操作；檢查控制項狀態與可見預覽一致、舊確認失效、輸入以純文字顯示、不自動送出或核准外部操作。原示範回歸見 `python -m src.website_intake_browser_test` 的 EDITABLE-DECISION-BROWSER；測試工具的本機回報不是產品送出。缺瀏覽器或平台介面時明示未測，不要求模型安裝或假造 UI 證據。區分自動 DOM 驗收、真人 UAT、正式授權；回讀精確 SHA 及 CI。

### 驗收器本身的負向驗收（NATIVE-EP-010-ORACLE-BOUNDARY）
先核對合法輸入域、最大工作量、數值端點、空/滿載、短路/最壞分支與資源預算；對公開 oracle 以已知錯誤候選測「能否拒絕」，不是只有正確參考程式 PASS。必要時在受限解譯器直接獨立跑合法邊界，對照整合 host QA 退件、修復及精確版本。保留原固定預期值/安全白名單/資源限制；不要為通過放寬限制或執行任意候選 native code。測試契約變更需新 oracle version/hash，歷史 PASS 不替代新版。原 EP-11、CI 43704461951 red / 43704563695 green：12→18公開樣本仍非全域、獨立盲測或正式產品驗收。

### 同一網站的多層實際驗收（NATIVE-WEB-014-EDITORIAL）
功能完整度依確切 R/A 追溯；把資料交易/角色/HTTP/DOM/CLI 啟動及復原分層，不能用某一層 PASS 代替其他層。對版本公開切換、原 actor token replay、未知寫入分別測未提交 subprocess cut 與已提交但回應丟失、直接 API 越權及重新登入唯讀查 receipt；真 DOM 在 exact viewport 驗分頁、鍵盤、稿件與公開視圖狀態。不得為 runner 放寬 Origin/CSRF/ACL 或加入日常 test route。CI 43708288874 434/434 +375/1280 each29；受控本機，不等於真使用者 UAT、完整 accessibility/security audit 或正式部署。
### HTTP framing 跨解析器與無副作用驗收（EP-12）
以本機真連線對同一舊版建立 red 測試，正確內容前綴但未收足宣告 bytes、異常標頭、逾時等負例；具權限的操作也不能因解析成功執行。驗收 oracle 包含狀態碼及所有相關業務表（包含負向決策 ledger）與可行時原檔 bytes；單用 4xx 或庫存不變不足。正向保留合法編碼及原冪等語意，固定 red/green SHA。實例 NATIVE-HTTP-020/021 詳 [原覆盤](../../../docs/training/reviews/2026-11-15-http-framing.md)；不把 loopback 或其他網站 DOM 當真設備 UAT。


### 動態資料跨模組與匯出驗收（TD-005 Developer/QA）
正反測追溯字典、版本、批次、缺失值與匯出格式；拒絕時核對所有相關紀錄、revision 及事件。使用獨立解析器路徑讀回 CSV 並比預期值/欄序/資料版本，非只看行數。以真第二連線在讀版本與讀 rows 間提交，核對兩者同一快照及下一版正確，重複匯出 bytes 必須一致。對危險文字前綴、逗號、引號、CR/LF 和 Unicode 測完整可逆性；不把 CSV quoting 或合成 prefix 檢查當 Excel/其他試算表的完整安全證明。詳 docs/training/reviews/2026-11-16-research-data.md（10/10；對照 8 failures；非獨立盲測、真人UAT）。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 qa；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。

### 心理實驗的瀏覽器時序品質（TD-005）
用真瀏覽器執行刺激 DOM 和自動化按鍵，同時計錄不同時間代理與 QA oracle，負測 wall clock 注入、主執行緒阻塞/延遲、重複或合成輸入、timeout、中斷；檢查狀態、row uniqueness、null 及版本。不將 programmatic blur/hidden/pagehide 冒稱真失焦、或軟體時間代理冒稱硬體精度。實際未產生預期 OS/browser transition 時保留 SKIP/BLOCKED，不計通過；不同設備/瀏覽器及研究者科學精度確認另行驗。原 lab 11 PASS / 1 SKIP；對照8 FAIL，詳 docs/training/reviews/2026-11-16-experiment-timing.md。不得以自動化輸入當人類反應。

### GAS/Sheets 資料完整性 QA（GAS-DATA-003）
區分鎖忙、未送、definitive batch reject、未知已送、晚提交風險；以 row/capacity/receipt/audit/outbox/pending/revision 整體不變或完整提交為 oracle，測 cache loss、相同 token 不同 actor/payload、negative receipt、其他 writer 反例與通知 ACK；無真並行時標模型。restore 先隔離副本，核可信 checkpoint 完整資料、收據、未決 mutation/通知及新版增量，不只比筆數，另查原始值/欄位/ACL/附件/復原相容；直接 version restore 可能破壞編輯歷史。配額與 actual API、真備份復原另驗，不能以 18/18 模型當 Google UAT。詳 [覆盤](../../../docs/training/reviews/2026-11-16-gas-data-integrity.md)。

### Trial 持久化 QA（TRIAL-RECOVERY-004）
真 reload/close/reopen + 獨立資料讀回，核原 pending/terminal row、parent、新時間原點、null 與 receipt；注入 commit 後 UNKNOWN 和 transaction rollback，重放同 payload 不變、不同 payload 拒絕，舊分頁 finish STALE、雙 tab 只一開始。host binding 非 HTTP、同步 callback 非真競寫鎖等待；browser origin storage 受限須標未驗而非偽造成功，不改安全政策。詳 [9/9 本機替代實測及限制](../../../docs/training/reviews/trial-recovery-004.md)。


### TD-004｜資料語意的負測（TD004-DB-KEYTYPE-01）
移轉驗收除行數/FK/唯一限制外，使用固定來源識別及期望的目的父子資料核對語意，刻意測「FK合法但指錯人/項」；拒絕重複業務鍵/穩定鍵及孤兒，核實副作用。型別核前導零、精確小單位值、起點/末秒/次日午夜、非法值及資料不變；相同合計不代表行內容正確。原 SQLite lab 僅支持固定格式 UTC 與本機型別限制，尚須按實際 API/DB 驗字串 coercion、bool、任意時間有效性、時區/DST、T-SQL、交易衝突及研究政策；不把自建故障對照當產品 bug 或真盲測。


### TD-004｜正規化及關聯生命週期驗收（TD004-DB-NORMAL-01）
拆表前後核固定預期行及語意，刻意重現插入/更新/刪除異常；無損接合與依賴保留分別驗，局部PK/FK合法仍可能失去全域業務唯一約束。版本新建後核舊事件與觀測值不變，拒絕刪被引用版本和不存在版本、核CASCADE/SET NULL影響範圍，不以FKcheck=[]代替業務驗收。不把保存歷史版本誤當防止任意UPDATE/DELETE或授權；依真需求另測不可變性、權限、稽核及交易競寫。自建示範與真產品故障區分，不冒稱完整原教材或獨立模型遷移。


### TD-004｜索引效能與結果等價驗收（TD004-DB-INDEX-01）
固定相同schema/data/查詢及逐行預期（含ORDER BY），先核實引擎版本及統計；比較實際EQP中的使用索引、搜尋條件、TEMP B-TREE、covering，加取未索引欄位做負例。分開量測讀取與同交易插入/更新、配置大小、資料完整性，重複取中位數並明示暖快取、合成分布、順序、記憶體環境等限制。VM callback不是I/O；不以單次時間、SEARCH、或固定EQP字串當通用產品契約，不設定跨環境僵硬耗時斷言。原測2/2非全負載、並發、引擎及真實使用驗收。


### TD-004｜資料匯入逐筆診斷與對帳（TD004-DB-IMPORT-01）
以原來源、核定schema/欄位語意與目標前狀態為oracle，測編碼、錯header/欄數/引號、合法與非法混批、重複與既有鍵衝突。全批拒絕時驗原資料不變、無成功收據，若保留診斷則核來源列及所有適用原因；在寫入後的receipt或逐值對帳注入真正失敗，驗promotion整體回滾及staging可追溯。count/sum相同不足以判資料正確，驗鍵與每欄/版本差異、保留舊資料，確認已提交批次不重寫。受控SQLite故障注入非真產品故障或未知ACK、並發/耐久/SQL Server BULK INSERT實機；正式資料的診斷保護、權限及大批量另驗。
