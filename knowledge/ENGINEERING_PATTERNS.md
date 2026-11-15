# 共用工程知識｜依任務選用索引（TD-001 候選）

本檔整併原「預約及名額一致性」「不明寫入復原」「需求修訂後的交接」與後續已實測經驗，屬通用工程參考，**不是其他專案的正式規格、核准或發布規則**。唯一訓練進度主檔仍為 [AGENT_CAPABILITY_TRAINING.md](../docs/AGENT_CAPABILITY_TRAINING.md)，決策依 [DECISION_LOG.md](../docs/training/DECISION_LOG.md)；原案例及所有歷史證據保留，不在本索引重複保存完整測試日誌。

## 如何按任務選用

1. 先讀目標專案正式來源、最新決策及權限，從 [skill catalog](../config/skill-catalog.json) 選真正需要的角色及技能。按下表的任務/風險挑 1–3 個最相關知識 ID，不因關鍵字出現就假定適用。
2. 閱讀相應知識卡的適用條件、禁止推論、原技能與原實測證據；有疑義或缺正式前置依賴時停止相應操作。若選到同一知識 ID 的多個案例，只載入需要的證據，不把案例數當獨立成效。
3. REPO_NATIVE / READ_ONLY 可直接閱讀本檔與原始證據（SOURCE_READ）；PRIVATE_WORKBENCH 依原 `context/cite/feedback` 流程，私人退休、未解衝突、前置及權限守門仍有效。不可用本公共索引復活私人退休案例或跳過工作區依賴。
4. 在原任務紀錄記錄知識 ID、來源案例 ID、適用或不適用的理由、實際採用步驟、目標 source SHA、產物及驗收/限制。新失敗先記 candidate，必要時增量修正原知識卡並保留歷史；不另外複製同義知識庫。
5. 區分兩個狀態軸：`EVIDENCE_VERIFIED` 指已記錄程式、合成工程實測、CI 或受控瀏覽器/CLI 證據；`INDEX_CANDIDATE` 指已整理供按需參考，尚未經獨立人審為正式共用種子。現有 DEFAULT / OPT_IN 案例只表示原程式可檢索範圍，**不是正式 Release 或私人記憶核准**。本輪不改 Python CASES / TRAINING_CASES、私人 DB、檢索演算法及發布門檻。索引筆記可以 SOURCE_READ 查閱，不能冒稱 public-context 命中或已匯入 SQLite。

## 任務導航

| 知識 ID | 觸發情境／中英風險詞 | 優先技能（catalog ID） | 來源重點 |
|---|---|---|---|
| EP-01 | 需求衝突、否定、草稿、traceability、source mirror | project-intake, requirements-spec, architecture-design | NATIVE-REQ-004 |
| EP-02 | 改選、確認、核准、editable confirmation、stale approval | requirements-spec, debug-and-repair, test-and-acceptance | NATIVE-TRANSFER-002 / NATIVE-UI-003 / P22-CASE-001 |
| EP-03 | 名額、庫存、重複提交、idempotency、actor/token、unknown POST、missing DB | architecture-design, implement-feature, deployment, security-review | B001/B002、P21-CASE-003 |
| EP-04 | 需求或任務改版、舊 DONE、DAG、revision、artifact、topology、worker | task-planning, resume-project, implement-feature, test-and-acceptance | TASK-CASE-001、P21-CASE-005、NATIVE-TOPOLOGY-006、P22-CASE-004 |
| EP-05 | CSV、批次匯入、報表、ZIP、snapshot、hash、exclusive publication | architecture-design, implement-feature, security-review, deployment | P22-CASE-002/003/004 |
| EP-06 | HTTP 正常但 UI 失敗、Chromium、Origin、角色隔離、migration、rollback | debug-and-repair, test-and-acceptance, security-review, deployment | P21-CASE-006 |
| EP-07 | 排程/區間、產品政策未決、PoC、oracle、gate | architecture-design, task-planning, test-and-acceptance | B003-CASE-001 |
| EP-08 | 歷史增長、查詢慢、SQLite latest head、memory、index | architecture-design, debug-and-repair | NATIVE-ARCH-005 |
| EP-09 | JSON 型別錯誤、跨角色交接、ordered guard、HOLD、gate priority | architecture-design, security-review, debug-and-repair | NATIVE-ARCH-006 |
| EP-10 | 沒有本機工作台、GitHub 原生環境、public-context、private isolation、蒸餾 | resume-project, learn-from-feedback, knowledge-distillation | NATIVE-AUDIT-001 / NATIVE-CASE-001 |
| EP-11 | 候選程式 QA 退件、model READY、functional oracle、bounded AST、repair budget | implement-feature, test-and-acceptance, task-planning, knowledge-distillation | P1-2c / P1-2 bounded functional gate |

