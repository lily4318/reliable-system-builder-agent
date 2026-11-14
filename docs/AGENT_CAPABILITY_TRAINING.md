# Reliable System Builder Agent｜自主開發能力訓練與基準評測（獨立候選）

## 最新訓練主檔｜2026-11-14（持續更新入口）

**使用者決策：** 將本次教材比對與訓練建議持久保存，以後每次要求訓練此 Agent，先讀本節與最新實際進度，再接續施工。此節為目前訓練方向及接續索引；下方保留既有評測協定與歷史，不將建議自動視為正式 Release 或額外授權。

- TASK_DOMAIN: RELIABLE_AGENT_ENGINEERING_CAPABILITY_TRAINING
- SOURCE_REPO: lily4318/reliable-system-builder-agent
- ACTIVE_CANDIDATE: Draft PR #8, candidate-skill-team-integration-20261114；https://github.com/lily4318/reliable-system-builder-agent/pull/8
- SOURCE_VERSION: P1-1c revision-aware task pool source/test commit 19d11e2d5b82e4a66ca87c4b4b9034d1496f6acc; guide/skill commit d8ea3eb3425ae7dcf93e3f3c40551d62579cadce; P2-1a verified baseline df58c6613cafaeddfdfb79a08f1508166ddb0622 CI 43567913525 success. Current PR head is authoritative.
- LAST_VERIFIED_STEP: P1-1b CI 43566849542/43567003958 and P2-1a CI 43567839044/43567913525 completed/success. P1-1c reproduced legacy session reuse failure, local 35/35 PASS (14 new + 21 regressions), actual cross-process contention, atomic cascade rollback and old-version-to-new migration verified; code/test/guide/skills readbacks exact. Full code CI 43568659877 in_progress at readback.
- COMPLETED: 七專家與12項技能、SQLite 私有工作台、P0與P1-1a/b完整 CI；P2-1a 本機設備網站 HTTP/安全驗收與完整 CI（瀏覽器仍阻塞）；P1-1c 原任務池 revision、原子下游失效、DONE重開、禁止同任務session重用、RECOVERY_REQUIRED/復原、DAG修訂、舊庫遷移及14項新增功能負測。
- BLOCKERS: P2-1a Chromium loopback navigation ERR_BLOCKED_BY_ADMINISTRATOR; browser DOM and manual UAT NOT_VERIFIED, no bypass. Real LLM/separate subagents, independent holdout/human reviewers not verified; no user private workspace. 外部部署與正式啟用未授權。
- WRITE_OWNER: 僅 Agent 候選分支；main/Release、外部專案、真實個資、付費模型或正式部署不在本次授權內。
- SYNC_STATUS: P0_P1_1A_B_P2_1A_FULL_CI_PASS; P1_1C_LOCAL_FUNCTIONAL_PASS; SOURCE_TEST_GUIDE_SKILLS_READBACK_VERIFIED; REMOTE_FULL_CI_PENDING; BROWSER_ENV_BLOCKED; REAL_RUNNER_NOT_RUN; NO_RELEASE.
- NEXT_ACTION: 回讀 P1-1c exact-SHA 完整 CI，修復必要回歸；續原 P2-1b 方向：在明確允許的環境實際瀏覽器 DOM 驗收及設備歸還/取消/後台作業、狀態轉移/稽核/權限與交易回退，使用 revision-aware 任務池驗收與跨階段接續。外部部署 gate 保持未決；不動 main、Release、外部專案；P1-2/P2-2 真實 runner 與獨立評測待授權。

### 教材比對與改善方向

參考使用者提供的《AI團隊實戰營_學員包_第一天_11月份(1).zip》第一天的三角色九技能、共用工作空間、品牌手冊、案例卡、靈感/選題、覆盤與學習蒸餾設計。僅記工程適用的概念，不存課程原件、業務素材或個資。七專家與十二技能是工程延伸，不是教材本身的七角色架構。既有工作台有資料儲存與相依檢查，但無實際模型調用；技能指令、公開合成資料及結構化 PASS 不代表自治能力。

| 差異 | 優化建議（待實戰驗證） |
|---|---|
| 角色與技能 | 保留七專家，按任務選擇角色，不強制全員；針對實戰弱點補 references/templates/scripts/examples/tests |
| 主動學習 | 從明確偏好、需求修正、測試失敗、Bug 修復、QA/UAT 退件、有效架構、部署事故形成候選案例；保留證據與適用限制 |
| 技術探索 | 先擴充 architecture-design，必要時增 technical-research；讀官方文件、比較方案、最小 PoC，供開發使用 |
| 記憶檢索 | 延用 SQLite；分使用者、專案、情節/案例、語意/知識、程序/技能；引入任務 ID、相關性/關鍵字、精簡 context；避免跨案混用 |
| 工作任務池 | 持久化需求、改善項目、優先序、依賴與驗收；週期覆盤根據實際成效，不增加無關規則 |
| 蒸餾 | 同 topic 去重不是語意蒸餾；提出可驗證合併與技能改善，保留歷史、經審核後推廣，使用新任務驗證 |
| 實戰評測 | 保留既有結構評分與安全門檻，另量測實際功能、修復、任務完成與遷移；真實多 Agent 需要執行證據 |

### 訓練路線（依驗收而非固定天數）

| 優先序 | 訓練任務 | 驗收 | 狀態 |
|---|---|---|---|
| P0-1 | B001 社區工作坊：需求→規格→架構→DAG→可執行垂直切片→QA；額滿候補、重複報名、需求衝突、未知寫入復原 | 獨立功能正反測、可重現的修復紀錄；公開合成實作與真實 Agent 評測分列 | LOCAL_FUNCTIONAL_PASS / FULL_CI_PASS |
| P0-2 | B001 案例記錄、蒸餾，遷移到 B002 公用設備借用 | 相關案例被實際取用；新任務功能測試，對照有/無經驗和適用限制 | CONTROLLED_TRANSFER_PASS / LOCAL_FUNCTIONAL_PASS / FULL_CI_PASS |
| P1-1 | 主動回饋事件、分層記憶檢索、技能專業深度、技術探索、任務池/覆盤 | 新工作階段重讀、無跨案混用；測試實際檢索與回饋行為 | P1-1a/b FULL_CI_PASS; P1-1c REVISION_RECOVERY_LOCAL_PASS / CI_PENDING |
| P1-2 | 專家獨立協作與交接 | 有授權平台才做真子代理；獨立 QA、交接與整合證據；無平台標單 Agent 分工 | BLOCKED_REAL_RUNNER |
| P2-1 | 隔離合成完整系統：前後端、資料庫、權限、後台、預約、復原 | 可操作成品、端到端功能及安全測試 | P2-1a HTTP_LOCAL_PASS / FULL_CI_PASS; BROWSER_BLOCKED; P2-1b NEXT |
| P2-2 | 未見題獨立前後測、語意蒸餾、必要跨平台同步 | 等模型/工具/資源條件、獨立評審、保留失敗；只有需要且授權才同步 | PROPOSED |

七專家訓練：System Lead 需求與路由/優先排序；Architect 技術比較、資料模型與取捨；Developer 真正實作/除錯；QA/UAT 獨立正反例與瀏覽器；DevOps/SRE CI/CD、部分寫入與復原；Security 最小權限與隱私；Learning Evaluator 記錄、蒸餾、遷移、前後測。

