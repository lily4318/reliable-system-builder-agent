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


### TD-004｜Emmet展開後的網站語意契約（TD004-VSCODE-EXTENSION-01）
VSCode內建Emmet，先核語言模式、includeLanguages映射、syntaxProfiles輸出格式、Tab/建議與自訂snippet scope，不為快捷輸入盲裝外掛。理解 >、+、^、*、$、[]、{} 的樹/兄弟/返回/重複/編號/屬性/文字語意，屬性引用與語言語法分開；生成不等於功能。研究表單固定唯一id、name/label對應、正確input type與required、資料契約；驗實際HTML/DOM、鍵盤及提交，拒重複ID、錯label與錯name，不把HTMLParser token check當HTML5 DOM或完整可及性/功能。原合成手寫等價輸出之Parser正反例已跑，沒有真Emmet engine/IDE實證；[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜.NET專案及建置契約（TD004-DOTNET-BUILD-01）
區分SDK pin、TargetFramework/TargetFrameworks、RuntimeIdentifier、project reference與PackageReference/lock；SDK版本不等於目標API或runtime。先核實際解析與依賴閉包、build前restore、編譯及執行獨立oracle；ProjectReference變更需核下游重建/真正功能輸出，不以舊DLL或obj存在當通過。XML靜態預檢僅限受控fixture、不是MSBuild evaluation；條件/property/import/glob、跨target、Windows .NET Framework/ASP.NET等另用真引擎依版測。原訓練實驗見[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。


### TD-004｜可重用.NET範本與產物契約（TD004-DOTNET-TEMPLATE-01）
先區分project/item/solution與dotnet new CLI/IDE host、identity/shortName/groupIdentity、來源版本與SDK/TFM相容。以runnable原始專案為範本，明示sourceName的檔名/內容替換與typed symbols choice/bool、default、replaces；host/user值可能覆蓋預設。sources/modifiers與條件控制產物，exclude/copyOnly/rename需辨別優先；自訂exclude不要誤丟原必要預設排除，literal資料勿誤替換。避免自由文字插入程式碼/路徑、先校驗型別和名稱；以固定選項的實際檔案清單、bytes、刪除負例、同參數重現（非所有含GUID/日期範本可byte相同）、生成專案build與真輸出oracle驗收，而非只看success。原[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)。

- TD004-DOTNET-TEMPLATE-01 實際紅測：.NET10 CLI可先生成檔案再報post-action 105（即使continueOnError=true），不得以非0推斷未寫入；明示核對exit/實際檔案與副作用，再決定是否只補已核准action，禁止盲重送或--force。實際最終回歸另核原覆盤。


### TD-004｜主控台輸入及MVC伺服器端契約（TD004-DOTNET-CONSOLE-MVC-01）
CLI分args/stdin/EOF，明示culture、型別/溢位/值域、stdout/stderr/exit code；MVC區分conventional/attribute routing、HTTP method、route constraint與業務存在性；明示FromRoute/FromQuery/FromForm，使用窄DTO而非直接綁持久化entity。一般MVC Controller須自行核ModelState.IsValid，錯轉型與業務驗證分離，無效輸入不得執行副作用；檢查實際Razor view/validation summary及編碼、HTTP狀態與可觀察副作用，不僅看200。原生實驗及限制見原覆盤（CI待驗）。


### TD-004｜MVC服務分層、DI與PRG（TD004-DOTNET-MVC-LAYERS-01）
Controller保留HTTP/ModelState/結果映射，領域規則放Service，即使DTO合法也須核業務條件；Data層封裝資料存取及原子性，單project分檔非compile-time架構隔離。明示constructor依賴與Transient/Scoped/Singleton，Scoped同request、Transient每resolve、Singleton全provider；避免singleton捕捉scoped，以實際實例及ValidateScopes/ValidateOnBuild測錯誤。成功POST後以303及本地Location查receipt，無效輸入留表單且無副作用，GET只查詢；PRG不保證重送幂等，独立key+內容契約，同key同payload返回已知receipt、不同payload409，不盲重送UNKNOWN。測真HTTP/實際count而非只看200。原生候選及限制見原覆盤（CI待驗）。


### TD-004｜C#常數、版本化研究規則與分支（TD004-CSHARP-POLICY-BRANCHING-01）
`const`只用於編譯期不會更改的結構性常數，政策版號/研究規則須具明確版本和未知版拒絕，不能靠改constant讓已編譯消費者自動更新；`readonly`並非深層不可變或自動版本管理。對合成觀測資料先核固定型別、值域及完整性，0和null分離，研究門檻、同意及品質旗標在同版決策；false/null/true需明確分支，不得把unknown != false當作已同意。`&&/||`可能短路，`&/|`仍會評估右側，避免驗證／授權函式藏在運算子副作用中；有混合條件加括號固定優先序。真規則與歷史重算需研究者核准，不能照抄自選合成版v1/v2。原生與完整限制見原訓練覆盤；新C# exact a946d1a2d56732a93ad36b6205527646b5178870 / final CI44851069296 581/581。原HackMD 5.1.7–9正文UNREAD/L0，非真研究或正式產品驗收。

### TD-004｜C#有界迭代及方法輸出契約（TD004-CSHARP-BOUNDED-METHODS-01）
研究資料的循環批次要先固定可信輸入字典、筆數/步數、缺失/真0、識別碼重複與STOP終止語意；在讀取下一筆前檢查budget，拒絕時不得回傳看似合法的部分合計。foreach/break/continue/while/do和yield finally需核實不同控制流與真正dispose；若後續資料不驗，必明示只在核准的終止契約下成立。以ReadOnlySpan<T>/純函式分離讀取與回寫，ref/out及可變陣列別名的副作用須顯式且失敗輸出具封閉語意；迭代器throw先暫存，全部完成才commit結果。原生CI44852671230 verified 582/582（code57fca56836186dbb317e987dc53bf1964d70bc97），但JSON先完整parse、研究規則/正式交易/真資源不在實驗範圍，教材5.1.10/11原HackMD UNREAD/L0；見原覆盤，非完整教材或真研究驗收。

### TD-004｜C# Array/List與研究批次雙重真值（TD004-CSHARP-ARRAY-LIST-BATCH-01）
Array.Length固定且Array.Resize替換陣列參考，不會改外部alias；Array.Copy/Clone、new List<T>(array)對class元素只複製參考，真快照須按契約逐層複製/證明不變性。List<T>.Count是有效筆數、Capacity只是目前內部存儲量，不能當業務上限；用獨立maxRows守容量，Add/RemoveAt後查移位及空槽。動態研究batch以全部study/person/wave/attempt或正式核准scope作唯一鍵，合法同分重測不去掉、0≠null；逐項shape/type/range/重複欄、超額、remove不存在時拒絕並禁止輸出部分成品。排序須完整複合tie-break，沒有指明時不可憑List.Sort的穩定性推導固定行序。原生QA40固定＋216獨立Python逐筆oracle、code8c65053aee025b96dcdafc29b80d5fef4cfe362a/CI44854742746 583/583 PASS；本例僅合成in-memory staging，不保證DB ACID或JSON parse前資源界限，原HackMD 5.2.3–4仍UNREAD/L0。詳原覆盤，不可直接套用為真研究規範。

### TD-004｜OOP property不變量與研究資料防禦性快照（TD004-CSHARP-OOP-PROPERTY-SNAPSHOT-01）
封裝不能只靠把setter設為private，若private array透過getter/readonly field或巢狀MutableMeta外洩，外部仍能竄改；constructor與公開屬性getter均需按資料所有權契約deep-copy巢狀集合，尤其是caller後續修改來源/已返回快照。先固定完整constructor/property invariants（null/真0/集合長度/值域/欄位重複），任何batch actions先在deep staged copy驗所有操作，再一次更新資料與revision/封存旗標，error不能發布部分狀態；記憶體rollback不等於資料庫交易或外部事件撤銷。原生驗收code605671ec557303d6b06282e3499e54fa1cfd7f83 +diagnostic-only ba7a418d98df635f0e4264b12cddecd2d0b707a5；CI44856735136 585/585，39固定/512 QA獨立Python逐欄oracle/3compiler負例；第一次Chrome red是獨立環境事件、根因未明。原HackMD 5.3.1–3不可讀L0，不把新合成Stage/Score/Tags當正式研究規則。詳原訓練主檔/覆盤。

### TD-004｜C# Enum與Inheritance狀態型別安全（TD004-CSHARP-ENUM-INHERITANCE-01）
枚舉顯式wire值也可被強制轉成未定義值：要在byte/int底層型別縮窄**之前**檢查原始數值合法範圍，再做Enum.IsDefined，特別是0/default、gap及257→1截斷。不要把enum轉型當研究狀態授權或自動補未知值。對同一研究事件型別階層，把主體、序號、From/To和允許轉換保留在**非虛擬基底類別共同入口**，受控sealed衍生類別只處理自己的payload，未知kind與未核准轉換fail-closed。處理多步事件應先stage後publish，拒絕不得輸出部分狀態/trace；此不保證DB ACID、並發或對惡意擴充程式碼安全。原生CI44858480306 586/586（code08ea0e9aab8d6b280327179f4fd5846a1000189b），首RED CI44858000999為QA將真CS0266誤設CS0029，已依真compiler最小修正。QA42固定+512獨立oracle/3真編譯器負例；原HackMD5.3.4–5仍UNREAD/L0，合成state/QA token非正式研究規範；詳原review。

### TD-004｜事件訂退與回呼副作用隔離（TD004-CSHARP-EVENT-ACCESS-01）
真C#event只開放外部+=/減=，raise保留publisher；保留同一delegate身分才能確實unsubscribe。多訂閱者同步回呼若用GetInvocationList snapshot，回呼內新增/移除的訂閱要區分本次已快照與下次生效；同publisher同步重入以顯式_guard拒絕，但不可當多執行緒鎖。逐handler捕已預期異常可繼續其他handlers，throw前與其他handler的side effects仍存在，絕非資料庫交易rollback、真網路exactly-once或任意Exception皆可安全吞。外部跨類別private/protected不可直接讀，internal同assembly可用，access modifier不是反射安全沙箱。原合成專用native code exacta127155b1da830cd2fc5a88ac95e804299dfa34c，CI44862320136 587/587（固定43+Python獨立512+真compiler負例3），首RED CI44862277353因一筆非法self target測試資料已最小修復；原教材5.3.6–7仍UNREAD/L0，詳原review。

### TD-004｜Constructor失敗隔離與確定性檔案資源所有權（TD004-CSHARP-CONSTRUCTOR-DISPOSAL-01）
Constructor內取得多個IDisposable資源時，任何中途throw都要由constructor自己try/catch清理已取得的部分資源，外部的using無法接住未成功交付的owner。把兩個FileStream真正保留在唯一ResearchTempOwner並讓Dispose idempotent，清理時即使一個child關閉後拋IOException仍要嘗試所有child；using和manual try/finally均需有確定性關閉證據。以FileOptions.DeleteOnClose/真目錄剩餘檔及逐項ownership數量驗收，fail不代表DB rollback或真OS I/O故障。Finalizer非同步且執行時機不可預期，託管檔案交由IDisposable及SafeHandle而不是以GC.Collect/WaitForPendingFinalizers作清理策略；僅在合成probe測class ~Finalizer語法/Reflect與GC.SuppressFinalize路徑。新原生code84e5aaadfcf48517bda633ade0fc01fcf7a5bdaf CI44878317123 588/588/28 steps，39固定+576獨立oracle+3真正編譯器負例，無第三方NuGet。原5.3.8–9教材仍UNREAD/L0，詳原review。

### C# 多載與跨檔宣告（TD004-CSHARP-OVERLOAD-PARTIAL-01）

遇到可空輸入和數值擴寬，先列出實際呼叫端的靜態型別、允許的轉換與該走的處理方法。需要不同業務語意時可採明確命名的方法。原生正測逐個查路由與輸出，負測檢查模糊 null、缺少允許的數值轉換、跨檔可見度不一致與遺漏 partial。每次只變更一個條件，檢查編譯器診斷，還原後重建及重跑正例。部分宣告應在同一編譯中核對，並以實際呼叫證明跨檔私有成員與方法契約成立。
