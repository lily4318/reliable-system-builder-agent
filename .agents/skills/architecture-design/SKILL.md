---
name: architecture-design
description: "設計架構、比較方案。architect 角色；交付 architecture。"
---
# architecture-design｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：specification。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
從需求 ID 推導元件、資料模型與狀態機、API、權限及故障處理。比較至少兩種合理技術方案及成本維護取捨（只有一種可行時說明）。提出具體圖表、介面、ADR 與驗收，不假定未授權外部服務。

### 技術探索（B003 實測方法）
先從原規格分離明確需求、推導、未決產品政策與授權；不以原型內部錯誤碼冒充已核准產品行為。比較最少兩種合理方案，先查適用現有程式、案例與必要官方技術文件；以最小可執行 PoC 對照契約及不同方法的結果，記錄複雜度、限制、實際測試與選用理由。B003 例：半開整數區間線性掃描與排序掃描，再以小範圍離散分鐘集合交集做對照；核實端點、包含、非法輸入。需要決策的後續 UI 工作使用 task-planning 的未決 gate，不阻斷已明確且隔離的原型工作。

### 需求與設計之間的來源契約（NATIVE-REQ-004）
從已確認的需求 ID、版本與原文推導每個元件、介面及資料流；不能因有架構章節、欄位或測試數量就放行。檢查被拒絕功能不再透過其他元件或資料流引入；未決的通知、隱私、整合與上線條件保持待核，必要依賴缺失則阻擋相應施工。

比較以單一正規來源＋版本化引用避免副本漂移，與保留既有 schema 的明示來源副本＋逐值驗證兩種方案：前者可降低長期重複維護但涉及消費端與遷移；後者相容舊介面但須列明映射並防止錯配。依目標系統、相依、改動範圍與回退成本選擇，不獨斷技術棧。原網站草稿 schema 1 採後者，`src.website_scenario_eval` 核對明示來源副本、需求 ID／狀態及審閱項的一對一映射；不把逐字相等套用到所有設計推導，也不將結構契約通過當成架構語意、安全或正式授權已驗收。需要變更 schema 或確認的方案另作 ADR 與受影響模組驗收。

### 持續累積資料的架構取捨（NATIVE-ARCH-005）
- 先區分目前狀態查詢與完整歷史稽核的契約。盤點資料量、查詢頻率、每列內容尺寸、版本鍵、輸出順序、依賴和交易邊界；不要為取最新版將整份歷史載入應用程式，也不要用刪除歷史來換效能。
- 以原程式與原 schema 的隔離資料重現，固定相同輸出，量測資料列物化數、Python 記憶體、時間及資料庫 query plan；以可確定的列數／內容／順序／歷史不變作回歸，延遲僅報實測環境與樣本，不設定不可靠的硬性速度門檻。
- 技術選項至少比較應用層過濾、資料庫集合式查詢及必要索引。先判斷現有資料庫能否安全完成篩選，再評估額外索引、materialized head table 或新儲存系統；後者需要明確資料量與負載證據及資料遷移、寫入放大、鎖定、失敗復原、版本回退設計。不能只按單次 latency 選最複雜的方案。
- 本 repo 原 `src.team_workbench._latest` 採每類 MAX(id)＋MIN(id) 排序與 PK join，在原 schema 上只物化最新版、維持原先類別首次出現的順序，保留原 current_artifacts 依賴判斷及 append-only 歷史。先測原 2,400 列實際 SQLite，再以既有檔案庫唯讀跑新舊查詢、比對輸出與檔案 hash；額外索引只在隔離副本試驗，未採用 schema 遷移。
- 回歸入口 `python -m unittest discover -s tests -p test_team_workbench.py -v`；實際測試與 ADR 取捨見原決策紀錄 NATIVE-ARCH-005。此例不證明所有 SQL、遠端 DB、分散式一致性或完整 Agent 性能；Python peak 不含 SQLite/C 原生配置，原生資料庫仍可能全掃描或建暫存 B-tree。禁止直接拿使用者私人資料庫做未授權 benchmark 或建立索引。