建議獨立實戰評分（尚未核准為正式門檻）：功能25、需求15、除錯15、架構10、自主規劃10、協作10、經驗遷移10、效率5。重大安全/未授權寫入 0 為必要門檻而非可抵銷分數。核心需求覆蓋/核心功能/必要交接目標100%；已有明確偏好不重問；追蹤復發率、修復輪次、成本時間和遷移正確率，先建立真實基準再比較。保留既有正式安全和品質閘。

### 2026-11-14｜P0-1 B001 實際工程訓練紀錄（可供下一輪檢索）

**資料來源：** evaluations/capability/public_tasks.json B001 R1–R4 (blob 0e422d8d36cb1697396dc753fb98304a9b914120)。範圍只限公開合成代號、本機暫存 SQLite；無真人報名、外網、部署或私有資料。當前聊天 Agent 單角色切換開發、QA 與學習分析；未啟動獨立七專家或 repo LLM runner，不是模型權重訓練或獨立評測。

**需求與架構交接（本輪產物）：** R1 最新額滿候補規則優先，R2 同一 applicant 唯一紀錄，R3 未知寫入先唯讀對帳且不自動重送，R4 正反及競寫邊界。SQLite config → capacity-policy + enrollment 唯一約束/依 seq 候補 → request 唯一 token 與結果同交易 → read-only audit。DAG：需求→交易及識別鍵設計→實作→並行及故障測試→缺陷修復→案例記錄。合成設計假設：SYN-* 格式、單工作坊、固定容量，變更需明確遷移；候補依成功提交順序，不含取消、遞補、HTTP/UI、實際 API 或多節點資料庫。相同 token 已知重播回傳原結果；未知結果不得自動呼叫 register；未找到仍須審查。

**實際程式及驗收：**
- src/b001_workshop.py（Git blob 33452b04c431e23bd6ec3eafb1b9d9cdc5242fbf）
- tests/test_b001_workshop.py（Git blob e187b3c71f0672a8cfef57a2b7d32971c6328050）
- 本機命令：python -m unittest discover -s tests -v（隔離暫存目錄僅含此輪兩檔）；初 8/8 PASS；新增缺庫負測後 8 PASS/1 FAIL；修正後 9/9 PASS（0.233 秒）。此為開發者撰寫、實際執行的功能回歸，非獨立人類 QA。
- R1：1 席、8 併行申請→1 ACCEPT / 7 WAITLIST；零容量及無效容量；順序與持久化。
- R2：8 併行同一人→1 ACCEPT / 7 ALREADY；候補重複、token 重播與衝突。
- R3：before_commit 失敗回退；after_commit 回應遺失後唯讀查得 COMMITTED；NOT_FOUND_REVIEW 仍 retry_allowed=false。
- R4：上述正反測與缺庫負測，9 項共通；未測真正 HTTP/遠端故障。
- 兩檔本機 git hash-object 與 GitHub 回讀一致；程式與測試 commit d531eb09798e69003280cc981a20094969d4f381，完整 CI Run 43561619878 查核時 in_progress，不提前宣告成功。

**案例卡 B001-CASE-001｜observed｜SQLite 唯讀復原不應建立檔案**
- 情境：既有 DB 遺失後，執行 reconcile 唯讀查詢。
- 原始錯誤：sqlite3.connect(path) 先建立空檔，即使隨後 PRAGMA query_only=ON；新增 test_readonly_reconcile_missing_database_does_not_create_file 實際 FAIL，assertFalse(self.path.exists()) 得 True。
- 修復：讀取使用 Path.resolve().as_uri()+ "?mode=ro"，uri=True，在連線時禁止建立 DB；保留 query_only 第二層防護。再次測試 9/9 PASS。
- 可遷移知識：在讀取資源前就限制唯讀權限；不要將「讀取操作沒有顯式寫 SQL」視為無副作用。對交易相關狀態及 request ledger 在同一原子交易寫入；以唯一約束及 BEGIN IMMEDIATE 維持單一 SQLite 庫一致性。
- 適用限制：本機 SQLite 案例，不保證其他引擎、遠端 API 或跨機鎖；B002 應重用原理而非盲目複製報名 schema。下一輪優先驗證缺庫唯讀、原子保留/回退、可用量與併發。
- 學習狀態：已保存公開合成案例，未建立使用者私人記憶、未實際執行自動語意蒸餾、未公開宣稱學習遷移成功；B002 尚未實作。此案例依訓練主檔檢索，不冒稱私人 workbench 已執行。

### 2026-11-14｜P0-2 B002 實際工程及案例遷移紀錄

**來源與前置查核：** evaluations/capability/public_tasks.json B002 R1–R4 (blob 0e422d8d36cb1697396dc753fb98304a9b914120)；先讀本檔 B001-CASE-001、B001 實作及測試、architecture-design、implement-feature、test-and-acceptance、knowledge-distillation 技能。B001 程式 commit d531eb09798e69003280cc981a20094969d4f381 CI 43561619878 與文件 commit 0f07a43006857bf915f1ffe70016ab35d899436b CI 43561661130 均 completed/success。main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57 未變。此輪為聊天 Agent 單角色切換實際工程練習，不冒稱獨立子代理/額外模型 runner 或人類盲測。

**需求、方案取捨及交接：** R1 以 stock-reserved 算可用量，R2 整數正量且 SQLite 64-bit 範圍內，R3 並行不超額，R4 失敗/回退可重現。方案比較：先讀取庫存再於另一交易寫入有競爭窗口；單庫 BEGIN IMMEDIATE + 條件式 UPDATE + 唯一 request token 在同交易管理庫存與紀錄，適合此本機合成需求；正式多節點服務需要另行選擇伺服器資料庫或分散式一致性，不假定目前 SQLite 模式能處理跨機網路。元件：availability-service (can_checkout) → reservation-lock (BEGIN IMMEDIATE/guarded UPDATE) → inventory-view (mode=ro) → rollback-log (原子 request ledger；回退後未留部分紀錄)。DAG：需求→設計→取用 B001 案例→實作→正反/並行/故障測試→案例整理。合成假設：單設備庫存池，固定初始庫存及已保留量，SYN-* token 是請求識別而非真人身分，重播相同 token/quantity 回原結果，拒絕結果亦可記錄為已提交請求，但不占庫存；無歸還、取消、多設備種類、日期區間、HTTP/UI 或部署。不是正式產品核准。

