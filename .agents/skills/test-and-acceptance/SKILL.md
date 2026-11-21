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


### TD-004｜受限匯入角色與診斷負測（TD004-DB-SECURITY-01）
在實際引擎以各自非管理受限連線驗合法收件/讀取/轉入，禁止直接查改基表、跨批次、偽裝TEMP view、修改schema/PRAGMA/ATTACH、caller繞過封存或透過OR REPLACE/IGNORE覆寫；核拒絕原始錯誤碼與所有相應表前後快照，正例其他批次保持不變。拒絕報告核欄位與範圍而非只看UI隱藏，外部錯誤固定代碼與原始日誌另測。SQLite固定scope/authorizer為可信host的連線級實驗，不能冒稱真身份登入、任意程式隔離、全部資訊洩漏防護、真研究安全或PG/SQL Server測試。


### TD-004｜SQL修改意圖與副作用驗收（TD004-SQL-SEMANTICS-01）
刻意測預覽未涵蓋的年份/NULL、其他scope、過期版本、已非允許狀態及不存在鍵，核實際受影響鍵、欄值、最終持久資料；WHERE存在不代表精確，RETURNING/rowcount成功也非完整副作用或commit。以AFTER trigger故障注入核回傳與真SELECT不同並回滾，固定全資料行oracle；SQL集合查核另測NOT IN含NULL、NOT EXISTS、EXCEPT/INTERSECT、UNION與UNION ALL、兩向集合相等但重複筆數不同。勿把自建演練當產品事故或實際併發；跨引擎原生語意、真ACL/競寫與大型負載另驗。


### TD-004｜聯結與研究統計的真值驗收（TD004-SQL-JOIN-01）
固定oracle逐鍵與每人的測量、報酬；刻意設多個合法child、同額/同分、只有不合資格右列、無右列、跨scope同ID。驗ON/WHERE/OR NULL/HAVING篩選是否保全目標母群，核COUNT(*)與非NULL child key、實測人數/事件數、SUM DISTINCT負例、分別預聚合後逐欄與原子表直接總和。平均的觀測單位與缺失分母依規格而非SQL結果筆數；衍生名單重複鍵應拒絕、修正後來源不變。去重負例保留真正獨立事件，禁止未授權物理刪除。受控假資料3/3不等於真資料、併發、效能或完整引擎驗收。


### TD-004｜異構UNION及遞迴CTE驗收（TD004-SQL-CTE-01）
以逐來源鍵、欄序/值/單位/型別及拒絕清單為oracle，測位置互換但查詢成功、CAST部分有效/非法被吞、前導零及同來源局部鍵；原始值保持。重構前後核逐鍵與精度邊界，避免先整數化avg改變篩選。遞迴負測環、self-loop、多路徑、跨scope及depth邊界，在受控資源內實測取消；外層WHERE或帶depth的UNION非終止保障。核路徑、唯一節點、循環狀態及深度截斷的未展開frontier，無完備證據不承諾完整；圖寬/資源預算、真身份/任意鍵編碼及引擎特有行為另驗。合成SQLite 3/3非SQL Server或獨立模型評測。