### 受限快照的欄位物化與排序（NATIVE-EP-011-SNAPSHOT-FIELD-BOUND）
讀取資料時同時列出列數、單欄 encoded bytes/type、應用程式與資料庫各自的資源界線。僅做 fetchall 後驗證或 streaming 仍可能先物化巨大非法欄；比較 SQL 型別/長度投影、應用過濾及索引/排序，禁止 filter/drop/truncate 非法列使報表看似成功。使用明確無效 sentinel，原完整語意驗證及交易/row cap 保留。文字 byte cap 要考慮 UTF-16、NUL 和原合法域。實測跨 DB→Python 欄位大小、正反輸出 hash/排序/編碼/快照契約；比較 EXPLAIN 避免新投影 alias 造成索引失效或額外排序。原 EP-05/08、CI 43704992532 six red / 43705180025 418 green；同本地可信固定 schema，不代表 SQLite native cost、全程序記憶體、任意資料庫或 SLA 保證。維持原排序鍵留在 DB，不將巨型原值傳回 Python。

### 跨角色輸入契約與依序守門（NATIVE-ARCH-006）
- 先區分資料形狀驗證、業務狀態機、守門優先序及實際授權。逐欄檢查實際使用的型別、允許值、缺欄預設與相依；不能把 JSON 可解析、列表存在或 truthy 當成有效證據。不合法輸入產生契約規定的 HOLD，而不是未捕捉例外或自動修正成核准。
- 比較局部驗證、集中依序驗證與集中全量預檢。原有逐步收集證據或唯讀任務可能不要求後段欄位；全量預檢可能遮蔽目標、來源與 UNKNOWN/PARTIAL 寫入的優先處置。集中化若有真實重複維護成本，須保留守門順序、缺欄語意、狀態碼與消費端相容性，再估計遷移與回退成本；不要僅因程式較整齊而全面重構或引入套件。
- 本 repo `src.engineering_workflow.route` 先核目標、來源、寫入結果，才驗 stage；在集合查詢前檢查字串。回歸須覆蓋 JSON 陣列／物件／null／數字／布林、合法階段、多個同時錯誤時的優先順序、最小唯讀輸入及既有案例。保留所有輸出 mutation_permitted=false；此判定器只產生建議，不驗證外部證據或執行操作。
- 回歸入口 `python -m unittest discover -s tests -p test_engineering_workflow.py -v`；原型比較與 red/green 證據見決策紀錄 NATIVE-ARCH-006。局部修補僅針對已觀測 JSON stage 錯誤，不等同通用 schema 驗證、惡意 Python 物件防禦、資料來源真實性或其他判定器的安全證明。原 write_outcome 缺欄預設維持不變，若要改成強制明示須盤點呼叫端及另行決策。

### 多平台免費選型（TP-006 / NATIVE-CLOUD-016-STACK-SELECTION）
依 confirmed requirement ID 提取 [多平台選型及實戰指南](../../../docs/CLOUD_ARCHITECTURE_SELECTION.md) 的 typed profile；用 src.cloud_architecture_selection 離線比對 Pages、GAS/Sheets、Workers/D1、Supabase+前端（可選混合架構），未知明示 null；先排硬限制與資料治理，再比較用量、帳號、維護與部署途徑。保留來源日期、估算範圍、理由與替代；preferred 不代表授權、真實費用或適配驗收。既有架構不符需 ADR/使用者確認，不盲目遷移。