**實際遷移與功能驗收：**
- src/b002_equipment.py blob 843a88dd061ab90b165176a5836bfa4bc0f632d5；tests/test_b002_equipment.py blob e714721b4cf40b0fadfd1331022d511a4667897c；兩檔與本機 git hash-object 一致。
- 本機暫存工作目錄 /tmp/b002_training（僅本輪可信合成原始碼與測試），命令 python -m unittest discover -s tests -v，13/13 PASS，0.144 秒；不是完整 repo 測試或獨立人類 QA。B002 兩檔 commit 20c4e85bd6572831ac78a33b56d4344b376b8572，查核時 CI 尚無 run 回傳。後續依實際 PR head 重新查。
- 初始 stock=10, reserved=3, available=7；借 7 成功，追加 1 拒絕；不合法數量（負、零、bool、小數、字串、None、超 64-bit）不得變更資料；8 路不同數量並行，已保留增量不超過 7，ledger 與庫存一致；8 路相同 token 只保留一次 2 件；相同 token 不同數量拒絕。
- 故障注入：after_inventory（更新後、寫 ledger 前）與 before_commit（ledger 後、提交前）均回復 reserved=3，沒有已提交 request；after_commit（回應遺失）唯讀回讀 COMMITTED/RESERVED，資料庫原始位元組一致。NOT_FOUND_REVIEW 不自動重送。
- 直接套用 B001-CASE-001：mode=ro + query_only；進一步讓 reserve 使用 mode=rw（缺庫不自建），create 使用 exclusive xb（拒絕既有資料庫）。缺庫 snapshot/reconcile/reserve 都實際拋出 OperationalError 且不建檔；mode=ro 寫入拒絕。受控 comparator test_reproduce_old_readonly_pattern_then_compare 將連線暫換為舊 sqlite3.connect(path)，實際重現 read-only 路徑意外建檔，再切回修正模式確認不建檔。這是同一測試中的機制比較，不是未看案例的獨立 Agent 或盲態前後測；沒有聲稱 B002 本輪出現未修復失敗或模型整體增分。

**案例卡 B002-CASE-001｜observed｜讀寫與初始化分離，交易中同時保存決定及資源狀態**
- 來源：B001-CASE-001 + B002 13 個本機功能回歸及受控 comparator。
- 萃取：讀取 mode=ro，既有資源修改 mode=rw，初始化獨立且拒絕既有路徑；避免在復原或修改時意外重新建立資源。先將庫存檢查與保留置於同一交易內，使用資源不變量/條件式更新、唯一請求鍵及 ledger，未知結果先查驗不盲目重送。COMMITTED 僅表示請求決定已保存，需檢查 result 區分 RESERVED 與 INSUFFICIENT。
- 證據：test_missing_database_never_created_by_read_or_reserve, test_initialization_is_exclusive, test_read_connection_rejects_mutation, test_reproduce_old_readonly_pattern_then_compare, test_concurrent_variable_quantity, test_concurrent_same_token, 三個 failure/unknown 測試。
- 限制：本機 SQLite/單庫、合成資料、作者測試；故障為刻意注入。初始建立期間若失敗可能留空檔供人工查核，未驗證 process crash/多機/正式遠端服務；拒絕盲目建立或刪除。不取代原 B001 案例，不寫私人工作台或自行發布通用正式知識。
- 學習狀態：經驗已由目前聊天 Agent 在開發前從主檔檢索並於 B002 實作驗證。沒有自動語意檢索、自動蒸餾或真正多 Agent 學習證據；下輪 P1-1 優先將兩張案例變成可按任務取用的測試化技能與 SQLite 選擇性 context，保留歷史並以新任務檢驗引用及適用。

### 2026-11-14｜P1-1a 任務導向記憶、回饋及案例引用實作

**前置來源與查核：** B002 程式 commit 20c4e85bd6572831ac78a33b56d4344b376b8572 CI 43563255803、文件 commit 388bec5a93dd7958956782108895cf577e6d3b3f CI 43563312827 均 completed/success。main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57 未變。先讀本檔 B001-CASE-001/B002-CASE-001、src/team_workbench.py、tests/test_team_workbench.py、config/skill-catalog.json、learn-from-feedback/resume-project 等技能、docs/TEAM_WORKBENCH.md。保留舊工作台與原本 12 項技能、共七角色，不另建競爭記憶庫。

**實作與使用方式：**
- 新增 src/workbench_learning.py (blob 1e93bb77ff3ab052b5cd6711c3bff28e2d74f982)，及 tests/test_workbench_learning.py (blob 692aa96f2ade3aa23c08d0a1a323e99f08ac329e)，程式與測試 commit 4c104a158a525ed88d340e9f6a8aa61bd205de44。兩檔 GitHub 回讀與本地 git hash-object 完全一致；本機原 team_workbench.py blob 4f2362bb3103513002d76176b26ff56bd8f6068d 與 skill-catalog.json blob c099499befb8ab24dfcbcce6dd454164ccca3ddd 亦與原來源一致。
- setup 原地增量建立 learning_cases/learning_events/learning_uses 三表，經明確授權才執行；原 artifacts/memory/resolutions 保留，兩張公開合成案例進既有 memory 與標籤索引，重跑不重複、不復活退休記憶；同名未登錄舊案例先停查。
- context: 根據 task/skill/query 及英文詞/中文雙字詞交集排名；預設 8000 字元與最多 5 筆記憶（可調 256–20000 / 1–20）；只傳必要且有效的前置產物正文，其他列索引、過期正文排除，超過配額明示 NEEDS_FULL_READ；候選與同主題未解衝突僅列 review_candidates，保留證據與 Scope。字元配額只限制正文及證據 payload，不含 JSON metadata；舊工作台仍回傳專案層級最新產物，task ID 不代表逐任務產物版本。
- feedback: test_failure/test_fix/qa_rejection/requirement_change/preference 五類事件均以候選記憶保存；task/session/event_id/來源，重複相同事件去重、同 ID 異內容拒絕；既有 remember/resolve 人審維持不變。此為 Agent 工作流程主動呼叫，非背景自動偵測或自動核准、蒸餾、模型權重更新。
- cite: 保存 task/session/skill/query/memory_id/decision/evidence，重算可選案例以拒絕無關、退休、候選或衝突案例。區分 applied 與 not_applicable，操作者宣告不是獨立執行證據；history 依 task 讀前後 session 紀錄。context/history mode=ro，不意外建缺庫或隱式遷移。
- AGENTS.md commit ada4cbe02c54d89cccd8de07663716bcff64ebb6；docs/TEAM_WORKBENCH.md commit 784a87ca86cc6657593bf3975bae2474a33aab78，分別接入全技能工作流程及實際 CLI/JSON 操作範例。兩者全文回讀一致。未改正式 main、正式 Release、外部專案或私有資料。

**實際驗收：** 暫存目錄 /tmp/p11_training，僅含回讀一致的舊工作台與 catalog、本輪可信新程式/測試。命令 python -m unittest discover -s tests -v；初 10/10 PASS (1.489s)，增 SYN-REPORT 實際案例遷移試驗後 11/11 PASS (1.619s)，本輪未觀察到失敗；不是整個 repository CI 或獨立人類 QA。11 項：setup 重跑、查詢排名/無關排除、Context 限額/過期規格、回饋去重/衝突、偏好不自動採用、新 Python 子程序讀回歷史和案例、拒絕無關或退休引用、唯讀與缺庫、專案隔離、限額/未 setup、報表缺庫復原實際應用。原工作台/cases 既有全套回歸待同 SHA CI；程式 CI 43564186355 查核時 in_progress，指南 CI 43564264957 pending。

