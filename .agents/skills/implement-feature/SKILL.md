---
name: implement-feature
description: "完成某功能、實作網站。developer 角色；交付 implementation。"
---
# implement-feature｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：specification、architecture、plan。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
先核對已授權候選工作區與規格確認；只做最小可運作垂直切片。讀現有程式及案例知識，寫實際程式與正反測，執行它們、讀完整錯誤、修復後重測。產物記錄檔案、commit、測試命令和結果；不把空函式或計畫當交付。

### 完整縱向網站訓練交付（NATIVE-WEB-014-EDITORIAL）
確認具版本需求與獨立候選寫入範圍後，優先完成同一網站從公開頁、私有工作台、資料/交易/API 到真實操作的閉環，不以孤立函式或 schema 檢查替代整體交付。按需求分離 public pointer 與 private draft、版本綁定核准及 mutation receipt；未知回應先原 actor 唯讀對帳。以階段 exact SHA/CI 及逐項需求驗收轉交；本機運行、正式部署及真人 UAT 分開。WEB-EDITORIAL-01 的 434/434 與兩種 viewport 各29實測見原訓練主檔，不泛化為任意網站成功或模型分數。

### 動態研究資料驗證與版本化交換（TD-005 Developer/QA）
依研究者核准的資料字典、欄位型別/值域、missing 與更新語意，將可接受輸入、唯一鍵、版本及 revision 守門、資料和事件更新置於同一交易。不得把 bool 當整數、缺失值補 0、靜默改研究資料或以逐列提交冒稱原子批次。匯出須明確消費者/格式、同一讀取快照、固定欄位排序與版本、可重現 bytes，必要分離機器交換與試算表閱讀格式；保留原文字及可逆契約。合成 lab 見 docs/training/reviews/2026-11-16-research-data.md；未證真試算表、正式資料字典及雲端。不要將固定合成規格套到真研究。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 implementation；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。

### 心理實驗的受控時序與事件狀態（TD-005）
使用同頁 performance.now()/Event.timeStamp 區分事件發生與處理時間，記錄刺激 DOM 寫入、frame readiness、response window 和中斷事件。以 trial identity 防舊 callback 導致新 trial 污染；結束只一次，取消 callback、區分 valid/invalid/missing，保留原始原因/null。防 held/repeat、不可信程式事件（非反作弊保證）；依已確認研究規格處理 focus/visibility/pagehide、延遲及未完成；持久化和 reload 另驗，不把頁面離開事件當可靠收件。見 docs/training/reviews/2026-11-16-experiment-timing.md；lab 不覆蓋完整 pending watchdog、硬體精度和全部真生命週期。

### GAS/Sheets 單寫入者及冪等故障處理（GAS-DATA-003）
tryLock 失敗不寫、finally release，鎖內重新查 id/receipt/容量；SpreadsheetApp.flush 在必要時於釋放前執行但非 rollback。使用同 workbook 一次 batch 寫業務/receipt/audit/outbox，values API RAW 或 UpdateCells typed stringValue/numberValue、精確 range/field mask（不混淆 RAW 與 UpdateCells），cache 非持久 receipt。未知 intent/remote ACK、partial/跨 writer 先對帳並阻擋共享寫入，不盲重送；定案未送/確定拒絕才按原契約恢復。額度錯誤有界退避/jitter 不持鎖等待，外部郵件/PDF 狀態分開、UNKNOWN 不自動重發。詳 [覆盤](../../../docs/training/reviews/2026-11-16-gas-data-integrity.md)；受控 JS 模型非生產 adapter。

### Trial 重開與未知結果（TRIAL-RECOVERY-004）
先交易提交 pending，再呈現；恢復依 durable current 狀態，明示 retry 在同交易保留中斷與新 attempt；expected ID/current doc/origin 避免舊回應污染。終結與 receipt 同交易，相同 payload replay、變更 conflict；未知提交唯讀對帳，拒絕舊來源與負 RT。不要用 reload 或 unload 自動重新計時/刪除舊資料；跨網路/雲端在途/真身份另驗，不能直接部署此 host bridge。詳 [覆盤](../../../docs/training/reviews/trial-recovery-004.md)。


### TD-004｜資料匯入暫存與原子推進（TD004-DB-IMPORT-01）
依已確認的編碼、標頭/欄位映射、格式、唯一性及新增/更新政策，保留來源bytes/hash與版本，界定大小/筆數、暫存解析值及可追溯邏輯列號；不預設清表、刪除重複或強制ANSI。分開staging與target promotion，在權限/一致性保護的交易內重驗暫存與現有資料、拒絕或寫入全部核准列，逐值對帳及成功收據/狀態同交易；拒絕報告可獨立留存但應最小揭露。不能以bulk命令成功、MAXERRORS、批次已提交或總額相同代替驗收。原SQLite小型實作見[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)；正式匯入需另驗來源不可變/角色ACL/資料留存、上限與大量效能、未知提交對帳及引擎bulk特殊約束，不能套用小樣本全表載入。


