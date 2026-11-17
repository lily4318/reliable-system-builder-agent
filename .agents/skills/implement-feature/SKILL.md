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