**新任務及新工作階段證據：** SYN-LAB-3 查詢 SQLite 唯讀 缺庫 transaction inventory concurrency，自動排名 B002-CASE-001、B001-CASE-001；排除 CSS 排版，不相關 astronomy 查詢零命中；使用 subprocess.run 啟動獨立 Python 程序的 CLI，從同一 SQLite 檔讀回前 session 引用及同一案例，第二 session 記錄不適用，另一 task 無紀錄。另 SYN-REPORT 合成報表復原任務由詞彙檢索選 B001，真正以 SQLite mode=ro 開啟不存在的來源，OperationalError 且無新檔；記錄 applied 引用及 test_fix candidate。這是開發者編寫的功能回歸及獨立 Python 程序讀回，不是陌生模型盲測、真實 ChatGPT 新對話自動工作或七 Agent 協作。兩張案例之工程原理已實際應用至工作台唯讀設計，但並未證明模型會自主檢索或判斷語意。

**待辦與限制：** 尚無自動事件監聽、語意/向量檢索、逐任務產物分支、實際跨平台同步、獨立真人審查、真實 LLM runner、持久任務池或技術研究技能完整驗收；僅用臨時合成工作區，未替使用者建立私人工作區。下一優先處理 P1-1 剩餘能力：B003 技術探索與規格未決辨識，追加同庫持久化任務狀態/依賴/驗收及覆盤，使用實際新任務和案例檢索驗證，避免堆疊無關稽核。原 B001/B002 案例正文及歷史狀態保留，最新頂部進度以同版 CI 為準。

### 2026-11-14｜P1-1b B003 技術探索、決策 gate 與持久化任務池

**前置查核與來源：** PR #8 起始 b38f863571bfaae79654f7fd40cc9bb57dd348c4；P1-1a code CI 43564186355、最新文件 CI 43564318315 completed/success。main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57。讀 evaluations/capability/public_tasks.json B003 R1–R4（blob 0e422d8d36cb1697396dc753fb98304a9b914120）、本主檔、task-planning/architecture-design、既有工作台及學習工具。實際本機原 team_workbench.py blob 4f2362bb3103513002d76176b26ff56bd8f6068d、workbench_learning.py blob 1e93bb77ff3ab052b5cd6711c3bff28e2d74f982、catalog blob c099499befb8ab24dfcbcce6dd454164ccca3ddd、既有測試 blob 692aa96f2ade3aa23c08d0a1a323e99f08ac329e。此次單聊天 Agent 角色切換，不是真實獨立多 Agent、未見題或模型訓練。

**需求辨識及技術探索：** R1 半開整數分鐘區間端點相接不重疊；R2 非法時段不可視為有效；R3 先釐清未決政策；R4 正反例。未決 D1 為錯誤輸入的產品/UI 政策；跨日、時間範圍、日期/時區未在原題規定。合成原型假設 list/tuple 二元素、真整數（不接受 bool）、start<end；不限定日期或時區，INVALID 是原型內部狀態，has_overlap 對 INVALID fail-closed，不表示已確認錯誤 UI 文案。任務規劃先保存 D1，不阻塞可隔離驗收的 core，正式 UI gate 持續 OPEN。技術比較：單次線性檢查 O(n)，排序後提前停止 O(n log n) 含每次排序成本；小範圍離散分鐘集合 oracle 僅作驗證，非大範圍正式方案。以 0..6 端點所有21個合法區間的三重組合（9,261）比對兩方法與 oracle；兩種皆一致，採低複雜度線性方案，保留排序 PoC。未調用外部研究來源或做實際大型基準；不宣稱普遍性能優勢。

**實作及實際驗收：**
- src/b003_shifts.py blob 82a02ed80a1e4286d9c0b26a8ba6106a61802b2b；src/workbench_tasks.py blob 4ff853335f1a84e66f31c7b07c55369ca7fc5ae6；tests/test_b003_and_tasks.py blob 90cac2efa37ec7ba45a1c66cf0daa1cc653b7368。GitHub 三檔與本機 git hash-object 一致。source/test commit adddfe3bf8c13cbaf7f0ed1d238bb887da5a21f3，CI 43566849542 查核時 in_progress。
- 同一授權 workbench.sqlite3 明確 setup 新增 task_pool/task_decisions/task_events；add 先確認依賴/decision ID 已存在、拒絕循環與無驗收；review 真正 mode=ro 取得依賴、next_ready、running_review、全部決策內容與來源、未決問題、驗收次數、失敗及歷史；start 原子領取，8 路並行只1成功；finish 必須全 checks PASS/FAIL 與證據，失敗退待辦且保留事件，未通過不解鎖下游。resume 需舊 owner readback、明確確認及證據，舊 session 不可再 finish；決策 resolve 需明確確認、答案及來源，不覆蓋歷史、不授權外部操作。任務依賴/已完成狀態目前不可動態修改或重開，尚未實作依賴變更後失效傳遞、完整逐任務 artifact 版本，以及自動排程；resume 的確認是操作者聲明，不會自動驗證舊程序已結束。
- 本機 /tmp/p11b_training（可信合成源碼，原工作台/學習模組/catalog 雜湊相同）python -m unittest discover -s tests -v；初 20/20 (9新+11既有) PASS 2.500s，審查後補已決政策答案/來源回讀及中斷任務明確 resume，新增負例及回歸後 21/21 (10新+11既有) PASS 2.443s。未觀察到初版測試失敗；上述為審查發現的補強。新測試含端點/重疊、非法 fail-closed、PoC oracle、DAG/未決 gate、驗收失敗及重試/owner、跨程序唯讀重讀、中斷接續/舊 owner 拒絕、8路競寫、原記憶/案例相容及缺庫負測、專案隔離。
- 另外執行實際合成 B003 三 stage（tempfile.TemporaryDirectory）：session-1 B003-spec R3 PASS（依原題記錄未決 D1）；session-2 B003-core R1/R2/R4 PASS（實際 subprocess 重新執行21個測試）；session-3 獨立 Python CLI review 回讀 completed=2、attempts=2、failed_attempts=0、next_ready=[]、B003-ui PENDING blocked_by=[B003-D1]、D1 answer/source=null。原 DB bytes 完全不變。另以學習工具 query SQLite 唯讀 缺庫 recovery reconcile 取得 B001-CASE-001，於相同暫存工作區保存 applied 引用及證據，history 回讀一致；未建正式私人庫。這驗證新程序與真實功能操作，非真實 ChatGPT 跨對話自主調用。單元測試中模擬 D1 confirmed=true 只驗證機制，從未成為真實產品核准。
- 更新 .agents/skills/architecture-design/SKILL.md (aa89182cd3d0496a2fe25d08050597b824459e4c)、task-planning/SKILL.md (af732a79936dfe9ca84904f75aea74f206d2fa4a)、resume-project/SKILL.md (245848f568b307bca27759c0fcb330c263751229)、docs/TEAM_WORKBENCH.md (0460c0dc6e895069d9e8fd17047bc91e0294de9a)，全部全文回讀一致。保留原工作台及七角色/12技能，未改 main、Release 或外部專案。