### TD-004｜精確SQL更新與集合語意（TD004-SQL-SEMANTICS-01）
預覽與mutation必核一致predicate及明確scope/主鍵；CASE應依核定條件涵蓋ELSE與NULL語意，WHERE比預覽廣會意外修改範圍外資料。WHERE帶可信範圍、記錄身份、預期版本及允許原狀態，使用參數化SQL，逐列版本而非一律全庫revision。零列不等於單一原因、回傳受影響鍵不等於commit或AFTER trigger最終狀態；未知結果先唯讀對帳，不盲重送。集合比較需分NULL、distinct與重複次數，非NULL expected key的NOT EXISTS可避免NOT IN受NULL影響，雙向EXCEPT不能驗bag multiplicity。依實際引擎核定rowcount/RETURNING/OUTPUT及交易語意。原SQLite新3方法見[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)，非正式身分授權、真競寫或T-SQL實機。


### TD-004｜資料粒度、關聯與統計口徑（TD004-SQL-JOIN-01）
先確認輸出一列代表受試者、事件、報酬或其他業務粒度，按完整範圍鍵、關聯基數與真實身份聯結。保留母群時將右表資格條件放ON或先篩右資料；WHERE加OR NULL也不能補回已有不合格匹配的左列。多個1:N子表先各自聚合至同一目標粒度，再JOIN，或只查存在性時用EXISTS；COUNT DISTINCT或SUM DISTINCT不能普遍修復fan-out（同額合法事件被消除），明確區分受試者/事件等權平均及缺失值、母群/有效分母。INSERT SELECT以目標粒度唯一鍵與明示欄位驗收；刪除重複必依核定事件身份、留存及授權，不能以同分或名稱判重。原SQLite見[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)，非SQL Server或真研究推論/權限。


### TD-004｜跨來源整合與有界CTE（TD004-SQL-CTE-01）
依核定資料契約明示每個分支的欄序、語意、型別、值域、單位及來源版本/記錄鍵；禁止只靠欄數相同/CAST成功/UNION去重判合法。保留原值與拒絕診斷，識別碼不得數值化；轉型依實際引擎，非單一小樣本validator。重構CTE須保留比較精度與分母，展示格式於計算之後。遞迴以可信scope及根、內部終止/深度、無歧義路徑與循環拒絕或標記、結果/資源預算，明示截斷/未知而非完整成功；路徑與唯一節點語意分開，先核是否允許多父節點，禁止無界MAXRECURSION 0。CTE非永久快照或保證物化；原合成SQLite見[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)，真引擎/權限/完整性與負載另驗。


### TD-004｜逐列處理及寬表統計契約（TD004-SQL-CURSOR-PIVOT-01）
逐列處理先核行順序、同序值的穩定鍵、狀態轉移與資源釋放；有集合/視窗等價方案時以逐鍵oracle比較，ROWS/RANGE、ties與負值跨越不能互換。避免同cursor重執行覆蓋迭代結果及N+1查詢；有真正逐筆依賴再選游標/分批，交易和錯誤清理獨立確認。寬表先確定粒度、穩定鍵、核准欄位/順序、聚合和觀測單位；保留rows/valid/value區分缺格、全NULL、真0與合法重複，原事件另存，聚合非可逆。動態欄位由可信白名單映射識別名，值參數化，額外分類明示診斷及處理政策；固定欄不能因無資料消失。顯示空白、型別格式及總計列與原值/分類分開。詳[原覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)；SQLite Python cursor/FILTER不等於原生T-SQL Cursor/PIVOT/UNPIVOT，真研究統計、引擎鎖、效能與權限另驗。


### TD-004｜排名與研究母群契約（TD004-SQL-RANKING-01）
先確定分析粒度、合資格母群/缺失政策、完整分區鍵、排名方向與同分處理。固定筆數用ROW_NUMBER加核准次排序唯一鍵；RANK依分數peer且跳號、DENSE_RANK依不同值等級，保留同分時不得把ID加入名次ORDER BY；外層展示另明示穩定排序。排名前後篩選不能互換；跨研究/組別分區非ACL、ROW_NUMBER非持久識別或跨版本固定名單。NTILE近似均分列，可拆同分及產生少於N個非空組，非分位數切點或隨機分派；研究資格及tie-break需核准，不以資料庫預設代替研究設計。詳[原覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)；SQLite合成實驗非SQL Server或真研究。