## 知識卡（已觀測原理與適用邊界）

### EP-01 需求來源一致性，而非形式齊全
- 採用：明示需求含否定與未決，與推導、整理副本、已確認決策分離；穩定 ID/版本、逐值校驗定義為直接鏡像的欄位、審閱項一對一追溯，缺失/重複/錯配不能放行。比較單一來源引用與保持舊 schema 的明示鏡像；保留消費端/遷移取捨。
- 證據：NATIVE-REQ-004，red [35b7f83](https://github.com/lily4318/reliable-system-builder-agent/commit/35b7f837221d7340d467d8a2f27e2d611f27ce50) / [CI 43693171112](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43693171112) 11 subtest failures；green [52e9d48](https://github.com/lily4318/reliable-system-builder-agent/commit/52e9d485a199c1c0481f1c0851e8f1d4c4bad08a) / [CI 43693293456](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43693293456)，395/395，3 新方法及 11 負例。原 [website_scenario_eval](../src/website_scenario_eval.py)、[tests](../tests/test_website_scenario_eval.py)、requirements-spec / architecture-design 的專節；決策紀錄 NATIVE-REQ-004。
- 限制：固定公開 schema 的結構一致性，不證明任意語意推導、架構正確、真人確認或正式研究/部署授權。真正摘要不要求逐字相同。
- 狀態：EVIDENCE_VERIFIED / INDEX_CANDIDATE；已有技能專節，尚未入程式檢索案例。

### EP-02 確認、核准與特定內容版本綁定
- 採用：literal boolean True 才能表示操作者確認；選擇、編輯、取消及空白草稿使舊確認和預覽失效，重新確認獨立於實際送出。文件版本核准亦不繼承到新內容；版本、actor、實際授權各自檢查。UI 依 EP-06 驗真 DOM，持久狀態依 EP-03/04 守門。
- 證據：NATIVE-TRANSFER-002 的 `test_human_confirmation.py` 核心兩方法現仍通過；NATIVE-UI-003 真 DOM 固定檢查 9/12→12/12（另一組 10/13→13/13 重疊不加總），[CI 43692897287](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43692897287) exact 2563e54ad5779042e575bae94b9fd7d84f2c5fd1，最新整合 [CI 43702633084](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43702633084) 核心及 DOM 再驗。P22-CASE-001 [CI 43666793523](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43666793523)，exact 36c03547b84a43c5c41c9aa93388c31839f56041，同 10 項 oracle 受控前後 6→10，原 `test_p22_document_review.py`。詳主檔及兩 NATIVE 決策。
- 限制：literal True 不證明人類身分、操作真實性；合成文件 actor 不是登入認證；受控 DOM 不等於真人 UAT、送件、對外發布或 Agent 增益。
- 狀態：EVIDENCE_VERIFIED / INDEX_CANDIDATE；核心與 UI 已入 debug-and-repair / test-and-acceptance，P22-CASE-001 仍主檔候選。

### EP-03 資源交易、冪等決定及未知寫入復原
- 採用：多人名額/庫存需狀態、唯一鍵、容量與 ledger 同交易，不能先讀後無鎖寫；區分 exclusive create、mode=ro 與 mode=rw，query_only 不足以避免缺庫被建立。actor/token 必須綁定 payload，成功與合法否定結果均持久化；同請求重播回原決定，不明結果先查狀態/憑據，不盲重送。遠端依專用 `recovery_reconciler` 與實際來源、交易能力另驗。
- 證據：原 [workbench_learning.py](../src/workbench_learning.py) DEFAULT B001-CASE-001、B002-CASE-001；OPT_IN P21-CASE-003（原 CI 43576453447）；主檔 P22-CASE-001 的失敗 stale_approval/denied_replay/future_revision_replay/fault_atomic 經同 oracle 修復；原 tests/test_b001_workshop.py、tests/test_b002_equipment.py、tests/test_p22_document_review.py。
- 限制：本地 SQLite 交易證據不移植為跨庫、分散式、HTTP POST exactly-once、外部 API 或正式容量/權限核准；COMMITTED 不等於業務成功。真實遠端不明狀態維持唯讀核對。
- 狀態：EVIDENCE_VERIFIED / 原 DEFAULT 2、OPT_IN 1；P22-CASE-001 作交叉證據而非複製案例。

### EP-04 版本失效、跨階段驗收與安全拓撲
- 採用：確認來源後以 revision、唯一 session、artifact ID、前置 ID 與交易核對；根需求及任務/事件同交易，綁定 stage PASS 才寫新產物，受影響 DONE 與下游回待驗，獨立支線保持。舊 RUNNING 需對帳和 recover，不能復用舊 session。新增圖節點/邊採完整任務與 artifact head snapshot CAS、唯一 producer、catalog 祖先、DAG/gate 驗證；拒絕受影響活躍 worker；未知結果查 receipt。舊歷史不刪，外部檔案按 EP-05 另查。
- 證據：TASK-CASE-001（原 task revision/session 負例）、P21-CASE-005 [CI 43606395473](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43606395473)；bound PASS exact 0f4f536d4c3daf05304add614d24e2563b42b1ef / [CI 43607088233](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43607088233) 351/351，七綁定及九修訂測試；NATIVE-TOPOLOGY-006 exact f060bb5db658d53b7b7a8d40a8d5425ed37c7ac0 / [CI 43702359542](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43702359542) 406/406，7 拓撲測試含實際子程序中斷及競寫；P22-CASE-004 跨檔案 generation；原 workbench_tasks.py、tests/test_bound_artifacts.py、tests/test_task_revision.py、tests/test_workbench_revision_sync.py、tests/test_topology_extension.py。操作詳 [TEAM_WORKBENCH](../docs/TEAM_WORKBENCH.md) 及 task-planning/resume-project。
- 限制：同庫、可信新版 API、明確 opt-in 綁定；拓撲只加節點/邊，非任意刪邊或重綁，不監聽外部規格、停止 OS worker、撤銷外部操作或證明語意。舊 API/直接 SQL 不能假定受新版守門；非綁定模式不可冒稱完全聯動。
- 實際遷移 NATIVE-EP-009-RECOVERY-FENCE：舊 worker 的復原保護不能僅依變更後的圖。原 revise 改邊可使 RECOVERY_REQUIRED worker 的舊祖先提早 ready；red [CI 43703424124](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43703424124) 3 failures，實際 spec blockers=[]；green [CI 43703631052](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43703631052) 412/412，四新方法。真正依賴集合變更且 affected RUNNING/RECOVERY_REQUIRED 時，於現有 transaction 完成圖檢查後、所有寫入前拒絕；保留內容修訂、獨立工及 recover 後合法改邊。EP-03/09 為共同原理，不另建卡。不能修復已發生的歷史 fence、終止 OS worker 或處理任意重綁；舊庫另行對帳。
- 狀態：EVIDENCE_VERIFIED / OPT_IN P21-CASE-005、P22-CASE-004；TASK-CASE-001、NATIVE-TOPOLOGY-006 及綁定負測為索引候選延伸；不重複建立三份同義交易規則。

### EP-05 輸入快照、成品與獨占發布
- 採用：先驗證所有列；固定來源 bytes 或一致 read-only snapshot、policy revision、canonical output/hash；排他建立新路徑不覆寫，未知結果唯讀核對實際 bytes 與同版 manifest。資料庫驗收與實體檔案發布分開；舊生成成品可留歷史，但不能提交為新版本 PASS。新來源或政策變更須生成、再驗。
- 證據：原 OPT_IN P22-CASE-002 [CI 43667714699](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43667714699)、P22-CASE-003 [CI 43668235893](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43668235893)、P22-CASE-004 [CI 43668854174](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43668854174)；各自 exact source 見原 TRAINING_CASES 與主檔；最新 [CI 43702633084](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43702633084) 原始日誌回讀 `test_p22_file_intake`、`test_p22_snapshot_report`、`test_p22_report_workflow` 正反例。復用 EP-04 任務版本，不複製其 DAG 規則。
- 限制：可信本地檔案系統、合作來源、合成資料；snapshot 不證明發布時 live-source CAS，無 Windows/斷電/惡意路徑/分散式保證。缺原快照不等於 NOT_OBSERVED；聚合不證明匿名。
- 實際遷移 NATIVE-EP-011-SNAPSHOT-FIELD-BOUND（與 EP-08 共用證據）：資料列 cap 不等於單欄大小 cap。SQLite snapshot 原在 Python fetchall 後拒絕巨型非法 TEXT/BLOB；red [CI 43704992532](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43704992532) 六失敗。以 SQL typeof/編碼 byte bound 回 NULL sentinel（不 filter/drop/truncate），原語意驗證、snapshot/order/hash 及排他發布不變；final [CI 43705180025](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43705180025) 418/418，最大回 Python field 在反例由262144/262153變0/8，1000筆多編碼 exact ZIP 相同，1001拒絕，WAL 原契約保留。16 bytes 是原八字元 ASCII schema / UTF-16 相容上限，不適用任意文字；不限制 SQLite native sort/scan 或總 RSS，不等於 live-source CAS。
- 狀態：EVIDENCE_VERIFIED / 原 OPT_IN 3；不新增程式案例。

### EP-06 實際瀏覽器、權限及遷移驗收分層
- 採用：HTTP、真 DOM、真人 UAT、正式部署、資料遷移與復原分開；使用真正 browser form/Origin 行為，不為測試通過放寬 CSRF 或 actor 隔離。遷移先停止舊 writer、保留來源與歷史、核對目標；已有新版寫入不能直接回退舊快照。UI 內容確認採 EP-02。
- 證據：OPT_IN P21-CASE-006 / exact 0f4f536d4c3daf05304add614d24e2563b42b1ef / [CI 43607088233](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43607088233) 351/351，native browser 3 roles、CLI migration 及 strict Origin。最新 406-test CI 仍有 P21-EQUIPMENT-BROWSER PASS、EDITABLE-DECISION-BROWSER 12/12。原 src/p21_equipment_site.py、src/p21_equipment_browser_test.py、tests/test_p21_equipment_cli.py，主檔 P2-1d。
- 限制：本機合成 Chromium/CLI 非真人驗收、正式服務/資安審計或斷電耐久；不是解除實際權限、安全配置的授權。
- 狀態：EVIDENCE_VERIFIED / 原 OPT_IN 1，已有 QA 技能相關原則。

### EP-07 未決產品政策與可測原型分離
- 採用：明確部分先做最小可測 PoC；比較合理方法與有限域獨立預期值（本例半開整數區間掃描與離散分鐘 oracle）。未決錯誤/UI 政策設 decision gate，真實 answer/source 前不能啟用；保留可獨立驗收分支。接續時重新讀 gate/worker，依 EP-04 不盲接管。
- 證據：B003-CASE-001，主檔 P1-1b 實際 21/21 本機回歸、三 stage 2 DONE、UI PENDING；原 code adddfe3bf8c13cbaf7f0ed1d238bb887da5a21f3 / [CI 43566849542](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43566849542)。最新 406-test CI `test_b003_and_tasks` 十項 ok。原 architecture-design 的技術探索及 task-planning gate，`src/b003_shifts.py`。
- 限制：合成有限整數/分鐘原型，非日期/時區/真人排班 UI；oracle 程式不授權產品政策或自動決策。
- 狀態：EVIDENCE_VERIFIED / INDEX_CANDIDATE；原主檔候選、已有技能專節。

### EP-08 目前狀態查詢與歷史稽核分離
- 採用：先量測相同契約、物化列數、記憶體及 query plan，再比較應用層載入、SQL 集合查詢、必要索引/遷移；保留輸出排序、IDs、依賴與歷史。只需最新 head 不應載入全部舊 payload，也不删歷史換效能。
- 證據：NATIVE-ARCH-005，SQLite 3.46.1 合成 2400 rows/12 kinds，Python 物化 2400→12、五次中位時間 24.787→0.720 ms、Python peak 39356642→200880 bytes；red [CI 43701076849](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43701076849) 301!=3；green exact 54694806bbb70229572b1f49041cffc9c29a7856 / [CI 43701094377](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43701094377) 397/397，原 `test_team_workbench` 兩項新增 ok。原 team_workbench._latest 與 architecture-design 專節，決策紀錄 NATIVE-ARCH-005。
- 限制：實測樣本非 SLA、非整體 Agent latency；Python peak 不含 SQLite native allocator，DB 仍掃歷史與可能 temp B-tree。未新增 index/schema 或測生產資料，禁未授權私人 benchmark。
- 實際遷移 NATIVE-EP-011-SNAPSHOT-FIELD-BOUND（同 EP-05 證據，不重複計數）：Python 物化量須同看列/欄 bytes/type；SQL sentinel projection 先守界、保留所有非法列讓應用拒絕。首版 ORDER BY 投影 alias 實測失去 records_id 索引，增加 TEMP B-TREE；保留內部原排序鍵且只返有界欄位後，SQLite 3.46.1 原/新 EXPLAIN 同 SCAN records USING INDEX records_id，final CI 43705180025 418/418。量測欄位大小及實際 plan，不冒稱 RSS、延遲或所有 query optimizer；不在實際私人 DB 建索引。
- 狀態：EVIDENCE_VERIFIED / INDEX_CANDIDATE；已有 architecture skill，未進程式案例。

### EP-09 跨角色輸入契約及守門順序
- 採用：形狀、型別、業務狀態與實際權限分開，集合檢索前驗 string；不合法回約定 HOLD 而非 exception 或自動核准。多項錯誤時維持目標/來源/unknown 或 partial write 的先後，不讓下游全量預檢掩蓋前面的安全拒絕；保留唯讀都不需後段欄位的相容契約。
- 證據：NATIVE-ARCH-006 red [CI 43702025465](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43702025465) errors=4；green exact a0d2c1cb7d8c16f62c021f334759f023c58f7948 / [CI 43702126591](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43702126591) 399/399；`test_malformed_json_stage_is_advisory_hold_not_exception`、`test_stage_validation_preserves_prior_gates_and_incremental_inputs` ok。原 engineering_workflow.route、architecture-design 專節及原決策。
- 限制：局部 JSON stage 修復，不是通用 schema 驗證或外部真實證據；缺 write_outcome 的原 NONE 預設維持，收緊需盤點 caller。mutation_permitted=false 不變。
- 實際遷移 NATIVE-EP-008：GitHub owner/repo 大小寫是名稱表示而非不同資源。先驗 ASCII 路徑形狀，再作大小寫等價比較，維持原 intent、權限與跨專案守門；不自行接受 URL、空白、rename/transfer 或 redirect。原 scope 判定器 red [CI 43703326898](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43703326898) 9/13 subcases failures；green [CI 43703386263](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43703386263) 13/13 新 subcases、408/408 完整回歸。詳原決策紀錄。此為兩卡共同證據，不另建知識卡或升格 seed。
- 狀態：EVIDENCE_VERIFIED / INDEX_CANDIDATE；已有 architecture skill，未入程式案例。

### EP-10 平台原生工作與知識檢索隔離
- 採用：按工具與授權選 PRIVATE_WORKBENCH、REPO_NATIVE、READ_ONLY；不可為公共檢索初始化私人庫、混合專案、把公開索引當私人記憶。repo-native 讀精確 SHA、原證據與任務適用案例，保存所允許公開的最少結果；沒工具就標記未執行。沿 EP-03 唯讀語意及 EP-04 版本證據原則，不冒稱 GitHub 與 SQLite 同一交易。
- 證據：NATIVE-AUDIT-001 / 候選 NATIVE-CASE-001，exact 7cd8085e6fd9f320fea0e0526cb3b2fd6a354af0 / [CI 43691876099](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43691876099) 390/390，既有 public-context 兩項隔離回歸且最新 CI 再驗；真實 REPO_NATIVE 回讀及後續 NATIVE-TRANSFER/REQ/ARCH 任務引用原決策紀錄。P22-CASE-001 原 [CI 43666793523](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43666793523) 真 SQLite 檢索 marker 3 retrieved/2 applied/1 non-applicable/2 candidate feedback。
- 限制：詞彙比對非語意模型；SOURCE_READ 不是實際 CLI/cite receipt，跨平台私有同步、真正獨立 Agent/盲測與升版均不證明；私人內容未獲授權不入公共 repo。
- 實際遷移 NATIVE-EP-008（交叉引用 EP-09）：REPO_NATIVE 唯讀原 GitHub API 查原名與全大寫別名取得相同 immutable repository id 及 canonical full_name；據此修復原 scope 比較，不靠名稱猜測權限。大小寫等價不保證 rename/transfer 後的同一資源；實際寫入仍核正式 repo id、head、授權及回讀。
- 狀態：EVIDENCE_VERIFIED / INDEX_CANDIDATE；既有兩 DEFAULT、六 OPT_IN 範圍不變。

### EP-11 外部候選結果必須由 host 驗收
- 採用：模型或其他生成者的 REVIEW_READY 只代表候選，不能等同程式功能 PASS。預先定義可重現 oracle、限定輸入及執行範圍，保存精確版本/輸出證據；功能失敗即由 host QA 退件，以既有任務池重開實作及必要下游，保留不受影響前置，設定有限修復次數與未知回應復原。未知 native code 不直接在有憑證或外網的環境執行。
- 證據：P1-2c exact 53f2f44f88d617797cfed8a4ef746c5280e56130 / [CI 43688435072](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43688435072) 385/385；P1-2 bounded functional gate exact d2ca12006988100a500a6a6fea0f41cd73de5f85 / [CI 43688939298](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43688939298) 388/388，最新 406-test CI 六個 DispatchContract / FunctionalGateContract 方法 ok。原 src/p1_dispatch_runner.py、src/p1_restricted_functional.py、tests/test_p1_dispatch_runner.py。
- 限制：fake transport 與有限 AST 的實際語意測試，未跑真模型或任意 Python、未證實獨立多 Agent、通用安全沙箱或真正自動修復能力。本地 runner 為選用評測，不是 TD-001 開工前提。
- 實際遷移 NATIVE-EP-010-ORACLE-BOUNDARY：公開 oracle 必須測到已聲明合法域的必要邊界與資源上限。原12案例最多3筆卻接受32筆，實際可錯放超3000步及數值端點錯誤候選。red [CI 43704461951](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43704461951) 四失敗；green [CI 43704563695](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43704563695) 415/415，oracle v2 18固定案例，安全限制不放寬，host 退件後修復通過。oracles 版本/契約/cases hash 變更後不能借舊 PASS（EP-05 原理）；仍非完整輸入域或獨立模型/人審驗收。
- 狀態：EVIDENCE_VERIFIED（有限契約/本機功能）/ INDEX_CANDIDATE；非可宣稱真模型案例。

## 現有檢索案例對照（唯一程式主本仍為 src/workbench_learning.py）

| 原 case_key | 原檢索狀態 | 本索引主卡 |
|---|---|---|
| B001-CASE-001 | DEFAULT | EP-03 |
| B002-CASE-001 | DEFAULT | EP-03 |
| P21-CASE-003 | OPT_IN | EP-03 |
| P21-CASE-005 | OPT_IN | EP-04 |
| P21-CASE-006 | OPT_IN | EP-06 |
| P22-CASE-002 | OPT_IN | EP-05 |
| P22-CASE-003 | OPT_IN | EP-05 |
| P22-CASE-004 | OPT_IN | EP-04 / EP-05（同一案例，不重複計數） |

原碼 public-context 及已授權私人 context 可以取得以上 8 個案例中的適用範圍；其餘知識卡是文件 SOURCE_READ，不是程式執行查找結果。索引候選只可在目標任務按需閱讀和檢驗，若未來需要加入 runtime seed，先確認人審、去識別化、重疊與歷史退休規則，選擇最小新增或以新版本可追溯替代；不直接增加 CASES 造成既有私人庫種子語意漂移。

## 整併及覆盤維護

本輪按共同原理做 11 張索引卡，並非新增 11 個獨立測驗或 11 個已發布案例。舊三項通用原則分別保留在 EP-03、EP-04，UI 確認/文件核准歸 EP-02，原子修訂/產物綁定/拓撲共用 EP-04，快照與檔案生成共用 EP-05。歷史主檔、決策、CASE key、原始 CI、技能方法不刪改為副本。B003、TASK、P22-CASE-001、NATIVE 系列與有限功能 gate 的較完整內容仍在主檔/決策，索引補足按任務找到它們的入口。

證據定位：原 [訓練主檔](../docs/AGENT_CAPABILITY_TRAINING.md)、[訓練決策](../docs/training/DECISION_LOG.md)；基準 exact 05d123b49860ce0fef772d9cd96dd47d4e79da4d / [CI 43702633084](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43702633084) / job 132776872828，原始日誌 227954 chars，406 tests in 39.910s/OK。索引整理非重新執行以上測試；不加總重疊測試數，不宣稱統計能力增益。

待人審：索引卡的適用性和升格範圍、在下一項不同真實授權任務中的選用效果。發現不適用或衝突時，回原來源核對後記新候選證據及原因；不自動蓋掉使用者偏好、有效案例或正式規格，遵循 [learning-policy](../config/learning-policy.yaml) 與既有 PR/Release 門檻。