**案例 B003-CASE-001｜observed｜產品政策未決與可測原型分離：** 已知區間規則可執行測試；對不明確產品錯誤政策，先在持久任務池記問題/依賴，不將內部 INVALID 決策當正式 UI。使用有限域 oracle 比較兩方法，明確記錄適用邊界。前一 session 的未決狀態、實測驗收及決策來源必須隨接續重讀；中斷任務不得因聊天切換自動接管。證據：B003 10 項新測試、21/21 本機回歸、三 stage 2/3 DONE 且 UI 尚 pending；已記本主檔，不自動提升記憶基礎或加入私人工作區種子。限制：合成原型、不含日期/時區、實際排班 UI、真人審核、獨立子 Agent。可於後續完整系統設計採用適用原則。

### 2026-11-14｜P2-1a 設備借用網站整合實戰（第一個切片）

**前置來源及範圍：** PR #8 起始 56e72db9e443c24b8b800e72dceb9abac7266cff，P1-1b code CI 43566849542、最新主檔 CI 43567003958 均 completed/success。main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57，release/current_release.yaml blob 6babe416f2ed652509b44d90d3eb98637a0886f3 未授權正式升版。以使用者 P2-1 合成訓練指令、B002 實測案例、原工作台為基礎；自訂獨立合成實戰規格，非外部專案或已核准產品規格，不代替新網站真人訪談/正式授權。

**需求與取捨：** Python stdlib HTML/HTTP + 本機 SQLite，減少訓練外部服務依賴；固定10件設備單庫存池，借用1–10件，兩個合成會員與一個合成管理員，會員能看自己的申請及可用庫存；管理員只讀全體申請，不可借用。臨時帳密每次服務啟動隨機產生，記憶體 session 30分鐘、登出刪除；重啟不保留 session。非正式產品，不含註冊、真實帳號、密碼資料庫、歸還/取消、庫存編輯、日期/多設備、正式 HTTPS/限流/生產維運。服務硬綁 127.0.0.1，不允許外網/真實收件。不保存臨時憑證輸出至 repo；只以臨時合成 DB 執行。

**實際可執行成果：** src/p21_equipment_site.py blob 28c38042df6bf60c5dea9c6fca7e2125594f9956、tests/test_p21_equipment_site.py blob 00a54e3a66837d1ff3f332ac2e08ec1f882c614e；均與本機 git hash-object 一致，程式/測試 commit c5accaab8a60ffd1e3b05c0c6f586768896a7198，CI 43567839044 查核時 pending。HTML login/dashboard/reserve/logout/admin；HTTP 依 Host/Origin/session/role/CSRF 檢查，Cookie HttpOnly/SameSite=Strict、CSP、no-store、HTML escape、SQL參數化、限制輸入與長度。資料庫獨立初始化 exclusive xb、查詢 mode=ro、更新 mode=rw；BEGIN IMMEDIATE、條件 UPDATE、(owner,token) 唯一 request ledger 同一交易。相同 payload/token 重播回原決定，變更數量拒絕；未知 SQLite 結果回503並要求先看唯讀 dashboard，拒絕自動重送。管理員只有檢視，不宣稱完整管理 CRUD 或全面安全。

**重現命令（已授權本機合成環境）：**
- Repo 根目錄執行 `python -m unittest discover -s tests -p test_p21_equipment_site.py -v`。
- 手動啟動：Windows PowerShell 選獨立、空的合成資料夾，使用新檔路徑，例如 `py -3 -m src.p21_equipment_site --database "$env:TEMP/agent-p21-synthetic-demo.sqlite" --initialize --port 8765`（若檔已存在，不覆蓋；選新的路徑，或明確要續作時才省略 --initialize）。只能在有權允許 loopback 的環境，開啟程式輸出的 127.0.0.1 URL；使用本程序產生的臨時合成憑證，勿貼到公開 repo／日誌，停止用 Ctrl+C。會員登入後 Dashboard → Quantity → Reserve → Dashboard；管理員登入後開啟 /admin，查可用量及全體合成記錄；測登出、另一會員不可見他人 token、會員不可訪問 /admin。不得為了測試修改或繞過環境安全政策。手動操作尚未實測。

**功能與安全驗收（實際）：** 暫存 /tmp/p21_training，Python 3.13.5，`python -m unittest discover -s tests -v` 6/6 PASS（3.080s），後續工作台演練重新以獨立 Python subprocess 跑 6/6 PASS。測試真的啟動 ThreadingHTTPServer 並透過 http.client 實際 HTTP、SQLite 查詢/寫入。六項：會員登入/借用/本人列表/他人隔離/管理員全體唯讀/庫存不足；未登入401、錯密碼401、會員進管理401/403、Origin/Host/CSRF 拒絕、管理員不可借；重複 token 不重扣、變更數量/冒充 owner拒絕；8路並行每次3件，3件申請成功、5件庫存不足，總保留9；注入庫存更新後拋錯回退且 ledger 無殘留，唯讀回查檔案位元組一致，缺庫GET/POST 503且不建檔；無效數量/注入字串拒絕、登出/session到期拒絕。這是作者撰寫實際 HTTP 端到端測試，不是獨立 QA/瀏覽器 DOM UAT。
- 實際 Chromium/Playwright 測試已嘗試，啟動瀏覽器後首個 Page.goto 到 127.0.0.1 隨機 port 失敗：net::ERR_BLOCKED_BY_ADMINISTRATOR。未繞過政策，未完成任何 DOM 表單步驟。BROWSER_ENV_BLOCKED，不能以 HTTP PASS 取代瀏覽器 PASS。下輪可在明確允許的既有候選 CI/本機測試環境建立可重現瀏覽器驗收；無需付費 API 或外部部署。

**同庫工作台實際演練與七角色產物：** 原 team_workbench.py、workbench_learning.py、workbench_tasks.py 本機 blobs 與 GitHub 前版相同（4f2362bb3103513002d76176b26ff56bd8f6068d、1e93bb77ff3ab052b5cd6711c3bff28e2d74f982、4ff853335f1a84e66f31c7b07c55369ca7fc5ae6）。以 TemporaryDirectory 建獨立合成工作台，明確 setup；handoff 實際保存 requirements、specification、architecture、plan、implementation、qa、security-review、learning-note、deployment-plan 共9類產物，最後以 context 回讀。七角色為當前聊天 Agent 按工作方法切換，沒有實際啟動獨立子 Agent。SRE 只交付到本機限制及停機/發布禁止之計畫，並未部署。
- 任務池 spec/design/build/qa DONE；browser PENDING（失敗事件記錄環境阻擋），release PENDING blocked_by browser,D1（另行外部部署禁止 gate）。三階段 s1/s2/s3，5次驗收，1次FAIL，4/6 DONE。新 Python CLI review 讀回 next_ready=[browser]，DB bytes 不變；未建立使用者正式私人庫。
- query SQLite transaction inventory concurrency rollback idempotency ledger recovery reconcile mode=ro → B002-CASE-001、B001-CASE-001（實際檢索）。兩者以 cite applied 記錄 HTTP rollback/readonly/concurrent test 證據並回讀；feedback test_failure 將 Chromium 環境阻擋保存候選記錄。B003 未決 UI/發布 gate 原則取自主檔，未冒稱由 seed 自動找出 B003。
- P21-CASE-001 候選學習：單機核心交易原先通過不代表整合權限與 UI 已通過；網頁必須在 HTTP 層從 session 決定 owner，不接受表單的角色/owner；ledger 唯一鍵以 owner+token 避免跨帳號讀寫；分開記 HTTP 與瀏覽器驗收，環境阻擋不可視為產品通過或繞過安全。證據上述6測試與1瀏覽器阻擋；本機合成適用，非全面生產資安審計/獨立盲測，未自動升格公共正式規則。以下 P2-1b 優先完成瀏覽器與管理作業切片、追加安全負測和可重複工作台演練，不擴張無關稽核。