### TD-004｜檢視表作為具版本的查詢契約（TD004-SQL-VIEW-01）
固定核准欄名/順序/型別、欄位投影與列scope，不用SELECT *公開報表；普通view不是資料快照或獨立備份。底表新增/改名/刪欄或更換view時，核下游所有消費者、資料粒度、NULL/真0及逐鍵值，必要時版本化相容介面、按引擎驗DDL與rollback。SQLite ordinary view預設唯讀，但底表仍可讀寫；SQL Server部分view可更新，CHECK OPTION只約束經view寫、SCHEMABINDING與refresh各有前提。實際權限/owner/invoker/底表grant另驗，不用view替代RLS；不套用SQLite migration語意到其他引擎。原3.4.1教材未讀，官方實測見[原覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜多列Trigger及有界同步副作用（TD004-SQL-TRIGGER-01）
先核引擎粒度：SQLite逐列OLD/NEW，SQL Server DML逐敘述inserted/deleted集合，聚合舊/新delta至完整業務鍵；UPDATE OF/UPDATE(column)不等於值改變，NULL-safe判斷按引擎，實測拼錯欄位/無操作。優先約束及清楚顯式交易；Trigger只承擔可驗證同步副作用，避免依賴觸發順序、無界遞迴及觸發外部郵件/API；外部副作用採交易outbox/提交後處理。核遞迴設定、收斂及界限；SQLite3.46.1深度錯誤實留未提交部分異動，FAIL/ABORT/ROLLBACK範圍不同，按交易契約rollback及所有表回讀，未知提交先唯讀對帳。審計同交易會隨回滾撤銷，不是不可竄改或完整拒絕日誌。原T-SQL/真權限/並發/研究政策另驗；[原覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜預存程序與明確交易所有權（TD004-SQL-PROCEDURE-01）
以實際引擎明示參數類型、NULL/預設/值域、具名與輸出欄序/業務代碼；PG CALL/INOUT/OUT與SQL Server EXEC/OUTPUT/return/resultset不同，不用SQLite或SELECT函式冒稱程序。錯誤分類與業務拒絕/已提交狀態分離，避免catch吞錯後以SQL成功判業務成功；PG子交易exception rollback不清區域變數。明示caller或procedure擁有交易；PG頂層CALL內COMMIT可部分持久化，外部BEGIN/SECURITY DEFINER/attached SET限制內部交易控制。原子業務優先caller交易、無任意內部commit，UNKNOWN先唯讀對帳。僅必要EXECUTE，撤PUBLIC，審核非superuser/no-login definer、最小grant、固定search_path及完整schema限定、可信actor範圍，真driver bind/JWT另驗。SQL Server THROW/XACT_ABORT/交易狀態按原生引擎驗。四個原生PG候選方法與狀態見[原覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)，原教材正文未取。


### TD-004｜函式粒度、NULL與volatility契約（TD004-SQL-FUNCTION-01）
明示scalar唯一列/首列選擇、SETOF/RETURNS TABLE粒度及元素型別；空集合、全NULL、真0、合法同值多筆分開，LATERAL選擇按核准母群。STRICT遇NULL跳過函式，不能用內部COALESCE補預設；必要時CALLED ON NULL INPUT。PG IMMUTABLE只給同參數永遠同值的無副作用計算；依資料/設定讀取適用STABLE，寫入或可變值VOLATILE，禁止為效能錯標。STABLE/volatile snapshot不同；SELECT可有副作用，不能假定固定呼叫次數或順序，敏感業務用明確受限入口、顯式權限與交易。依賴外部設定的錯IMMUTABLE會折疊prepared plan或把舊值存入expression index；修正分類並盤點索引/相依與重建、結果一致性，固定參數/版本的純函式僅在業務契約確認後採用。COST/ROWS是planner估算非限制；不把測試GUC當上線調參。PG與T-SQL規格分別確認；詳原覆盤，原教材未讀。


### TD-004｜交易重試及局部復原（TD004-SQL-TRANSACTION-01）
對實際引擎設定隔離等級，界定完整transaction與結果分類；SSI 40001可能在statement或COMMIT，已知abort先清理，再有界重試整筆（含讀取、決策、SQL及參數），不可只重送舊DML或把已aborted transaction的COMMIT/ROLLBACK回應當成功。真業務拒絕停止，未知commit依EP-03查durable結果；外部副作用獨立處理。SAVEPOINT只用於已確定可局部復原的錯誤，核保留/撤銷資料、後取普通鎖釋放、先取鎖保留；RR snapshot不刷新、sequence值不回收。避免放任直接DML繞過不變量；真driver/pool/權限與重試耗盡另驗。原生案例見原覆盤，非正式T-SQL。


### TD-004｜版本化研究資料從提交到報表（TD004-SQL-HOMEWORK-01）
在核准資料契約下，用完整scope鍵固定規則版本、題號與值域，保持NULL缺答及合法重測，不以同值去重。受限入口先驗身份與visit範圍，鎖該定稿對象再判狀態，原答/狀態/log同交易且late constraint錯誤整體復原；ALREADY_FINAL只表示禁止覆寫，不等於成功重放或unknown ack對帳。report明示列粒度、母群/有效分母/版本，讀一致性及匯出來源版本依核准契約；不為簡單將歷史改套current配置。普通角色無底表寫/原答直讀，固定search_path/撤PUBLIC、實際授權分層；session_user只適用獨立DB登入，真driver/JWT/審計治理另驗。見原SQL例與覆盤。