### PostgreSQL 與 Supabase 資料庫架構（TD004-OFFICIAL-02 / EP-13）
先以資料所有權矩陣及操作權限界定 exposed schema、GRANT/RLS、UPDATE 新舊 row、column privilege、view invoker、function ACL、管理員 bypass；不將 UI filter/登入當授權。交易須列共享 invariant、lock scope、owner/token namespace、衝突與未知結果；用真正非 owner 角色及兩獨立連線驗正負例、持久化與 rollback。Migration 按舊資料/相容 client/constraint validate/lock/版本回退設 gate，不把一次 DDL 成功當上線相容。Supabase 新表 Data API opt-in 公告及實際 grants/settings、JWT/auth.uid()、RPC/Storage、service key 邊界另驗；原生 PostgreSQL session_user lab 非 Supabase Auth 或正式部署。實作與驗收見 [原生 PostgreSQL 覆盤](../../../docs/training/reviews/2026-11-15-postgres-architecture.md)。

- 進階 migration / 同 token 競寫（NATIVE-PG-023）：先列 RLS/ACL/constraint/view/function/資料全快照，真實阻擋 DDL、晚期衝突、失敗後檢查與合法修正才續作；lock_timeout 非整體期限。舊長連線明示投影與 wildcard prepared 0A000 分開，不承諾所有舊客戶端相容。以 pg_blocking_pids 真實競寫和 SQLSTATE 檢查不同 isolation；新 denial receipt 也是決策狀態變更，若不更新協調 row version，RR 可能得到 23505 而非預期 40001。原 v3 採同 transaction no-op logical update；保留 replay/owner ACL，評估 MVCC/WAL/trigger 成本。只在確定 abort 後重跑整筆交易；unknown commit 不盲重送。以 append-only migration 保留原已驗版並測帶歷史 receipts 之升版，不混同正式遠端資料遷移。見 EP-13 / 原覆盤。

- 共享名額與生命週期（NATIVE-PG-024 / EP-13）：先定共享 invariant 與鎖順序（pool before ledger/booking）、actor/token 的 operation/target/qty binding、拒絕決策持久化、取消 transition exactly-once；歷史 receipt 不等於當前狀態，恢復名額不重判舊 token。避免直接 client stock DML；若採 SECURITY DEFINER 需專屬 NOLOGIN 非 owner/非 BYPASSRLS、可信登入身分而非 caller owner、固定安全 search_path、全限定 schema、同 transaction 撤 PUBLIC/grant、own-row policy；自主共享查詢可見性列入資料責任，Supabase JWT 另驗。測試真 lock wait、不同 actor/相同 token、取消競寫、回復、歷史 migration 及舊明示 projection，核 pool+active booking 守恆與 ledger/version；單資源成功不代表多資源死鎖、零停機或正式資安。參見原 PG 覆盤及實際 CI。

### 研究專案成員權限與服務層隔離（TD-005 必要專家訓練）
比較全域角色與「可信 session→actor→當前 study membership→operation」的授權；研究專案撤權後既有 session 不得沿用舊 membership。讀取、單筆更新及全部匯出均需 scope；study/id 複合鍵、參數化查詢、在同一交易查權限與副作用，拒絕須比較原資料、業務事件及適用 DB 快照，不只比較錯誤回應。區分安全稽核事件的合法契約與越權業務寫入。先用跨專案同 ID、撤權、讀者寫入、匯出、正常 operation 的獨立負正例；RLS 可作防縱深而非取代 API 層。參見 [受控研究 scope lab](../../../docs/training/reviews/test_research_scope.py) 及原訓練決策。本例合成 SQLite 本機證據，非真 Auth/JWT、同時撤權競寫、production 或完整資安驗收，不為無登入的靜態 APP 新增功能。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 architecture；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。

### 線上心理實驗時序與 trial 契約（TD-005）
研究者核准 stimulus/timing window、有效性與中斷政策後，分離 wall clock、同一 context 單調時鐘、DOM write、frame proxy、input event timestamp、handler delay、terminal status；禁止跨 reload/time origin 直接相減。先比較成熟框架（jsPsych/PsychoJS 等）和必要自寫方案、平台/裝置及方法風險；rAF 或高解析 API 不等於實際物理 onset。保留 trial/attempt 版本、原始狀態、null/原因與適用校準需求，不能自動剔除或重試真研究資料。詳 docs/training/reviews/2026-11-16-experiment-timing.md；合成 lab 非科學精度驗證。