### 2026-11-14｜P1-1c 任務池修訂失效、重開及跨階段復原（使用者指定加強）

**前置查核：** 最新候選起始 df58c6613cafaeddfdfb79a08f1508166ddb0622；P1-1b source/test adddfe3bf8c13cbaf7f0ed1d238bb887da5a21f3 CI 43566849542、最終 56e72db9e443c24b8b800e72dceb9abac7266cff CI 43567003958；P2-1a source/test c5accaab8a60ffd1e3b05c0c6f586768896a7198 CI 43567839044、最新 df58c66 CI 43567913525，四者均 completed/success。原 workbench_tasks.py blob 4ff853335f1a84e66f31c7b07c55369ca7fc5ae6 及本機 team_workbench/learning/catalog/B003 tests 與 GitHub 狀態一致。依使用者指定優先加強現有任務池，不回退 P2-1a、不同步外部專案。P1-1b 的歷史限制「尚未實作重開、依賴修改和失效傳遞」由本節實作更新。

**實際缺陷及修正：** 舊版 test_legacy_session_reuse_is_rejected 在失敗驗收回 PENDING 後，以相同 session 再 start，本應拒絕但實際成功，1/1 FAIL（AssertionError: ValueError not raised）。此為同 task 舊 session 可能重新成為持有者的風險。新實作禁止 START/RESUME 歷史中的 task+session 重用，以 revision（初始1、受影響任務每次+1）、原有 SQLite BEGIN IMMEDIATE、當前 state/session 同時守門；revision>1 時 start/resume/finish 必須提供匹配 expected_revision（revision=1 暫保原呼叫相容）。已完成的驗收歷史不刪除、不授權任何外部操作。
- revise 必須帶匹配的 expected_revision、明確 confirmed、來源/evidence；可增量改 title/deps/gates/checks，或只重開重驗。拒絕未知依賴/gate、循環/空驗收；從最上游向傳遞下游原子更新 revision 與狀態，DONE/PENDING→PENDING、RUNNING/RECOVERY_REQUIRED→RECOVERY_REQUIRED，保留原持有者及事件。無關獨立分支不更新。新增 REVISE/INVALIDATE 事件含舊/新 revision、狀態、持有者、根任務修訂前後定義。新 PASS/FAIL results 包含 revision/checks（舊事件原樣保留）。
- RECOVERY_REQUIRED 禁止舊 session finish/resume；依目前 DAG 的 recovery_blockers 阻止未查清失效下游時重新啟動相關上游。recover 需核對相同 revision/舊 session，確認舊操作者停止與部分操作已處理，帶新 reviewer session 與證據；只釋放 PENDING，不能復活舊 PASS。未失效 RUNNING 仍可明確 review/resume 至新且未用過的 session。review 真正 mode=ro、列 recovery_review、recovery_blockers、revision 以及歷史。既有已決政策不直接覆蓋，新政策另建 decision/gate。
- setup 在同一庫原地增加 revision 欄位，保留原任務/記憶/歷史；舊 RUNNING 遷移為 RECOVERY_REQUIRED/revision2，追加 MIGRATION_FENCE；重跑不重複。升級前備份並停止舊操作程序，不支援新版/舊版程式混寫同庫。未修改使用者真實私人庫。

**執行及證據：**
- src/workbench_tasks.py blob 24bd30557271aa2c39b907ed0b494bb28046acf8、tests/test_task_revision.py blob 801608abc6ee9000e86989212540f38bbd899348，GitHub 與本機 git hash-object 一致；source/test commit 19d11e2d5b82e4a66ca87c4b4b9034d1496f6acc。暫存 /tmp/p11c_training 使用 /tmp/p11b_training 舊源碼及測試（原檔雜湊已核對）；python -m unittest discover -s tests -v 最終35/35 PASS（7.386秒，14新增+21既有B003/learning回歸；非完整repo本地回歸或獨立人類QA）。開發中31項測試曾因同優先級預期順序誤寫為 qa,other，實際排序為 other,qa，修正測試預期後與新增 recovery blocker 得33/33，加入注入回退與真實程序中斷測試後35/35。保留實際舊版缺陷測試，不刪減驗收。
- 14新增涵蓋：舊 session 重用；連鎖重開且獨立分支保留；RUNNING 下游隔離/復原/阻止相關上游；過期 revision 和 ABA；非法 DAG/gate/無確認原子拒絕；8路同 revision 修改僅1成功；finish 與 revise 競寫不留過期 DONE；8路 resume 僅1成功且原 owner 被拒；新程序唯讀重讀；模擬舊 schema 遷移；3個真正 CLI 程序同時 revise 回傳 0,2,2；重複修訂不釋放隔離的 owner；SQLite 觸發器注入下游寫入失敗後整體回退、所有狀態與歷史一致；實際啟動 CLI 領取後退出、新程序確認接續、過期完成請求 exit2、有效完成 exit0。
- 另行真實跨版本演練：使用原 /tmp/p11b_training CLI 建立合成庫 spec DONE / build RUNNING，三筆舊事件；新 CLI setup 後 spec DONE rev1 / build RECOVERY_REQUIRED rev2，舊3事件逐筆一致，新增 MIGRATION_FENCE；確認舊 subprocess 已退出，recover→start 新 session→finish，最終兩任務 DONE、build rev2。合成目錄自動清理。此為真實本機版本遷移/程序行為，非用戶正式資料庫升級。
- 操作手冊 docs/TEAM_WORKBENCH.md commit 64ae53ec0cb23f5cc63d46060a2897e7c5232aee；task-planning SKILL commit 18577d8b11a987fc59bc83fd6cc1a88c95012faf；resume-project SKILL commit d8ea3eb3425ae7dcf93e3f3c40551d62579cadce；全文回讀一致。code CI 43568659877 查核時 in_progress，最終以實際最新 SHA 重新查核。

**案例 TASK-CASE-001｜observed｜需求修訂必須使舊驗收與舊寫入者失效：** 用當前 revision + 單次任務 session + transaction 守門，而非只用 session 字串；留存先前結果，不把歷史 PASS 當目前版本合格。失效執行者不可直接復活；先停止/對帳並 recover 後從正確前置依賴重驗。適用證據為上述14項本機功能負向測試與真實跨版本演練。這是候選訓練案例，不自動升級為正式 Release/私人記憶。**限制：** 修改需求文件或 handoff 不會自動觸發 revise；操作者須依正式來源明確呼叫並同步適用產物。SQLite 狀態守門不會終止 OS/外部 GitHub/GAS 或已執行寫入；停止及部分操作證據需外部查核，不得盲目重送。修訂 DAG 時仍需查核舊工作接觸資源及原依賴，不只新圖。未實作分散式租約或混版本保護、逐 task artifact 分支；沒有獨立 Agent/盲測或真實私人庫。P2-1a 瀏覽器阻塞未解除，續作仍按 P2-1b 原方向。