### TD-004｜逐列與Pivot真值驗收（TD004-SQL-CURSOR-PIVOT-01）
逐筆與集合結果用固定逐鍵oracle驗同tick、負值、多次threshold crossing、ROWS/RANGE及穩定順序；測同cursor內層重執行截斷外迴圈、記實際SQL trace次數而非推估耗時。寬表核精確欄名/順序/列值（含rows/valid/sum）、無觀測欄、全NULL/真0、同分合法兩筆、未核分類；刻意測補0混淆、DISTINCT丟合法觀測、空/重複/未知/注入樣動態欄，回讀原事件未變。來源粒度與母群按需求，不以合計相同證明原始可逆。3/3本機SQLite為合成測試，非真研究、SQL Server、UNPIVOT或獨立模型。參見[原覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜排名與分層的逐鍵驗收（TD004-SQL-RANKING-01）
固定oracle比較ROW_NUMBER/RANK/DENSE_RANK及top-N入選ID與人數，特別測邊界同分、跳號、加ID破壞peer及兩種索引路徑下無tie-break的反例；反例計畫依引擎，不將未指定排序當固定契約。測資格過濾先後、跨研究同局部鍵/同組名、真0與NULL、合資格與有效分母；NTILE驗不能均分、小母群、同分拆組、非法N及原事件不變。結果與分析母群、排序及版本一起追溯；不把排名或NTILE當真隨機分派/百分位數驗證，實際研究規格與引擎另驗。詳[原覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜View契約相容與負測（TD004-SQL-VIEW-01）
以固定欄序、逐鍵值、scope與NULL/0作oracle，增底層敏感欄測SELECT *漏出；直接測合法/禁止的底表與view入口（唯讀非ACL），DML拒絕後核底表完整快照。刻意破壞欄名/相依consumer，實查下游失敗，再按引擎交易回滾核舊結果、相容替換提交後重驗。普通view即時更新不證快照；測試不能只看CREATE成功或行數，亦不把SQLite受控實驗當SQL Server/RLS/真研究驗收。原教材正文未取得，官方證據見原覆盤。


### TD-004｜Trigger多列與跨表原子性驗收（TD004-SQL-TRIGGER-01）
固定多列同組/跨組逐列OLD/NEW、原明細聚合與衍生統計oracle，測重複/no-op、NULL→0/0→NULL及拼錯UPDATE OF欄位；核全部相關業務表、審計與先前交易marker而非rowcount。受控深度重現遞迴錯誤，實查交易active及未提交部分異動，再顯式rollback驗恢復；合法有界收斂另測。刻意第二列巢狀審計拒絕，比FAIL/ABORT/ROLLBACK各scope，查正例commit與拒絕後完整狀態；不把錯誤、DDL成功或已寫audit當已commit。SQL Server集合delta及真引擎錯誤/鎖/權限、外部副作用與不可竄改審計另驗。詳原覆盤，原教材正文未取得。


### TD-004｜程序輸出、異常及提交邊界驗收（TD004-SQL-PROCEDURE-01）
真CREATE PROCEDURE/CALL與catalog prokind驗，測具名、NULL/非法、OUT/INOUT、舊版/跨actor與固定輸出；查逐值和所有相關表，不以SQLSTATE或result row成功冒稱業務成功。真獨立低權限連線測EXECUTE-only、INVOKER/DEFINER、direct DML、PUBLIC/其他actor與temp shadow。捕捉例外後核局部變數與子交易資料差異及caller marker；頂層/外部transaction、DEFINER與SET限制、先commit後故障，另一連線查持久化部分；非所有錯誤一律rollback或盲重試。按實際CI原始日誌標示PASS、非本地缺引擎/SQLite mock、非T-SQL/正式ACL；詳原覆盤，原教材未取。


### TD-004｜函式回傳、穩定性及索引真值驗收（TD004-SQL-FUNCTION-01）
固定逐人/觀測ID及值oracle，scalar零列與NULL、SET空列/同分多列、STRICT versus CALLED ON NULL、CROSS/LEFT LATERAL及count非NULL鍵/值、原表不變。以真長存活PREPARE跨另一連線修改設定，對照舊plan/新query、修正標記後重建plan並再改設定。VOLATILE副作用核實表、STRICT NULL跳過、STABLE違規DML拒絕及同敘述snapshot差異。故意錯IMMUTABLE建立expression index，固定真EXPLAIN路徑與逐鍵結果比較index/seq、刻意更設定再驗；修復錯索引和函式、純固定版本索引兩路徑等價及來源不變。GUC只在隔離驗收，不以計畫匹配為效能證明；非T-SQL/正式資料庫/研究政策/獨立能力。原始CI狀態依原覆盤。


### TD-004｜SQL診斷與修復的獨立真值驗收（TD004-SQL-DEBUG-01）
測同SQLSTATE不同constraint及正確診斷欄、錯誤ON CONFLICT零回列卻漏合法新id，限定constraint後其他衝突必須浮現，合法輸入逐列核實；正式重播payload另驗。用相同合成分布取EXPLAIN ANALYZE JSON/估算actual rows及loops/buffers，核stats前後固定實際數及不相容條件；集合重寫用獨立逐鍵oracle驗所有母群、缺失與源資料，觀測scan減少不當延遲倍率；避免固定時間門檻、未授權EXPLAIN ANALYZE寫入和輸出敏感日誌。受控timeout/其他錯誤分類與session恢復，按真CI原始日誌驗收，非正式效能/SLA或真資料。


### TD-004｜真重疊交易、SSI及SAVEPOINT驗收（TD004-SQL-TRANSACTION-01）
以兩獨立backend pid/同時active transaction及交錯讀寫證明重疊，非以thread數或順序測冒稱競寫。固定至少一位active的跨列真值，RR兩筆各自合法仍皆commit而0，SSI允許40001在write/commit且只一筆成功；核另一連線的每列與變更log，完整fresh replay重新判斷兩人拒絕/三人可成功，非盲DML retry。SAVEPOINT真NOWAIT前後55P03、23505/25P02恢復、保存點前後逐列及鎖、RR舊快照與fresh值、sequence空洞及commit後釋鎖；不以rollback訊息或rowcount當完整真值。保留原CI正反證據及未驗混合隔離、高併發、driver/正式效能；不降品質gate。


### TD-004｜研究資料端到端獨立數值與安全真值（TD004-SQL-HOMEWORK-01）
建立逐study/person/wave/attempt/version的常量oracle及每組planned/submitted/complete/sum；至少含同值合法重測、真0、部分缺答、全缺答、未提交、跨研究重複ID及同原答不同version。核原版報表不漂移、不同版不混合、受限身份只得scope，direct raw、版本/狀態篡改、跨研究/不存在及anon拒絕且全表不變。真late check failure（先更新狀態）及外層rollback逐表核，長存活讀快照與另一提交交叉驗，同一訪視雙連線實查blocking及競爭不同payload只一份定稿。逐鍵oracle而非僅rowcount/CI分數；真CSV、正式研究工具效度/權限/資料治理與獨立Agent評分另驗。原課程作業未讀，原覆盤記證據限制。


### TD-004｜C#版號決策、短路副作用及原生負測（TD004-CSHARP-POLICY-BRANCHING-01）
以獨立固定逐欄oracle核同一觀測在不同版門檻的不同結果；逐別測null/false/true consent、quality hold與insufficient的優先序、合法0與missing、未知version、bool/float/overflow/錯shape及重複JSON欄。驗證同一輸入兩文化輸出一致、來源bytes不變、拒絕無部分結果。短路/非短路呼叫數、括號優先序與nullable lifted結果用實際runtime；`const`變更、動態initializer及非bool if以真compiler code/無輸出DLL驗。驗同版SDK/ref/runtime、empty local NuGet feed/沒有第三方package，結合原生單元測試、全CI及精確checkout SHA，不拿新C# marker代替全局CI。首次CI44850341988因原Chrome就緒timeout而全局red；補限縮診斷後CI44851069296 581/581 green，但真Chrome根因未證。人工、Windows、真研究字典及外部部署另驗。

### TD-004｜C#迴圈預算、參數副作用及例外隔離 QA（TD004-CSHARP-BOUNDED-METHODS-01）
至少驗空資料、正好budget、超出budget、STOP於預算前/後、STOP尾端未讀、合法0/null、重複ID、錯shape/型別/值域；檢查status/inspected/valid/missing/sum逐欄，不只比總和，失敗不得回傳部分sum或動原輸入bytes。方法以獨立oracle比ReadOnlySpan純讀、變數ref修改、array alias寫入、out成功/失敗值；用會throw的真iterator驗finally清理及結果尚未提交，以break驗不多拉取。另以原生compiler檢loop scope/缺ref/未賦值out三負例與壞build無DLL，核.NET SDK、NuGet empty feed、不同文化及exact CI checkout。33固定/192獨立Python小域組合及CI44852671230 582/582 verified；此為合成host QA非真DB/網路IO/異步、完整JSON資源界限、原教材或盲測。不可把CI marker替代全局品質守門。