### GAS/Sheets 交易邊界與未知在途請求（GAS-DATA-003）
單 workbook atomic batch 非 SQL 隔離；列全 writer（同 script/trigger/admin/其他 script/人工 API），ScriptLock 只合作同 script；若無法約束 writers 或要求真唯一/FK/高可靠隔離，提出 DB 選型，不自動遷移。以可信身份+study/operation/target/token/payload 契約，持久 receipt/audit/outbox 與業務同 batch。未知 commit 可能在鎖釋放後仍未確定，先確認 durable intent，整個受影響 invariant HOLD，absence 不證 abort；intent 寫入本身未知也停，不能 TTL 解鎖。保守模型假設不是 provider CAS/保證；需真可驗 durable fencing 或安全替代。詳 [覆盤](../../../docs/training/reviews/2026-11-16-gas-data-integrity.md)。

### Trial 跨文件持久化及重試契約（TRIAL-RECOVERY-004）
研究者核准後區分 logical trial 與 attempt ID，持久 pending 再呈現刺激，reload 先讀狀態而非跨 timeOrigin 續算；原 attempt 保留 interrupted/null，明示重試生成 parent 關聯與新 doc/time origin。版本、當前 attempt、原點與 receipt 同步守門；真研究缺失/重試政策、資料耐久/倫理獨立核。IndexedDB 與 server storage 權責分開，不把 unload/best effort 或 SQLite 交易冒充 GAS 遠端承諾；詳 [覆盤](../../../docs/training/reviews/trial-recovery-004.md)。


### TD-004｜資料身份、型別與跨庫映射（TD004-DB-KEYTYPE-01）
辨認業務鍵、local surrogate、跨來源 stable identity 與授權是不同契約；依穩定度、分布、查詢與整合選自然鍵/整數/原生UUID或混合，另保業務唯一約束。跨庫匯入以可追溯來源鍵→目的鍵映射、交易及固定預期父子語意驗收，FK 合法不代表資料對。欄位以核定資料字典的單位、語意、值域、精度、時區選型（非數字識別碼保留 leading zeros；精確定點用途適用原生decimal或有範圍的縮放整數）。實際查詢用起點包含/終點排除，時區及精度以實際契約驗；SQL Server rowversion/timestamp 非日期時間，datetime2 表示精度非物理測量準確度。原教材 SQL Server 特定建議不得泛化；用原有命名與 schema，不為風格重命名。參見[原實證](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)與既有 test_research_data.py 新 class，SQLite 局部證據，非 T-SQL 實機/UUID效能/完整教材或正式研究。


### TD-004｜正規化、依賴保留與歷史事實（TD004-DB-NORMAL-01）
先從業務規格列候選鍵、功能依賴、關聯基數及資料生命週期，核1NF/2NF/3NF/BCNF而非只算拆表數；無損接合及依賴保留分別核。BCNF可能失去原唯一性規則；若不能可靠強制，保留適當3NF或設計可交易驗證之約束。區分現行主檔值與交易當時值/研究版本，事件金額、原規格與研究測量不能因當前主檔變更而被重算；以來源/版本外鍵與必要不可變權限契約保留。NO ACTION為保守起點，CASCADE限明確可同生命週期處理的資料，SET NULL/DEFAULT須合語意、合法父鍵與留存政策；外鍵不等於授權。反正規化前核實負載/索引/延遲/重建與對帳。原SQLite三方法見[覆盤](../../../docs/training/reviews/2026-11-17-capability-evidence-and-postdelivery-learning.md)，非正式研究刪除政策、全部引擎或效能實證。