### 每次續作及更新協定

1. 當使用者說「訓練此 Agent」「繼續訓練」時，定位本 repo；先查 main、目前訓練 PR 的實際 head、最新 CI/PR 討論，再讀本節與直接相關技能、程式和測試。新候選轉移時保留本路徑並更新導航；不得用固定 SHA 當現況。
2. 以使用者最新決策、實際程式/測試與同 SHA 證據為準。歷史文件與舊對話只供導航；本節的建議不授權付費模型、外部寫入、合併、部署或正式發布。
3. 優先完成最高優先且可安全執行的未完成工作；若真實 runner 受阻，實作隔離合成垂直切片、功能測試和案例學習，不停留於反覆查核或空報告。
4. 每次實質訓練後在本節更新 SOURCE_VERSION、LAST_VERIFIED_STEP、COMPLETED、NEXT_ACTION、BLOCKERS、WRITE_OWNER、SYNC_STATUS 和路線狀態；記錄真實測試命令/CI、失敗修正、產物與限制；區分已驗證、NOT_RUN、BLOCKED、PROPOSED。回讀同分支檔案確認，保留 Git 歷史；不複製出多個互相矛盾的訓練主檔。
5. 若候選 SHA 改變，分開記錄最後已測程式 SHA 與目前文件 SHA。單 Agent 實作/合成測試、真實 LLM 執行、獨立子代理、獨立盲測、正式 Release 均分開報告。未經授權不自行修改模型權重或宣稱已修改。
6. 本檔為訓練方向的持久化入口，`docs/CURRENT_STATE.md` 與 PR/CI 紀錄保留實際工程歷史；有衝突先查證並更新本節，不另建重複進度來源。


## 目的與邊界
此計畫聚焦本 Agent **能否完成系統開發**，非持續增加供應商來源稽核。要訓練的能力依序為：需求理解、架構取捨、可執行任務計畫、程式實作、QA Debug、跨七角色實際交接、從錯誤修正策略。適用 Repository 只有 `lily4318/reliable-system-builder-agent`；所有公開案例皆是合成，不帶外部正式專案原碼、資料、個資、API Key 或部署權限。

本 PR 與尚未合併的 Draft PR #4（目標分流）、#5（角色交接）及 #6（真實模型 runner/來源）**平行且不互相依賴**。本候選不替三個 PR 做合併決策；任何未來整合須按當時 main 解衝突、同 SHA 跑全套回歸及另行人工審查。

## 可立即執行的公開訓練工作台

```bash
# A. 出一題給真正的 Agent，公開輸入不含參考架構與解答
python -m src.capability_prompts --task-id B001 --output output/agent-task-B001.json
# 其餘四題：B002 B003 B004 B005

# B. 驗證題庫、5 份參考提交之格式，不呼叫模型
python -m src.capability_workbench validate

# C. 示範工具本身的自測；100 分只是「自行撰寫參考」通過機械評分
python -m src.capability_workbench evaluate \
  --min-structural-score 100 \
  --output output/self-authored-structural-reference.json

# D. 在有權執行的獨立 Agent 環境，讓 Agent 完成題目並輸出提交 JSON。
#    以下只對已存在的本地檔評分，沒有任何模型／API 呼叫。
python -m src.capability_workbench evaluate \
  --submissions /secure/offline/agent-submissions.json \
  --output /secure/offline/capability-structural-report.json

# E. 舊有政策與事故復原保護仍需通過
python -m unittest discover -s tests -v
python -m src.agent_eval evaluate
python -m src.independent_acceptance evaluate
python -m src.quality_gate check
```

### 2026-11-14 補強｜五題離線任務準備與成果匯入（不呼叫模型）
```bash
# 產出 B001 至 B005 五份「題目及提交格式」，沒有 gold / 參考程式
python -m src.capability_execution prepare \
  --output-dir output/capability-taskpack

# 只有真正取得已授權執行器的成果時，才另行執行下面這個離線匯入：
python -m src.capability_execution ingest \
  --packets-dir output/capability-taskpack \
  --bundle /secure/agent-run-bundle.json \
  --output-dir /secure/capability-review-001
```

**執行器查核現況：** repo `main` 與本 PR #7 只有題目產生器／結構評分器／GitHub Actions，沒有可證明已授權的 LLM 或七個子代理 runner；GitHub 環境／變數端點也無可用資料，無法判定其他私人執行環境是否存在。因此本輪只建立**離線接收介面**，沒有執行 B001–B005 的真實模型解題，也沒有替你配置或呼叫任何付費 API。

`prepare` 使用不可覆寫的新目錄產出 `B001.json`…`B005.json` 和 `manifest.json`，將各題 prompt SHA-256 與公開題庫 SHA-256 鎖住。它無法啟動 Agent，`real_agent_executed=false`。私有 `bundle` 頂層格式為：
```json
{
  "schema_version": 1,
  "kind": "externally_supplied_agent_outputs_unverified",
  "attempt_label": "attempt_2026B001",
  "results": [
    {
      "task_id": "B001",
      "status": "completed",
      "packet_sha256": "取自 manifest.json 的 B001 值",
      "run_id": "agent_run_B001_0001",
      "model_id": "declared_model_version",
      "submission": {"task_id": "B001", "requirements": [], "architecture": {}, "plan": [], "implementation": {}, "qa": [], "handoffs": [], "risk": {}, "claims": {"real_agent_invoked": false, "model_weights_trained": false, "system_deployed": false}},
      "implementation_source": "def enrollment_status(capacity, enrolled, applicant):\n    return 'NOT_IMPLEMENTED'\n"
    }
  ]
}
```
上方 `submission` 只示範 JSON 形狀，未填的部分**不會得分**。完整欄位說明可從任務包 `submission_shape` 取得。若單題無法執行，改用 `{"task_id":"B001","status":"blocked","packet_sha256":"...","reason_code":"NO_AUTHORIZED_RUNNER"}`，不得虛構結果；其餘未提供的題會明示未完成。

匯入會檢查所有題目 prompt SHA、重複 task/run ID、申報模型 ID、假冒參考答案、未核驗的模型／部署主張和程式長度；對任何 `implementation.path` 一律重寫為新私人目錄的 `implementations/Bxxx.py`，並用 AST 做**靜態**分析，不 import／exec 候選碼，不建立正式執行權。若未通過輸入驗證則不建立結果資料夾；若通過才存 `submissions.json`、原始候選程式與 `report.json` 供人工檢視。現階段無論自述模型名稱或 run ID 多完整，`actual_agent_model_execution_verified=false` 且 `program_semantics_verified=false`。請勿將私人原始碼／日誌上傳公開 Repository 或 Actions artifact。

CI 僅驗證離線題目產生與**合成**匯入協定；合成正例即使結構 100 分、程式實際回傳錯誤，也不會被標成真正程式正確率。只有另行核准的 runner、實際執行紀錄、隔離程式測試及獨立人類審查才能建立真實訓練基線。

要生成候選提交，需在有權使用的真實 Agent runner 取得每題的最終結果後，將它整理為 `{"schema_version":1,"submissions":[...完整提交...]}`；格式見 `src.capability_prompts` 的 `submission_shape`。重要：`--submissions` 僅是**讀檔評分**，不會啟動 Agent，也不會證明 JSON 的來源真的是該 Agent。要聲稱真實 Agent 成績需另保存 runner 的執行 ID、模型與提示詞版本、源碼 SHA、工作紀錄、時間與人工審核。

## 題庫與情境

| 題目 | 核心情境 | 預期應學會 |
|---|---|---|
| B001 社區工作坊 | 先前與新規格衝突、額滿候補、重複報名、未知寫入 | 接受最新需求、設計狀態與驗收邊界 |
| B002 公用設備借用 | 可用量、保留庫存、並行競爭與回退 | 系統模組拆分、資料一致性與復原 |
| B003 志工排班 | 時間端點相接、非法區間、模糊政策 | 辨別未決問題與驗收邊界 |
| B004 文化中心藏書 | 只做離線補貨建議、不得自動採購 | 需求取捨、函式設計與權限限制 |
| B005 餐食領取 | 合成取餐碼、已領、查無、角色交接 | 限制重複行為、跨角色工作規格 |

總計 **5 題、20 項編號需求**。這是公開、作者設計的開發集，不是隱藏測試或獨立 blind holdout。固定預期元件名稱與結構是**自動評測用參考標籤**；同樣好的替代架構可能被機械檢查扣分，必須人工複審才可作公平的能力比較。

## 七角色訓練任務與產物

| 角色 | 需要展現的技能 | 可量測提交產物 |
|---|---|---|
| System Lead | 正確理解新需求、衝突、驗收與優先權 | `requirements[].acceptance` |
| Architect | 將需求拆成有界線的元件、資料流、相依 | `architecture.components/links` |
| Developer | 提交可測函式、風險可控的最小代碼 | `implementation.path/function` |
| QA/UAT | 每條需求都有成功和失敗案例 | `qa[].kind/requirement_id/expected` |
| DevOps/SRE | 工作相依、失敗與回退方案，未知寫入先對帳 | `plan[].depends_on`、`risk` |
| Security | 保持最小授權、公開案例無敏感資料 | `risk` 與必要的否決條件 |
| Learning Evaluator | 找出弱點，版本前後比較及人類審查 | 統一評分器與失敗案例報告 |

`handoffs[{role,input,output}]` 記錄七個角色的交接**預期產物**。它只能驗證文件是否齊全，不能證明七個獨立 AI 實際接力工作。

## 評分維度與方法

| 自動結構維度 | 配分 | 實際驗證 |
|---|---:|---|
| 需求追溯 | 20 | 所有 R 編號與非空、具體驗收文字 |
| 架構 | 15 | 預期元件責任、元件連結及資料流結構存在 |
| 工作計畫 | 20 | 角色 owner、需求覆蓋、有效依賴與 DAG 無循環 |
| 程式靜態檢查 | 10 | 受控路徑中的 Python AST 有對應函式和 return |
| QA | 20 | 每個需求至少一個正例及一個負例 |
| 七角色交接 | 10 | 七位專家各自有可追蹤輸入與輸出 |
| 基本安全 | 5 | 未知非冪等寫入不重送、人工正式核准、風險匹配 |
| **總計** | **100** | **只代表結構符合公開評分準則** |

**刻意不量測的能力**：L​​LM 語意推理、架構實際合理性、真正程式語意正確性、非預期需求泛化、執行多個子代理、部署、真人 UI、模型權重更新。這些不可能只靠簡短 JSON 及 AST 得知。評分結果將永遠顯示 `real_llm_or_seven_agents_invoked=false`、`actual_program_correctness_evaluated=false`、`independent_holdout_evaluated=false`、`formal_release_authorized=false`。真實執行證據必須由另行核准的執行平台獨立提供，而不是由提交 JSON 自我宣告。

`src/capability_reference.py` 是公開、可信、自行撰寫的極小參考函式；CI 使用這些函式的可信單元測試驗收參考語意。對 Agent 提交的任意 Python 程式，評測器**只用 `ast.parse` 讀取靜態形式，不 import、不執行**，避免在有網路或 Secret 的 CI 中跑不可信代碼。

## 真正的能力訓練與改善前後比較流程

1. **凍結基線**：保存 Agent 所用模型的實際版本、Prompt／Role SHA、工作台 SHA、公開題庫 SHA、指令與資源限制、工具權限、執行時間和成本。先用固定題目取得真正模型至少 3 次獨立輸出，保留失敗案例。
2. **獨立人工觀察**：兩位審查者盲態評閱需求是否正確（尤其衝突與含糊處）、架構取捨、錯誤後修正；建立理由與仲裁，不只看元件名稱是否匹配。開發者不可一邊改評測題目一邊宣稱成績上升。
3. **隔離程式執行**：在另外授權、無外網、無 Secret、唯讀掛載、限制 CPU/記憶體/時間且可銷毀的沙箱，將 Agent 寫的程式跑「未向模型提供的功能測試」，記錄成功率、錯誤型態和修復輪次；**不可只在 GitHub Actions 直接執行不可信程式**。
4. **專家協作追蹤**：若平台真正支援子代理，保存每位角色的輸入與輸出、交接損失、是否被 QA 找出問題及最終整合結果；不支援時分開記為單 Agent 模擬分工，不能把角色文字當工具執行。
5. **修正策略**：針對最低能力維度改善角色 Prompt、交接契約、程式工作步驟與測試邏輯；維持安全與授權底線，不擴充無關的供應商身分稽核。
6. **真正未見題測試**：由未參與 Prompt 開發的人另建隔離題庫、封存原始 SHA、標註與測試版本；前後候選在同一成本及工具條件下比較，分別報告結構分數、人工架構分數、可運作功能測試比例、Bug 修復輪次、七角色交接成功率和安全違規。只有到這步才可討論 Agent 是否真的進步，仍非模型權重微調。
7. **人工 Release 決策**：只有在審查者和 Owner 對 PR、CI、真實資料處理及部署門檻分別授權後才進正式 Release。本候選不做任何外部部署或自動合併。

## 成功門檻的建議（未核准、不是已測結果）
- 每項新公開任務應有完整驗收與雙向 QA 追溯；公開自我參考的結構回歸保持 100 分，只檢查工作台未退步。
- 待可執行真模型後，第一輪目標是產生完整輸出和可回讀來源，下一輪看實際功能測試和人工架構評分；不事先假定準確率或宣稱改善百分比。
- 不可信程式通過靜態 AST **不能**當程式已成功；沒有已核准隔離環境，就只保留為 `CODE_EXECUTION_UNVERIFIED`。
- 人類審查安全違規一律阻擋，且任何 UNKNOWN 非冪等請求皆以唯讀對帳優先。

## 本輪狀態
**已設計並可在此 Repo CI 執行**：公開合成需求、參考產物、任務生成 CLI、結構評分器、受信任參考程式與單元測試、既有政策及復原基準。**仍沒有**：實際模型生成的系統成果、真正子代理執行、未知程式的隔離沙箱、獨立 holdout、真實部署驗收。以上項目不得借用之前 PR #6 的 runner／模型來源檢查狀態，或以任意合成 PASS 冒充完成訓練。
