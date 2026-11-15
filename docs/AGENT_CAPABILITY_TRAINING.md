# Reliable System Builder Agent｜自主開發能力訓練與基準評測（獨立候選）

## 最新訓練主檔｜2026-11-15（持續更新入口）

**使用者決策（2026-11-15 最新、TD-001）：** 以教材的專業角色、技能、記憶、工作空間及實際工作覆盤為核心，使用既有 AI 平台執行；本地模型降為選用評測工具，保留已完成的工程能力。此決策取代歷史 P1-2「本地模型優先／缺本地模型先阻塞」的接續順序；不否定真實獨立評測的價值。每次先讀本節及 [訓練決策紀錄](training/DECISION_LOG.md) 的相關有效 ID，歷史頁面僅供證據查核。未核准之建議不覆蓋正式決策；本候選不代表已發布 main 或額外授權。

- TASK_DOMAIN: RELIABLE_AGENT_ENGINEERING_CAPABILITY_TRAINING
- SOURCE_REPO: lily4318/reliable-system-builder-agent
- ACTIVE_CANDIDATE: Draft PR #8, candidate-skill-team-integration-20261114；https://github.com/lily4318/reliable-system-builder-agent/pull/8
- SOURCE_VERSION: Latest verified code/tests/common-mode documentation 7cd8085e6fd9f320fea0e0526cb3b2fd6a354af0 / CI 43691876099 success; NATIVE-AUDIT-001 evidence and acceptance supplement commit a4676be98fb04f4e516c6575062096ef449ca06f. Current Draft PR #8 head authoritative; subsequent documentation-only CI must be checked separately.
- LAST_VERIFIED_STEP: Exact CI 43691876099/job 132744079996 completed/success, full raw logs 224366 chars, 390 tests in 43.728s/OK, both PublicContextTest methods and all steps success. Actual ChatGPT/GitHub native audit read 7 roles and 12 SKILL files, public case constants; wrote/verified source using authorized connector. Subsequent doc head ee431ec707a62269c44c272a35a6786529042f51 CI 43691956604 was in_progress at check; do not conflate.
- COMPLETED: All previously verified engineering capability retained; NATIVE-AUDIT-001 public-only lexical retrieval without workspace, two regressions, and three workspace modes verified in exact code/docs CI (390 PASS). Actual native connector work documented; seven roles and twelve skills read, not independently executed. Candidate lesson NATIVE-CASE-001 preserved, not promoted; retained private workspace behavior and safety rules.
- BLOCKERS: Latest documentation-only exact CI not yet verified. Fresh-conversation and different real task using revised workflow, role/SKILL direct-loading behavior and other platforms remain unobserved. Individual role/SKILL files unchanged; central AGENTS must be read. No independently executed subagents, actual user private-workspace access, private synchronization, semantic retrieval or blind model assessment claimed. TP-001 broader private persistence and TP-002–005 remain proposals; external project integration, paid API, formal release and deployment require separate authorization.
- WRITE_OWNER: 僅 Agent 候選分支；main/Release、外部專案、真實個資、付費模型或正式部署不在本次授權內。
- SYNC_STATUS: NATIVE_CODE_AND_COMMON_MODE_EXACT_CI_390_PASS; NATIVE_AUDIT_7_ROLES_12_SKILLS_READ; REPO_NATIVE_SOURCE_WORK_OBSERVED; DECISION_LOG_ACCEPTANCE_READBACK; LATEST_DOCUMENTATION_CI_UNVERIFIED; FRESH_CONVERSATION_ACCEPTANCE_NOT_RUN; NO_PRIVATE_WORKSPACE_USED; NO_INDEPENDENT_MULTI_AGENT; NO_RELEASE.
- NEXT_ACTION: Follow TD-001/TD-002: verify latest doc-only head and exact CI; then use a genuinely different authorized engineering task and REPO_NATIVE to recover source, choose relevant roles/skills/cases, produce verified work and examine transfer of NATIVE-CASE-001. If direct role/SKILL loading bypasses shared rules, repair observed conflicts. No local model requirement, redundant synthetic tasks, or external integration without authorization. Fresh conversation and other-platform acceptance separate.

### 最新有效訓練優先序（TD-001；取代下方歷史路線的執行優先順序）

**定位：** 不是建立另一個 LLM，而是讓 ChatGPT、Claude、Copilot 或其他已授權平台上的 AI 能按共同的工程角色與技能完成任務。是否可以真正啟用子代理、執行工具及持久化，依平台實際能力。單一模型按角色分工可完成實際工作，但必須標記單 Agent，不得宣稱獨立多代理。

| 優先 | 工作主線 | 可驗收成果 |
|---|---|---|
| 1 | 平台原生任務啟動與需求理解 | 從最新正式來源選擇適用技能與權限，沒有本地模型依賴 |
| 2 | 專業角色、技能及工作空間 | 按需角色與交接；讀實際 SKILL；獨立專案來源、案例與任務狀態 |
| 3 | 真實工作交付、測試與除錯 | 使用已有授權工具實作、驗證與修正實際問題；保留前後版本與日誌 |
| 4 | 覆盤、案例檢索、技能深化與遷移 | 記錄可重現的根因、修復、限制及引用；人審後增量更新，下一個不同任務觀察應用 |
| 5 | 跨平台可用性、獨立能力評測 | 按實際平台能力驗證；同模型/資源的比較與盲測另列、非日常工作門檻 |

以真實授權任務及實際缺陷為優先。無獲授權外部專案時，可在本 Agent repo 完成有實際價值的改進與驗收，不自動接管 Study1 或其他系統。公開 repo 僅保存去識別化、可泛化工程知識；私人工作空間仍需實際授權，不混用個資、研究資料、Secret 或私人日誌。

**覆盤最低證據：** 任務 ID、正式來源及 SHA、選擇的角色/技能及理由、案例 ID/適用判斷、實際產物及驗收、缺陷及根因、改進前後證據、可泛化原理與限制、候選/已核准狀態、下一次應用結果。檢索命中不等於有效遷移；不因單次結果或合成 CI 宣稱模型增益。無工具時標記限制，仍可完成授權範圍內可證實的工作。

**保留能力及選用工具：** 原七專家、十二技能、工作台、任務池及版本失效、候選 QA/安全、受限功能直譯器、案例庫、Ollama runner、公開基準及私人 holdout 協定均保留。Ollama、本地模型安裝、模型權重微調、擴充通用沙箱及獨立推論測試不作必要工作前提。除非有具體評測需求和適用授權，不再反覆要求本機 probe、增加模型執行器、provider 稽核或同類合成案例。

### 2026-11-15｜NATIVE-AUDIT-001 平台原生使用與真實流程修復（TD-001）

- 已讀回七角色及十二技能原文；共通 context/handoff 說明依賴私人工作區，GitHub-only 路徑缺少公開案例檢索及明確交接。實際執行模式 SINGLE_AGENT_ROLE_WORK / REPO_NATIVE：本輪 ChatGPT 使用現有 GitHub 工具完成讀檔、角色/技能選擇、公開案例 SOURCE_READ、原程式修正、回讀與 CI 查核。不是七個獨立子代理。七角色/十二技能可讀不代表自主使用全部技能已驗收。
- 保留原私人 SQLite，依實際授權選 PRIVATE_WORKBENCH / REPO_NATIVE / READ_ONLY。原 AGENTS 共通條款、START_HERE 與 TEAM_WORKBENCH 已更新，所有角色/技能原文暫保留，循根規則；無持久私有位置不得將私人資料寫公開 repo。repo-native 只用正式檔案、精確 SHA、原交接紀錄及 CI，不製造假私人收據。
- 原 src/workbench_learning.py 新增 public_context/public-context，使用原 CASES 及明確 opt-in TRAINING_CASES，原 _terms 詞彙檢索、有限字元、來源與匹配詞；不建立或讀寫私有 DB，不宣稱驗證必要產物、私人退休狀態、授權或保存 citation。私人命令仍要求 workspace。新增兩項回歸測試；中間 CI cancelled，後續 exact code/docs SHA 7cd8085e6fd9f320fea0e0526cb3b2fd6a354af0 的 CI 43691876099/job 132744079996 已驗證 390/390 PASS（43.728s），兩項 PublicContextTest 皆成功；新純文件 SHA 另行查核。
- 實際案例使用：B001/B002 唯讀缺庫經驗用于無 DB 檢索與拒絕 workspace 設計；P22-CASE-004 版本失效原則用于實際 GitHub head/blob 檢查及精確回讀；不移植 SQLite 原子性承諾到 GitHub。詳細證據、檔案 SHA、角色選擇、取捨及未決見 [原決策紀錄的 NATIVE-AUDIT-001](training/DECISION_LOG.md)。候選 lesson NATIVE-CASE-001 已保存，待不同任務的實際遷移及審查，不自動加入有效案例。
- TP-001 僅完成本輪授權的 GitHub 原生工作兼容修正，不升格較廣私人持久化提案；TP-002–005 原狀態不變。下一步核對 exact CI，再用不同真實授權任務驗證接續、技能應用和覆盤；不要求本地模型，不跨案不部署。

### 決策及跨對話接續（TD-002）

- 唯一有效訓練主檔就是本檔；[DECISION_LOG.md](training/DECISION_LOG.md) 增量保存長期討論、使用者決策、取代關係及來源。深入分析可另存 training/reviews/ 並索引，不另造主檔。已存 [2026-11-15 平台原生訓練覆盤](training/reviews/2026-11-15-platform-native-training-review.md)，涵蓋教材、架構選擇、案例學習及既有網站 Agent 的前次比較。TD-002 於本輪由使用者明確再次確認；待確認 TP-001–005 只見原決策紀錄，不是現行施工命令。
- 新對話先讀 START_HERE、AGENTS 及原候選 PR #8 最新 head 的本節與相關決策，再驗證實際狀態。正式使用 main/release 與候選訓練分開。
- 每次重要討論記錄 DISCUSSION/PROPOSED/CONFIRMED；實際修改及驗收另記 IMPLEMENTED/VERIFIED。改原檔並查寫前 SHA、寫後回讀和 exact CI；失敗清楚回報。
- 歷史段落、舊 NEXT_ACTION 與未採用方案保留為證據，不作執行命令。新使用者明確決策須增量更新本節與決策紀錄。跨專案或正式升版另需授權。

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

### 歷史工程訓練路線（留存既有能力驗收；執行優先序依上方 TD-001）

| 優先序 | 訓練任務 | 驗收 | 狀態 |
|---|---|---|---|
| P0-1 | B001 社區工作坊：需求→規格→架構→DAG→可執行垂直切片→QA；額滿候補、重複報名、需求衝突、未知寫入復原 | 獨立功能正反測、可重現的修復紀錄；公開合成實作與真實 Agent 評測分列 | LOCAL_FUNCTIONAL_PASS / FULL_CI_PASS |
| P0-2 | B001 案例記錄、蒸餾，遷移到 B002 公用設備借用 | 相關案例被實際取用；新任務功能測試，對照有/無經驗和適用限制 | CONTROLLED_TRANSFER_PASS / LOCAL_FUNCTIONAL_PASS / FULL_CI_PASS |
| P1-1 | 主動回饋事件、分層記憶檢索、技能專業深度、技術探索、任務池/覆盤 | 新工作階段重讀、無跨案混用；測試實際檢索與回饋行為 | P1-1a/b FULL_CI_PASS; P1-1c FULL_CI_PASS |
| P1-2 | 專家獨立協作與交接 | 有授權平台才做真子代理；獨立 QA、交接與整合證據；無平台標單 Agent 分工 | P1-2a LOCAL_ROLE_CONTRACT_EXACT_CI_PASS; P1-2b SKILL_CASE_CONTRACT_EXACT_CI_PASS; P1-2c READY_TASK_DISPATCH_CONTRACT_EXACT_CI_PASS; RESTRICTED_B003_HOST_TOOL_EXACT_CI_PASS; OPTIONAL_LOCAL_INFERENCE_NOT_RUN |
| P2-1 | 隔離合成完整系統：前後端、資料庫、權限、後台、預約、復原 | 可操作成品、端到端功能及安全測試 | P2-1a/b/c/d CONTROLLED_FUNCTIONAL_PASS; REAL_CHROMIUM_DOM_PASS; CLI_MIGRATION_RESTART_PASS; FULL_CI_PASS; MANUAL_UAT_NOT_RUN |
| P2-2 | 未見題獨立前後測、語意蒸餾、必要跨平台同步 | 等模型/工具/資源條件、獨立評審、保留失敗；只有需要且授權才同步 | P2-2a CONTROLLED_TRANSFER_AND_EXACT_CI_PASS; P2-2b DISTILL_EXACT_FULL_CI_PASS; P2-2c DISTILL_EXACT_FULL_CI_PASS; P2-2d DISTILL_EXACT_FULL_CI_PASS; TRUE_HOLDOUT_NOT_RUN |

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


### 2026-11-14｜P2-1b 設備借用生命週期（第一增量，測試結果待核）

**已核前置：** Draft PR #8 起始 04bbf07e015bf16f431eb5d8e5e16db48bdb6cd1；CI 43568793377 completed/success；P1-1c source CI 43568659877 completed/success。延續 B002/P2-1a 與 TASK-CASE-001；不變更外部研究網站、正式 Release 或 main。

**本輪合成規格假設（非正式產品決策）：** 保留原 RESERVE=保留/借出合成語意；會員僅能取消本人 ACTIVE(RESERVED) 項目，管理員僅能標記歸還，整筆釋放、不可部分歸還、不新增實際交付狀態。兩個 terminal 狀態互斥且不可重開。原請求與決定保持不變，另存 lifecycle actor/action_token/owner/target_token/result；交易內依唯一目標約束只釋放一次。相同 actor/action token 及相同 payload 重播原決定，不同 payload 拒絕；已終止/查無/原始不足回 NOT_ACTIVE。本人從 session 決定 owner，不接受會員指定他人；管理員明確目標 owner，不能代取消或借用。原 Host/Origin/CSRF/session guard 保留，頁面顯示原決定、現況、成功操作者與 action ID，僅 ACTIVE 顯示對應操作。未知 SQLite 結果 503 要求唯讀核對，不自動重送。
- src/p21_equipment_site.py：commit 912230bb833f3b772a4708eb6fd255f847eeae8b，blob 78113d8b4b6791dc1c114b1cfc210dc159c382ad，已完整回讀比對。
- tests/test_p21_equipment_site.py：commit 0c0cbc3a93e05b2d5b014c8bb92d9933089af4a1，blob fd39c090affcfbe4094d3cc6d14b88656e487a06，已完整回讀比對。保留原六個測試，附加四個測試：取消/歸還/稽核隔離與重播、未登入/越權/CSRF/跨來源/原不足與 token 衝突、8路 cancel/return 競爭預期只一成功、故障注入回退與缺庫唯讀/不自建。這些是已提交的測試條件，尚非實測 PASS。
- 原有資料庫不做隱式遷移。此候選僅新建獨立合成 DB；舊 schema 啟動/生命週期讀取拒絕，禁止覆蓋舊檔。稽核目前只有成功操作 ledger，尚無時間戳、失敗審計、完整生產稽核政策；沒有實際出入庫、部分歸還、外部部署或真實個資。
- 檢核命令：python -m unittest discover -s tests -p test_p21_equipment_site.py -v；本輪尚無本機執行證據，CI source-only 43570995375 先前 in_progress，新增測試版本 exact CI 待取，禁止用舊版測試或歷史 PASS 替代。瀏覽器政策阻擋未解除；revision-aware 任務池完整演練、真實獨立 Agent 未執行。下一輪先查最新同版本 CI、修復再處理上述缺口。

### 2026-11-14｜P2-1b 第二增量｜故障復原與命名空間驗收

- 起點：PR #8 head 3365297f731afdd7dba2f31508fcb744b6b4c746；CI 43571054944 completed/success，已回讀 verify job 132375323523 的 Offline unit tests、品質安全守門及其他步驟。0c0cbc3 的 run 43571017490 cancelled，不作成功證據；後續含同程式/測試的 head CI 成功。
- 單 Agent 分工（非實際獨立子 Agent），以公開隔離合成程式為實作對象，原 10 個測試保留；tests/test_p21_equipment_site.py commit 4f3e8d9602d0b71ac835cbae0cb603375663ebf1，blob da0ddb42412a1b991bdf17e7aead81e11ca66c64，新增 test_actor_and_owner_token_namespaces（相同 target/action token 的不同 actor/owner 並行、重播及 admin payload conflict）、test_unknown_after_commit_read_only_reconciliation（cancel/return 真交易完成後注入 OperationalError，HTTP 503；GET 對帳無二次 release、庫存零、ledger 唯一且資料庫 bytes 不變）、test_legacy_schema_refuses_lifecycle_without_mutating（舊 schema 避免隱式重建及寫入）。新增測試已遠端回讀，CI 43571651587 exact-SHA CI in_progress/pending。未另聲稱本地執行或瀏覽器 DOM 驗收；故障注入為 synthetic，不是實際網路故障。
- 新發現（靜態原始碼核對，尚未重現）：release 在找不到 ACTIVE 目標時直接回 NOT_ACTIVE，沒有保存負向 token 決定。若先對不存在的目標操作，之後同 owner/target 被建立，再重送同 token 可能轉為成功，與原「相同 payload 重播原決定」契約不一致。先用新合成回歸重現，後續保留成功操作互斥、拒絕記錄和獨立唯讀對帳；不以新測試代替修復。舊 schema 測試只驗證拒絕保護，不等於顯式遷移完成。尚無真實資料、真人 UAT、外部部署、模型自治評測或正式 Release。 

### 2026-11-14｜P2-1b 第三增量｜拒絕決定重播與顯式舊庫遷移

- 起點：PR #8 b9412a02a6b0ebe8f63eecdcafe160f37fc101d8，CI 43571713215 completed/success，保留原13組設備網站測試。現階段僅 Agent 候選分支及暫存合成資料。
- RED：將前版 Store initialize/reserve/release 原方法摘錄至本機隔離暫存 SQLite，取消（member）與歸還（admin）各自重現 NOT_ACTIVE → 建立原本不存在的 4 件借用 → 同 token 變成 CANCELLED/RETURNED、reserved=0，而應仍 NOT_ACTIVE、reserved=4。不是遠端失敗 CI，勿冒稱整個舊版測試套件執行。
- FIX：src/p21_equipment_site.py commit 68206d17298303fa414e3742023cb94677f0989d, blob e09024bf973623f0a664012853c2af279fa72685。選擇獨立 action_attempts (actor,action_token) 的完整合法決定及 payload，保留 lifecycle 成功狀態 (owner,target_token) 唯一約束；同 token 不重新判定、不改原結果，相異 payload 400；庫存、成功 ledger 與新決定同一交易。合法 NOT_ACTIVE 409 也持久化；未授權/非法輸入不當作有效業務決定。dashboard 顯示登入者自身操作決定，UNKNOWN after commit 以唯讀對帳，不自動重送。舊資料庫在正式寫入/生命週期查詢拒絕；原始 basic view 仍可唯讀查看舊庫。
- Migration：兩種原始 user_version=0 合成 schema（P2-1a 兩表、P2-1b 三表）均支援，先停所有舊 writer，明示離線確認；只讀來源 snapshot、integrity_check、表結構、每列合法性與庫存和有效借用相符；保留 requests/lifecycle 歷史、成功 token 決定，寫入同目的檔系統暫存 v1，再完整回讀對帳，以 os.link 排他建立新路徑，不覆蓋來源/既有目的檔。故障 before publish 不留可用半成品；只新增候選庫，不自動啟動/cutover。原來源檔是切換前的回退依據，切換後若新版已有新寫入必須先對帳，不得直接退回舊檔而丟失資料。拒絕 WAL/SHM/journal、未知版本與非合成格式。舊版從未保存的拒絕決定不可追溯；遷移後勿重送舊未明 token，先依已保存狀態唯讀查核。未測驗 power-loss durability 或 Windows 檔案系統；無真資料、正式服務或資料庫寫入。
- 合成使用入口（停止來源舊程序後）：python -m src.p21_equipment_site --database NEW.sqlite --migrate-from OLD.sqlite --confirm-source-offline 。成功只輸出版本/筆數；確認新庫完整性/庫存/歷史後另行啟動候選站：python -m src.p21_equipment_site --database NEW.sqlite 。未知發布結果先唯讀確認目的檔及內容，禁止覆寫或重送。CLI 完整進程測試仍待做；僅 local Store methods 已實測。 
- GREEN 本機：將修復後完整 imports+Store excerpt 從遠端原始碼轉錄，字元/bytes 13780，FNV-1a c555baa8 與遠端一致；本機 py compile 與 6/6 smoke groups PASS：兩種拒絕重播及新 token 正例、8路拒絕競寫/rollback/actor 隔離、兩表遷移、三表歷史成功重播及庫存、offline confirmation/故障回退/no overwrite/invalid inventory/version/sidecar、雙路遷移排他建立。驗證舊庫 bytes 不變、新庫庫存及紀錄；此為 Store 層實測，非整 repo 或 HTTP/瀏覽器完整驗收。
- tests/test_p21_equipment_site.py source+test commit 64a5f2ed8fe5dff429fe38d8edf191c6532b7c51, blob 594e3728837608007c4a92046889c5d679b84a5f。新增3項 HTTP 拒絕決定/失回應/競寫與5項遷移正反測，共21項，原13項未刪，完整 source/test 遠端 blob readback。CI 43576453447 completed/success；不以舊版成功取代本版。 
- CASE P21-CASE-003｜observed (Store local): 冪等契約必須包含合法負向決定；分離 terminal state 與 all accepted action decisions，以 actor 級 token/payload 衝突驗證、原子交易、唯讀對帳避免歷史請求在後續狀態變化中重新執行。資料遷移用原始檔保留+明確離線+快照檢查+新庫稽核+排他發布，不能把版本欄位變更當遷移完成。案例為公開合成訓練紀錄，不聲稱自治模型或獨立專家已驗證。下一步跨階段 revision-aware 工作台演練及允許環境的瀏覽器驗收。

### 2026-11-14｜P2-1 跨階段完整演練：報表需求修訂、交接、復原與重驗

- 起點：Draft PR #8 a16cd7234f529815c9ca670b62c7aa7005248627，CI 43576629567 completed/success；不重做既有設備網站及遷移。使用公開合成資料及 CI 暫存 SQLite；單 Agent 依角色分工，自行制定兩版訓練需求（非使用者正式產品核准），不是獨立模型或人類驗收。
- System Lead/Architect：R1 報表僅有效借用數量、會員只看自己、管理員加總、唯讀；R2 保留 R1 並新增取消/歸還/不足的數量、登入者自身 NOT_ACTIVE 次數、管理員專屬全庫存。使用 Store.view 單一唯讀 snapshot，庫存一致性與資料隔離。沒有新增 HTTP endpoint 或正式產品功能。
- Developer：src/p21_equipment_report.py commit 08fc8098763fa19ee99eb2b5ae62955f0e2cf584 blob ff4a738918fc07eab95b240a59d234053d08228d。report_v1 是刻意保留的可執行基線，report_v2 依新需求新增狀態統計及權限範圍；實際 Store reserve/release 產生 fixture。三角色 v2 驗收：member active=2,cancelled=4,returned=0,insufficient=0,denied=1；member2 active=1,cancelled=0,returned=3,insufficient=8,denied=0；admin active=3,cancelled=4,returned=3,insufficient=8,denied=2,stock=10,reserved=3,available=7。會員沒有整庫存欄位，未知 actor 拒絕，缺庫不建立，設備資料庫 bytes 不變。報表函式本身沒有登入認證，呼叫者須由既有認證邊界提供 actor。 
- 實際工作池及交接演練：建立 intake/spec/arch/plan/impl/qa/security/deploy-plan/activate 九項相依任務，另有獨立 inventory-audit；R1 逐階段交接並回讀實際產物內容及 dependency ID；report_v1 真功能驗收 PASS。子程序實際 start deploy-plan、保存 staged-plan.json（舊 implementation/qa IDs）並 exit 0，不作外部部署。修訂 intake 至 r2 同時使 9 項任務失效；獨立 inventory-audit 仍 DONE/r1。明確另行 handoff 新需求，使六類舊下游產物 current=false；stale handoff、舊 worker finish/resume 皆拒絕。RECOVERY_REQUIRED 未解前阻擋上游；查核子程序 exit 0、回讀 staged ID 並移除隔離暫存檔後 recover；新 Python CLI 進程重新 review 再領取新任務。
- RED/GREEN：執行 report_v1 對新版完整字典驗收，確實 AssertionError（非合成宣告 FAIL）；task pool 記 FAIL、阻擋 QA；新 session 實作 report_v2，實際相同判準 PASS，再執行三角色精確字典、未知 actor、缺庫不建立與 SQLite bytes 不變測試。更新 implementation 及 QA、security、deploy-plan 交接；最終 9 DONE、1 activate PENDING（LIVE 未決）、1 failed_attempt retained、無復原阻塞；舊 implementation/qa artifacts 保留。測試內 role 流程均由固定可信合成測試驅動，非自治多代理。
- Learning Evaluator：實際使用 workbench_learning context 找回 B002-CASE-001，由 report_v2 使用原 Store.view read-only snapshot、庫存不變及一致性約束驗證適用性，記 cite applied；requirement_change/test_failure/test_fix 三筆事件保留 candidate，不將回饋自動升格。history 回讀確認事件及 citation；未將此合成政策當永久個人偏好。
- QA/SRE：tests/test_p21_cross_stage.py commit 9adf5634765b88830d9426c6dd83da1f82b45959 blob f7d5857d3ecd00cace677e8cdd8808481559a338，source/test readback verified. Exact-SHA full CI 43605726496 verify job 132479932899 completed/success；原始 logs 2026-11-14T14:37:07Z 明列 P21-CROSS-STAGE: v1 accepted; 9 invalidated; stopped worker recovered; v1 rejected on v2; v2 accepted; 9 DONE; LIVE blocked; 3 feedback events; B002 case applied；test_full_revision_handoff_recovery_and_revalidation ... ok；Ran 330 tests in 36.170s / OK；Candidate quality baseline and safety gate success. 全部證據為遠端 CI 實際執行，不聲稱額外本機執行（本機 git DNS 不可用）；無真人資料或真實外部操作。
- **P21-CASE-004｜observed｜需求變更後的雙相依鏈與重新驗收**：task revision/state 及 artifact dependency/current 分別有效，但不是同一交易；確認來源變更後兩者皆需修訂並回讀，不能只拿任一 PASS 當施工依據。曾執行但失效 worker 先核實實際停止、盤點部分成果，再 recover；保留舊 PASS 和 FAIL，使用新 revision/session、實際新版測試及最新產物重驗，獨立已驗證工作不重做。適用於本機單工作台合成工程，未驗證中途雙索引同步中斷的自動復原、外部程序停止/寫入回退、真正多 Agent、跨平台、正式部署或真人 UAT。此案例記原訓練主檔，非正式政策自動升級。下一步設備瀏覽器/CLI smoke，之後陌生任務工程遷移。

### 2026-11-14｜P2-1 跨階段一致性：雙索引原子修訂與中斷復原

- 起點：Draft PR #8 f1106ed027b76cf0144f39ebe528367cd205977f，CI 43605933260 completed/success。沿 P21-CASE-004 實際查核同一 SQLite 內 task_pool / artifacts 不同交易的風險，僅隔離合成工作區及本候選分支，未碰使用者私人 DB、正式專案或部署。
- RED：tests/test_workbench_revision_sync.py 實際啟動子程序，以舊 standalone revise 或 handoff 提交單邊後 os._exit(23)。task-first：task revisions 更新、3 項失效，舊 requirements/spec 仍 current、architecture context READY，甚至可重新 handoff 舊內容；artifact-first：spec 過期但四個 task 仍 DONE。原始 CI 日誌兩個 REVISION-SPLIT-RED marker 證實，非純靜態推測。
- 修復：src/team_workbench.py blob a923db7a9e5761b416e7efbbe0a004cb088b6ba1 提取 _handoff_in_transaction；src/workbench_tasks.py blob e58d862dd16e4e364b53f8ece12f918eb025fc52 在 revise 增加 requirement={expected_artifact_id,content,source_ref}；同一 connection/BEGIN IMMEDIATE 核對 task revision 與当前有效根 requirements ID，確認唯一 change session、DAG 合法性，寫入 requirements、task revisions/失效狀態與 root REVISE event 的雙 artifact IDs；任一錯誤全部 rollback。revision-status CLI 以唯讀 snapshot 查 COMMITTED / NOT_OBSERVED、still_current（僅對應根 revision 與最新需求）。不自動重試。已更新完整跨階段案例採用新路徑。
- RECOVERY：兩種既有 split 狀態皆以重新核對兩索引及獨立確認 R2 合成來源，使用當前雙版本及新 session 原子修訂，不猜測哪個索引是真理、不抹除歷史。提交前於 artifact INSERT 後真實 os._exit(23)，兩側保留舊值、integrity_check ok；DB trigger 注入 task event error 同時回退 artifact/revisions/history；完成提交後 os._exit(23)，唯讀 receipt 確認 COMMITTED、bytes 不變，舊版本重送拒絕。四路競爭僅一個 commit，錯 artifact ID/空內容拒絕。
- QA：新增 tests/test_workbench_revision_sync.py 9 項（blob e70731ed46129e74186e55e8e0ae2f2c8576ad2d）；更新 tests/test_p21_cross_stage.py（blob 308c79c91cdbb31c2ed1bf2f8764cce688edb2a4）。Exact code/test head f6ad1e35eaef281a09eec3ce102fffd2e1c35eec；CI 43606395473 job 132481951934 completed/success，raw logs 9 tests ... ok；REVISION-SYNC-GREEN: combined revision, stale guard, receipt, revalidation；兩個 REVISION-SPLIT-RED markers；P21-CROSS-STAGE marker 與 9 DONE / LIVE blocked 保持；Ran 339 tests in 38.776s；品質安全守門 success。較早被取消的 run 43606348140 不作通過證據。本機 GitHub DNS 不可用，沒有聲稱本機整 repo 測試；實際執行證據為 CI。
- 操作手冊 docs/TEAM_WORKBENCH.md blob 9650577e9ee463e1065a65a7b0b6b376ca4a7fa1，明確 root requirement revise+requirement、receipt 唯讀回讀、已 split 的人工來源確認流程及限制，readback verified；guide head 433e7ac53421016d0107d3749e16741bbc27eb1e CI 43606430195 in_progress at this read。
- **P21-CASE-005｜observed｜同資料庫的相依索引變更應原子提交，未知結果先查憑據**：雙版本防競寫，狀態／產物／事件同一交易，使用實際程序退出與錯誤注入驗證，不只測正常路徑；已存在的不一致狀態不能由最新日期或較大 revision 推測正確需求，須獨立確認來源再用新修訂恢復。此為可信合成工程案例，非獨立 Agent 盲測。限根 requirements，standalone API 仍可繞過，尚未全域強制或原子綁定每階段 handoff/finish；未證實跨資料庫、外部服務、舊版混用、Windows/斷電或真正獨立 Agent。下一輪優先設備 UI/CLI 完整實戰及陌生任務經驗遷移，必要時再補 opt-in 強制綁定。

### 2026-11-14｜P2-1b 候選：任務—artifact 版本綁定

- SOURCE_VERSION: PR #8 基準 e3b364ba782c4da52d054c1d0ff9911576b20bbd；保留最新 CLI/瀏覽器工作及 P21-CASE-005 歷史。公開根需求既有 task pool 的 standalone 覆寫拒絕；新增明確 bind-artifacts，核對完整任務 revision、根 ID、catalog 依賴與 DAG；重開受影響 task，保留無關分支及歷史。綁定 PASS 與 artifact CAS/前置 ID 同交易，producer 非 DONE 則產物失效。根修訂只走 combined revise。
- TEST_PLAN: tests/test_bound_artifacts.py 七項負面及跨階段測試；保留舊版本 split 重現，改用歷史寫入方式模擬。基準後 CI 需以新 SHA 讀回，未確認前不得稱成功。
- LAST_VERIFIED_STEP: 基準與正式主檔讀取；候選實作、測試尚待新 SHA CI。NEXT_ACTION: 查 CI 原始日誌與安全守門，修正實際失敗；補拓撲擴充及真正 stage PASS 程序退出。
- BLOCKERS: 綁定須明確採用；受信任新版 API，不防直接 SQL/舊程式混用，不保證語意正確、外部同步或真 Agent 能力。WRITE_OWNER: lily4318；SYNC_STATUS: 原候選分支，不合併 main、不 Release、不改外部專案。

### 2026-11-14｜P2-1d 設備網站真正瀏覽器、CLI 遷移及端到端驗收

- 起點：Draft PR #8 898ea184e31a62403e6ecfa6124bb3566381f1f1，CI 43606595848 completed/success；僅公開合成設備網站與 CI 暫存 SQLite，未碰真人資料、私人工作區、外部服務、正式部署或 Release。本機 Chromium 實際探測 ERR_BLOCKED_BY_ADMINISTRATOR，GitHub DNS 不可解析；採原有 GitHub Actions Chromium 環境，非本機全測或人工 UAT。
- RED：新增 src/p21_equipment_browser_test.py（blob efceea5361fed81d92355ce6633ebf2630a14046），以本機 loopback Chromium/Node CDP 真 DOM 表單事件與頁面導航，接入 src/website_intake_browser_test.py（blob b9c96e177aba41dea7d5a7a78d49c1971fc125f9）原 CI 瀏覽器入口。基線 f7112614f79de0e8ca6a4327c1796a5c861047c0/run 43606845560/job 132483410360 原始日誌：既有六個 intake browser case PASS，equipment 的 native login 出現 Invalid origin。含 CLI 的 e3b364ba782c4da52d054c1d0ff9911576b20bbd/run 43606931057/job 132483727720 同樣失敗，但 343 unit tests OK。先前 HTTP tests 人工指定 Origin，無法發現瀏覽器實際表單政策不相容。
- FIX：0874b68d75b3c1bf00b2c309cfa52d70a5eade02 改 Referrer-Policy: no-referrer → same-origin（原生 POST 的 Origin 可能受 no-referrer 影響，未直接記錄原封包的 Origin 值，不宣稱已捕獲 null）；仍拒絕非完全匹配的 Origin，保留 Host/CSRF/session guard，不放寬授權。1fab759a4dcff17071a6c1c40768a66b1415d580 增加獨立負向測試，null/缺失/外部 Origin 拒絕、有效 same-origin 成功。src/p21_equipment_site.py blob 723cbd45c6d11792e38aa35732b791679950f7a0，tests/test_p21_equipment_site.py blob a105f1b802cb62cfe128b27a8d7e7dade8ddcae3。
- CLI：tests/test_p21_equipment_cli.py（blob 80690617f95277257a4339c55a1602b250ccf3d8）四項以獨立 Python CLI subprocess 實際執行；首次 init/缺庫啟動拒絕/已存在不得覆寫；兩表、三表 legacy → v1 遷移、啟動/登入/唯讀 admin 查詢/停止、原檔 bytes 不變、可從保留舊快照重新遷移；錯參數/缺來源/目的檔存在拒絕；新增借用後重啟新版、舊 session 失效、資料及庫存持久化（舊 3 件、新 5 件）。原始日誌 P21-CLI-CUTOVER 與 P21-CLI-RESTART markers；前置回退限未有新版業務寫入，驗證保留資料快照與再遷移，沒有執行歷史 legacy server binary；新版已有寫入時不得直接退舊檔。
- GREEN：並行任務—artifact 綁定提交整合後 head 0f4f536d4c3daf05304add614d24e2563b42b1ef，已回讀保留上述 5 blobs 及並行工作歷史；CI 43607088233/job 132483961970 completed/success，raw log P21-EQUIPMENT-BROWSER: {"status":"PASS","actual_browser_dom_events":true,"roles":3,"stock":10,"reserved":0,"manual_uat":false}；三角色原生登入/錯誤登入拒絕、借用/取消/歸還、獨立會員資料隔離、管理後台及登出/非法數量/庫存不足測試均成功；4 CLI tests 和 test_native_form_referrer_policy_and_strict_origin ... ok；Ran 351 tests in 39.918s；品質／安全守門 success。取消的 43607050068、43607070881 不算成功；最新整合 head 全 CI 為驗收證據。沒有把並行綁定功能冒稱本輪獨立開發。
- **P21-CASE-006｜observed｜HTTP 正測不能替代真正瀏覽器，遷移成功不能等同可逆回退**：原生瀏覽器安全政策影響標頭與實際流程，應先 RED 背景重現，再保留 fail-closed 安全邊界做最小修復，並回歸正常表單和非法來源。用真正瀏覽器 DOM 與獨立 CLI 程序驗證角色、持久化和資料完整性；遷移與啟停、切換、寫入後復原分開驗收，不以保留舊檔作為 post-write rollback 證明。CI 實際可信合成測試不等同人工 UAT、Windows/斷電、跨資料庫或獨立真模型盲測。下一輪優先移轉工程經驗到陌生任務，保留 concurrent binding 進度及其限制。

### 2026-11-15｜P2-2a 文件版本審閱系統：受控工程經驗遷移及案例庫匯入

- 起點 Draft PR #8 fd71076758d4873344145eff93581824eb466d7d / CI 43607268933 success。自行制定公開合成 CLI 文件審閱需求，非使用者正式產品決策。編輯者新增 immutable version、審閱者核可當前指定版本、發布者只變動本地已核可版本指標；舊內容不覆蓋。可信本地 actor 標籤不是認證服務，不得用於真人文件或實際外部發布。
- 架構與實作：src/p22_document_review.py blob 948deb53c5f0c8abd4b6f17d23eac4af987998a7，commit f747eea3a6d668270e67d5ad0cc887b0856de352；versions/state/approvals/decisions SQLite schema，BEGIN IMMEDIATE，expected revision、actor scoped token+exact payload、合法正負決定與狀態同交易、mode=ro readonly receipt；init 排他、CLI init/action/receipt/snapshot。Baseline 是同作者刻意移除 exact revision approval、negative receipt、atomic commit 三個控制的 ablation，保留正常流程及角色檢查，不是實際無記憶獨立模型。
- 實測：tests/test_p22_document_review.py initial blob ebb58b96ad8cd8e3053666ad76c12ce299157b01，commit 36c03547b84a43c5c41c9aa93388c31839f56041，CI 43666793523 job 132667997029 completed/success。相同十項規格預期值：baseline 6/10，improved 10/10；baseline 失敗 stale_approval / denied_replay / future_revision_replay / fault_atomic，另外 happy/competing_edit (6 workers)/role_guard/token_conflict/readonly_missing/published_history 兩版皆過。原始日誌 P22-TRANSFER marker；新增三組整合測試 ... ok；Ran 354 tests in 37.877s。此為同作者受控方法比較、規格導出 oracle，不是獨立評審、模型增分或陌生私有 holdout。
- 學習與交接：在暫存工作台明確匯入先前 master P21-CASE-003/005/006，實際 learn.task_context 檢索，讀 requirements/spec/architecture/plan，採用 003（否定結果重播）、005（原子 state/receipt），006 判定 not_applicable（此次無瀏覽器／遷移）；保存 citation、實作/QA/security/deployment-plan handoff，兩筆 RED/GREEN feedback 保持 candidate。原始 P22-LEARNING marker 3 retrieved, 2 applied, 1 not_applicable, 2 feedback。P22-CLI：實際子程序完成 edit 後 os._exit(23)，其他程序只讀 receipt、資料 bytes 不變，後續核可和本地發布可在新程序驗證。
- 可重用案例庫：src/workbench_learning.py commit e63dc55a68d698abb5a806d919e65cccc0bc3239 blob 4a23d25f0de3a9fb5421753ed4cfbb636dde50da；預設 CASES 仍 B001/B002，新增 TRAINING_CASES 三份已驗證 P21 案例的標籤/適用限制/來源 CI；需明確 setup(include_training_cases=True)，不自動升格 feedback、不變更使用者私人 DB。CLI 在已授權/已初始化工作區可使用 JSON 參數 {"include_training_cases":true}，命令 python -m src.workbench_learning setup --workspace <workspace> --input <json-file>；同一顯式 setup 可重複而不覆蓋既有或退休案例。整合回歸測試 blob da6cb92fe8a27220838b844cf81df70549a70d76，候選 bfe4299a99833d62c0f6586e8207281a72cb9053 CI 43666877892 in_progress, unit success at this read；default 2→explicit 5、重複匯入、非 boolean 拒絕及實際檢索。新版本驗收不可借用初版 CI。
- **P22-CASE-001｜observed｜版本特定核准與持久否定決定的受控遷移**：新資料版本不繼承舊核准，認證/作者角色與資料版本/操作狀態分開；合法的否定結果也需持久化，未知提交先只讀查核；狀態與稽核事件在同 DB 交易。相同規格 oracle 對 baseline 及 improved 執行，保留反例及已過項，引用不適用案例的理由。適用本地文件審閱 CLI 與相似狀態工作流；不聲稱多文件、網路認證、外部發布、真多 Agent、語意蒸餾或盲測成效。下一步改做資料匯入/驗證/轉換等不同架構之工程任務，擴張方法遷移廣度。

### 2026-11-15｜P2-2b 檔案匯入與可重現轉換（候選，尚待 CI）

- 起點：Draft PR #8 a26bd595115bfb9b425db399c8c91281000484c3，CI 43667013361/job 132668532801 completed/success；原始日誌 354 tests in 37.160s/OK、P22-TRANSFER、P22-LEARNING、P22-CLI，原品質守門成功。先前 opt-in 匯入已包含於同版通過。
- 自行設定公開合成文具數量 CSV 任務（非使用者正式產品規格）：固定 header、唯一 R 四位數 ID、三類固定類別、1–999 數量、UTF-8、64 KiB／1000 列上限、整批拒絕非法資料；固定測試 oracle 為 folder=7,paper=5,pencil=0, rows=3。這不是 SQLite 狀態機，也不是獨立前後測或模型能力增分。
- src/p22_file_intake.py commit 44fdba9d35c1950b671ffb3fa4a4943a71f5c1e9 blob b9dcf906ecabd9df9d25d95f58c323dd0a097f07：解析整份資料後 canonical JSON、input/result SHA256、單一 bundle 保存內容與憑據；同目錄暫存/檔案 fsync/排他 hard link，不覆寫既有輸出。reconcile 僅讀且重新計算完整 bundle；COMMITTED / NOT_OBSERVED / CONFLICT，unknown 禁止盲目重送。只適用受信任本地目錄、穩定輸入及支援 hard link 的檔案系統；未驗證斷電、Windows、敵意目錄或外部系統。
- tests/test_p22_file_intake.py commit 9bc7b39cf9576e3e4f34492e80cd8ff251ac27c0 blob af3cae62fed16fc338ac9cf6924f54e5ec25d483，六組方法：精確 oracle/可重現、14 個無效輸入拒絕、唯讀衝突及發布前故障、八路競寫、獨立程序退出後重新查核、真實工作台匯入與引用交接。預計 P21-CASE-005 僅遷移原子可見性原則（非直接套 SQLite），003 無 actor decision ledger、006 無 browser/migration 判不適用；回饋保持 candidate。程式與測試已由遠端完整讀回；CI 43667672400 pending at check，所有新測試結果仍未確認。不得標為 P22-CASE-002 observed 或已通過。
- WRITE_OWNER: 原 Draft PR #8 候選分支。沒有改 main、正式發布、研究網站、真實資料或外部服務。

### 2026-11-15｜P2-2b 功能驗收、復原邊界與工程蒸餾

- 原始候選為 088c8264d4e622ba3bb09e8212e220c91ed05caf；先前 CI 43667672400 cancelled（無 job），非失敗或成功證據。完整 CI 43667714699 job 132670734319 completed/success，下載完整原始日誌（初次未完成時暫時 404，完成後讀取成功）。六個 test_p22_file_intake 方法皆 ok；P22B-LEARNING: 3 cases considered; 1 principle transferred; 2 not applicable; feedback candidate；P22B-FILE-RECOVERY: process exit after publication; exact bundle reconciled read-only；Ran 360 tests in 39.988s / OK；所有 workflow steps success（browser、privacy、policy、quality safety gate 均成功）。無實際功能失敗須修正；Node.js 20 actions deprecation warning 留作維護，不放寬守門。
- 額外本機隔離實測：將完整 src/p22_file_intake.py 4471 bytes 轉錄至暫存目錄，git hash-object=b9dcf906ecabd9df9d25d95f58c323dd0a097f07 與遠端 blob 相同。兩份不同 CSV 同時發布到同一 output：1 PUBLISHED、1 EXISTS；唯讀分別 COMMITTED/CONFLICT，輸出不變。獨立 subprocess 於 os.link 前或實際 link 後、finally 清理前 os._exit(23)，分別 NOT_OBSERVED/COMMITTED，兩次殘留 staging 內容均完整且查核不改變；僅清除測試自有暫存檔。輸出符號連結拒絕，來源 bytes 不變。不是整 repo 本機測試，未驗證 power-loss/Windows/非本地 FS。
- **P22-CASE-002｜observed｜來源綁定的不可覆寫檔案發布與唯讀復原**：先整批驗證，再產生 canonical output，將原始輸入 hash、內容與結果 hash 放入同一可驗證 bundle；單一檔案排他發布避免資料/憑據分離。發生未知結果先對原始輸入完整重新計算並比對 bytes；區分 COMMITTED/NOT_OBSERVED/CONFLICT，禁止覆寫與盲目重送；暫存檔殘留不能當作發布失敗，先驗證其來源、使用及狀態才處理。遷移 P21-CASE-005 原子可見性原則，非直接套用 SQLite 交易；P21-CASE-003/006 不適用。適用穩定、可信本地目錄及支援 hard link 的檔案系統；不聲稱敵意路徑防護、來源並行修改、斷電耐久、外部服務或自治多 Agent。來源：上述 exact CI 與獨立本機故障注入。
- 可重用經驗庫：src/workbench_learning.py commit e66720d6e45e68804f1bfde7c84fc5a8f0dcfa10 blob 8d9531f7e1c2595bf44952a0fbe45df1caf96dbe，explicit opt-in TRAINING_CASES 新增 P22-CASE-002，預設 CASES 維持 2；不寫私人工作區，不自動升格 feedback。tests/test_p22_document_review.py blob bdc859c5555223b2edf7133c6833438d529fc44e 更新 explicit corpus 6 筆的預期值（不刪原驗收）；tests/test_p22_file_intake.py blob fe43243f95887ccd365400a042cd16c712066dba 新增 3 組（不同來源、真正發布邊界程序退出、舊 5→6 案例增量匯入/保留舊 ID/跨程序檢索），code/tests head fe48c8b5f7983022b3a581980c404456fc824477 遠端回讀確認。新 CI 尚未核實，不將預期 363 筆當成功結果。curation 是證據導向的運作案例整理，不是獨立模型語意能力評測。
- WRITE_OWNER: 原 Draft PR #8 候選分支；未修改 main、外部研究專案、部署或正式發布。下一步讀最新 exact CI，驗證案例庫匯入及新測試，保留歷史。

### 2026-11-15｜P2-2b 蒸餾整合驗收及 P2-2c 跨架構報表匯出（新候選）

- P2-2b exact code/test head fe48c8b5f7983022b3a581980c404456fc824477 / CI 43667923887/job 132671442278 completed/success（363 tests in 40.489s）；latest docs-integrated head 989244c889c307dac676399e02fba9711794126b / CI 43667964691/job 132671715291 completed/success（363 tests in 38.328s）。完整原始 logs 回讀成功，P22B-DISTILL 舊 5→6、原案例/ID 不變、跨程序檢索，P22B-CUTOVER link 前 NOT_OBSERVED/後 COMMITTED、staging bytes verified，P22B-FILE-RECOVERY；所有 workflow steps success。無實際 CI 失敗需要改動舊核心。預設 2 筆、explicit opt-in 6 筆，P22-CASE-002 已驗證檢索；案例不是權限或模型能力證明。
- P2-2c 自訂公開合成需求（非使用者產品核准）：從本地 SQLite 既有資料庫用 mode=ro/query_only + BEGIN 讀單一快照，檢查唯一 metadata revision、1000 列上限、SYN-四位數 ID、類別/狀態/整數數量；R1 只輸出 completed quantities，R2 再加各狀態筆數；不輸出逐筆 ID 或 pending/rejected 數量。獨立於實作的固定測試 oracle：paper=5,folder=7,pencil=0；complete=2,pending=1,rejected=1。選擇 ZIP 而非 CSV→JSON，將 report.json 與 manifest.json 固定內容/順序/時間戳，manifest 含 canonical logical snapshot SHA256（非原始 DB 檔 hash）、報表 hash、source/policy revision。排他 hard link，禁止覆寫及盲目重送；以相同來源/政策再計算完整 ZIP 比對。來源不可讀/版本不符時拒絕查核，不誤報 NOT_OBSERVED；不同政策需新檔，舊成果保留。快照時點一致，不保證發布時 live DB 未變更；hash 不等於匿名化；只做合成資料，可信穩定路徑，不做實際部署或授權認證。
- src/p22_snapshot_report.py commit 124c46289801bbe1485594316ecfd78f780f66a1 blob 92cf3188a0d00eb67f8cfba82f6db59136a53927；tests/test_p22_snapshot_report.py commit 5366ea6029dc8003ff80af20ed7d055d14c723c1 blob cdbe9ac119e2d8a72b170b0f3ed0a887c131f1a4。六組方法：固定 oracle/隱私欄位/可重現 ZIP；R1→R2 政策和來源 revision 改變；8 類非法來源及缺庫/未知政策；不同政策並行競寫與毀損；CLI 程序退出唯讀復原；實際 learning context/cite/handoff/feedback。擬採用 P22-CASE-002（單一檔案成品/憑據的原則，改成 ZIP）及 B001-CASE-001（SQLite 唯讀缺庫防護），P21-CASE-006 不適用，回饋保持 candidate。測試為同作者需求導出 oracle，非獨立前後測、真實多 Agent、外部系統或完整 requirement revision-aware task invalidation。新程式及測試遠端讀回，43668190276 pending/unverified；尚未宣告功能成功、未將 P2-2c 案例升為 observed。 
- WRITE_OWNER: 原 Draft PR #8 候選分支；main、Release、真人資料、外部研究專案與部署未動。下一步核實 exact integrated CI，再做必要修正與蒸餾。

### 2026-11-15｜P2-2c 報表功能驗收與新案例蒸餾

- Exact integrated head c1f5a605976925dd3ff281894f4e7ceb7be5fb2e / CI 43668235893/job 132672315245 completed/success；完整原始日誌回讀，六個 test_p22_snapshot_report 方法皆 ok，Ran 369 tests in 37.430s/OK，P22C-REVISION（R1 成品不符合 R2；舊來源 revision 拒絕；新來源獨立規格 oracle 檢查）、P22C-TRANSFER（P22-CASE-002 與 B001-CASE-001 applied，P21-CASE-006 not applicable，R2 正確），P22B-DISTILL 仍成功，所有 workflow steps 包含品質/安全/privacy/browser success。沒有實際失敗需要修改報表核心。
- 固定合成規格 oracle：R2 完成數量 paper=5, folder=7, pencil=0；complete=2,pending=1,rejected=1；資料庫原 bytes 不變，ZIP report/manifest 檔案內容和 CRC/邏輯 snapshot hash/報表 hash 匹配，重複輸出 byte-identical；舊 policy/不同來源 revision/競寫/毀損/缺庫與八類非法資料拒絕，程序退出後另一 CLI 唯讀對帳成功。範圍為受控開發者自訂規格與測試，非獨立模型盲測或真實營運。
- **P22-CASE-003｜observed｜雙版本綁定的可重現報表及資料最小揭露**：來源 revision 與報表 policy revision 必須分開；對既有本地 SQLite 以唯讀交易取得一致快照、僅匯出規格所需彙總；以固定 ZIP manifest 將邏輯快照 hash、報表 hash、兩個版本綁定；舊成品保留，新版排他發布，不將缺少/過期來源誤當 NOT_OBSERVED。未知結果需以相符快照及政策重算比對；舊成品不符合新政策不代表舊成品錯誤。將 P22-CASE-002 排他成品/憑據及 B001-CASE-001 缺庫唯讀原則遷移至 SQLite→ZIP。適用合作式本地來源與可信穩定路徑，不保證發布當下 live source CAS、沒有歷史快照的對帳、匿名化、敵意路徑、斷電或 Windows。來源：上述 exact CI。 
- src/workbench_learning.py commit d5cf02264b38bd05a8691c32aafeaee850c77fd7 blob 68543564c6263cf0e8a883f7ccb123fa6c0a6017：P22-CASE-003 加入 explicit opt-in TRAINING_CASES；預設 2 筆不變，擬由 6→7，無私人工作區寫入，不自動升格 feedback。tests/test_p22_document_review.py blob 3985b935ac9884a65a132a18cf1aba8095f6a226 更新完整 opt-in 7 筆預期；tests/test_p22_file_intake.py blob d7dcfe0cf1fbe32819948158295f0fbc79e0168b 固定歷史 5→6 fixture 不混入未來案例；tests/test_p22_snapshot_report.py blob 805eb91cd7a4dbf8b6ae534f1f7c26231d3980e1 增加 6→7 保留舊資料/ID、冪等匯入、跨程序檢索、無關查詢排除；另用 SQLite WAL 讀取中另一連線實際提交 R2 的測試確認 R1 快照一致而非 live CAS，驗證過期舊來源查核拒絕、R2 新報表。新測試尚未實際驗收，預期 371 tests 不計入通過。Code/tests head d4b1a86e7694d3bd84c74eaed65de2b1f71d65bf 遠端回讀；43668423715 in_progress/unverified。下一步核查 exact integrated CI，非自動 promotion。
- WRITE_OWNER: 原 Draft PR #8 候選分支；main、Release、外部研究專案、真人資料及部署未動。

### 2026-11-15｜P2-2c 蒸餾驗收與 P2-2d 版本變更的任務—Artifact—實際成品聯動

- Exact integrated head 193ed127b2a12ee8c31744c2fbf10f4666d6de45 / CI 43668465656/job 132673166596 completed/success；完整 raw logs 371 tests in 40.725s/OK，P22C-DISTILL 6→7 保留舊 ID/內容、冪等 explicit opt-in、跨程序檢索、無關查詢排除，P22C-SNAPSHOT 真實 SQLite WAL 寫者於 R1 讀取中提交 R2 且 R1 一致，P22B-DISTILL 舊歷史 5→6 fixture 仍通過；全部 workflow steps success。P22-CASE-003 可實際檢索，沒有既有 CI 功能失敗，不修改已驗收規則。
- 本次自訂合成情境：使用既有 src/workbench_tasks.py bind_artifacts/revise/revision_status/start/finish/recover 與 team_workbench current_artifacts，不新增第二套任務或 artifact 資料庫。根 requirements 存 source_revision + policy_revision + logical snapshot SHA256；同 source revision 不允許更動內容後假冒同一來源。明確 confirmed change 經既有雙版本原子 revise 使 intake/spec/arch/plan/impl/qa/security/deploy-plan 與 activate 重開，audit 獨立保留；RUNNING 被失效時擋 recover 前的上游工作。根要求 ID 決定 report-root-ID.zip，所有版本保持獨立且排他發布，舊 worker 無法將舊路徑接受為新 generation。QA 以外部於程式實作的固定 synthetic oracle 明確比較字典，錯誤回傳 FAIL 並保留紀錄；security 檢查允許彙總欄位，deploy-plan 再核對各前置 evidence root_id/zip_sha256 且 LIVE gate 保持未核准。所有 PASS 須經 bound finish 檢查 exact session/task revision/prerequisite artifact IDs；不是自動外部部署。
- src/p22_snapshot_report.py blob 4cc8830262148a211bc22ce759e255032e29b4d0 commit 9a643e6809f09fe2c424f7db493ced2979fda589：最小抽取 _publish_bundle，讓已驗證快照的 bytes 排他發布，避免先核對來源再重讀不同快照。src/p22_report_workflow.py blob ae51677d4b8adaf84d88d189a547d7bbc94bbf93 commit cc4734d72e0e274fddda1d13c12c186f2f854f58：新工作台 initialize、confirmed revise、verify、complete_stage，實際 ZIP 及 SHA 綁定。未知已有檔僅在明確 reconcile_existing=True 時唯讀比對，拒絕盲目覆寫；不保證檔案和 DB 原子交易，舊 worker 可留下舊 generation 成品但不能通過新任務驗收。要求來源/工作台穩定可信且合作寫者，外部修改沒有自動偵測，當前快照不等於 live-source CAS；generic API 舊程式/direct SQL 不受此專用流程強制。初始化多交易、部分完成需 review；不接管既有私人工作台或正式資料。
- tests/test_p22_report_workflow.py blob ec3d31f268b3625a137bd1fb76aae2588245d89a code/test head 39800776eb2979ce762f8f71fa379a584dd52596：四個實際功能測試方法（1）先改報表政策再改來源，三個 ZIP generations 依固定 oracle R1/R2/R3 重建，八階段重新驗收，audit 及歷史檔保留、LIVE blocked；（2）實際 publish 後注入 root revise，舊 worker PASS 拒絕、RECOVERY_REQUIRED，回讀舊檔後明確 recover 並重新產生新 root/hash；（3）未知已有檔不能直接盲目重送，明確 read-only reconcile 及實際錯誤 QA oracle FAIL 保留，新 oracle PASS；（4）同 revision 改資料拒絕，修訂新來源後復原，實際 retrieve/cite P22-CASE-003。前一測試提交 ba91a0a26fd8a1d53f73ada8e2b860ab6d192386 CI 43668788619 in_progress at check；最新 43668815796 pending/unverified。程式與測試已回讀，預期 375 tests 尚非 PASS，P22D-* marker 尚待實際 CI，未蒸餾新的 observed case。
- WRITE_OWNER: 只原 Draft PR #8 候選分支，main/Release/外部研究專案/真人資料/部署均未動。訓練是單 Agent 控制流程與實際合成程式測試，不是獨立子 Agent 或真實模型學習成效。

### 2026-11-15｜P2-2d 跨階段驗收及工程蒸餾

- Exact integrated HEAD 8639a359491b9eb923e64efa1db1f8c51b0d628b / CI 43668854174/job 132674236212 completed/success：完整原始日誌（220851 chars）回讀，375 tests in 38.045s/OK，所有 workflow steps success。先前 ba91a0a26fd8a1d53f73ada8e2b860ab6d192386 / CI 43668788619/job 132674032499 同樣 375 tests in 38.643s/OK；39800776eb2979ce762f8f71fa379a584dd52596 / CI 43668815796 cancelled，不計 PASS。沒有實際 CI failure 需修正。
- P22D-REBUILD：政策變更再來源變更，3 個實際 ZIP generations，R1/R2/R3 oracle 通過、舊 ZIP bytes 與三代 QA history 保留，所有 8 相關 stage/artifacts reaccepted、獨立 audit 保留、LIVE gate blocked。P22D-STALE：檔案成功提交後注入根需求修訂，舊 worker PASS 拒絕、明確 recovery 後新版成品與新 root/hash 綁定。P22D-RECOVER：既存檔明確唯讀比對，不盲目重送；錯誤 QA oracle 實際 FAIL、正確 PASS、後續閘門保留。P22D-TRANSFER：同 source revision 內容異動拒絕，P22-CASE-003 實際 retrieve/cite。均為單 Agent 自訂合成情境、真實程式執行而非真人或獨立模型驗收。
- **P22-CASE-004｜observed｜跨交易邊界的世代綁定、任務失效與安全復原**：root artifact 綁來源 revision、logical snapshot hash、policy revision；明確修訂時根需求與相依任務失效在同一工作台交易更新；舊世代檔案保留，輸出以 root ID 區分；任務 session/revision/prerequisite artifact IDs 與實際成品 exact bytes/hash/QA 綁定；檔案先成功但 worker 驗收失效時，保留舊檔與證據、明確對帳與復原後才生成新版，不能宣稱跨檔案／工作台 DB 原子性。適用可信本地受控流程，不等於自動來源偵測、通用 API/direct SQL 防繞過、分散式交易、獨立模型 QA 或斷電耐久。來源：上述 exact CI 43668854174。
- src/workbench_learning.py commit 57781cb67f24ec11e12b2a532f9eead8dccfabfe blob 7574a41d567586ef1f754142b3fc2c693aa07982：新增 explicit opt-in P22-CASE-004；預設 2 筆維持、預期 opt-in 7→8，不動既有私人工作區或自動升格 feedback。tests/test_p22_document_review.py blob 4b22cf46320cf23a902798ec25224b23592ea448 比對完整現行案例鍵；tests/test_p22_file_intake.py blob 86603b62d1b0bc06893d6286e5e7151b647d34a1 與 tests/test_p22_snapshot_report.py blob 12009ff268e4f6e83ca154750aaccddd3c4dca28 凍結歷史 5→6／6→7 驗收集合而非修改原期望。第一次更新後 PR head 暫時滯後，停止寫入並讀回分支 blob 及 PR head 相符後才續作，沒有盲重送。
- tests/test_p22_report_workflow.py blob bff74193d382af63f5f66b9880fd97e2ea6d72c3 head 1220f618e9ffc9bd812e7b31b83d6c1ca1416dac：新增 exact 7→8 case migration/ID/content preserved/idempotent opt-in/跨程序檢索/無關查詢排除，以及 real subprocess os._exit(23) 於 ZIP publish 後 task commit 前；預期唯讀 verify COMMITTED 但 impl RUNNING、QA blocked，明確 resume 新 session、舊 session refuse、只讀 exact reconciliation 後完成 acceptance 且 bytes 不變。這兩個新測試尚未實際 CI 驗收，預期 377 tests 不計通過；43669048037 pending/unverified。全部相關檔案遠端回讀成功。
- WRITE_OWNER: 只原 Draft PR #8 候選分支；main、Release、外部研究專案、真實資料及部署未動。下一步核實蒸餾整合 CI，再優先準備 P1-2 真正獨立執行評測；保留歷史與權限邊界。

### 2026-11-15｜P1-2 本地獨立角色呼叫準備（轉向真實模型，不冒稱已執行）

- P2-2d 蒸餾 exact integrated HEAD 90561afaa9b899fc0dc4796e0939e3427537a49c / CI 43669080334/job 132675094766 completed/success；完整 raw logs (221467 chars)，377 tests in 42.176s/OK，P22D-DISTILL 7→8、舊案例及 ID 保留、冪等跨程序檢索和無關查詢排除；P22D-PROCESS-CUT 真實子程序在 ZIP publish 之後 task commit 之前 os._exit(23)，檔案 COMMITTED、impl RUNNING、QA blocked；明確新 session resume、拒絕舊 session、唯讀對帳且未重寫原檔後完成驗收。P22D-REBUILD/TRANSFER/STALE/RECOVER、歷史 P22B/C 與全部 workflow steps success。前 code/test head 1220f618e9ffc9bd812e7b31b83d6c1ca1416dac / CI 43669048037/job 132674851163 同樣 377 tests in 41.381s/OK；無實際 failure。
- P1-2 執行環境查核：原 PR #6 HEAD 09c9f9d852ec7ab6a468dd241af72b87a40237cb 為 open draft，changed files 包含 llm_runner_preflight、provider evidence、dual source、requirements eval 等；PR #8 既有 src/llm_runner_preflight.py（blob ed613b323260761188ca0e24c3604308877b37bd）只稽核設定雜湊而不 inference，src/capability_execution.py（9956b59303c4fc66b2928ee93c59c351a755317b）只 prepare/ingest AST；docs/TEAM_WORKBENCH.md、docs/WEBSITE_HOLDOUT_EVALUATION.md、AGENTS.md、七角色檔及 agent-ci.yml 所讀適用節不提供實際模型執行授權。當前聊天工具 inventory 未見獨立 subagent/model inference 工具；本機 sandbox command -v ollama/codex/claude/llama-cli/docker/podman/bwrap 無，ollama/llama_cpp/transformers Python module 無，預設本地模型快取 dirs 未見，127.0.0.1:11434/1234 無可連線服務。僅限當前環境，不推定使用者 Windows 或其他私有環境。未讀秘密、未啟動額外服務、未下載模型、真實 inference=0。
- 自訂 P1-2 首個實跑入口：src/p1_local_role_runner.py commit fc9a9bde85245f89c595fc566a50c6309380472b blob dd40d6ccd2ab1d82e18e193df82b7e4a167cab8d。官方 Ollama API chat/tags/FAQ（https://docs.ollama.com/api/chat、https://docs.ollama.com/api/tags、https://docs.ollama.com/faq）核對。只連固定 127.0.0.1:11434，不經代理/redirect/remote endpoint；probe 只 GET version/tags，不推論；run 需明確 operator offline-local confirmation、已安裝非 cloud model tag + exact digest，只接內建 public B001–B005 packet，無 reference/gold、無真人/私人資料。七角色固定 DAG，分開 stateless chat request，QA 在 developer 前、只收到 lead 交接；其他角色接明確上游 handoff，不給工具，不執行輸出原碼。保存新私人目錄 packet/run/每 role request,response,receipt SHA、model tag manifest digest/version、時序及 token metadata；不完整/未知 response 保留現況、禁止自動 retry。此為實際模型呼叫介面，不是單 Agent 手工角色文字模擬，但本輪未呼叫；固定 DAG 不代表 autonomous routing，同一模型的分離請求不等於七個具自主工具的 Agent，local endpoint 與 digest 不構成獨立 provider 及 offline attestation，須使用者關閉 cloud 並隔離外網。角色擷取輸入有長度與 context 限制，真實模型可能截斷/失敗；不得假設所有模型可正確完成。
- tests/test_p1_local_role_runner.py commit c76630433a8d1dba5b92556e6d758e3a20109e95 blob 2c01e9064b796885f311b07bdc209be2ce24e715：三個 offline fake transport 契約方法（無明確同意、cloud tag、錯 digest 拒絕；7 次獨立 request、QA 盲於程式、exact receipt hashes、無 tools；遺失回應保存已觀察資料、無重試）。新檔 readback；43669302039 pending/unverified；預期 380 tests 不是成功證據。CI 不執行模型或候選原碼。
- Windows 手動啟動（待 runner exact CI PASS 後）：從原 PR 候選分支下載對應 SHA ZIP/解壓，於含 src 根目錄開 PowerShell，先 `py -3 --version`、`ollama list`、`py -3 -m src.p1_local_role_runner probe`。probe 回 LOCAL_ENDPOINT_RESPONDED_NO_INFERENCE、version 與已安裝 name/digest；無可用模型或 endpoint 時停止，不自動下載。確認 Ollama 已關 cloud（見官方 FAQ）且可斷開外網後再執行 `py -3 -m src.p1_local_role_runner run --task B001 --model "<probe 實際 name>" --digest "<probe 實際 64 位 digest>" --output "$env:LOCALAPPDATA\\SystemBuilder-P1-Pilot-001" --confirm-offline-local-model`（新私有目錄不能已存在；先核對 ACL、不共享）。成功僅為 LOCAL_ROLE_RESPONSES_CAPTURED_REVIEW_REQUIRED；新 session/role 證據私下審查，不將 raw 內容傳公開 PR/CI。不得執行模型生成程式。之後依既有 capability_execution importer 格式整理模型實際輸出，隔離執行與 independent review 仍另行授權；不能以本地 raw receipts 自證真正模型能力提升。
- WRITE_OWNER: 原 Draft PR #8 候選分支；main、其他 PR（含 PR6）、Release、外部研究系統與正式資料未動。未啟動付費 APIs、外部部署、真實模型或真人盲測。

### 2026-11-15｜P1-2 優先：實際模型技能選擇、案例檢索及獨立評測

- User priority（本輪最新）：解除實際獨立多 Agent 執行及盲測阻礙；驗證七專家能否自主應用現有技能及案例，不啟用未授權付費 API 或外部部署。P2 合成工程訓練已完成足夠基礎，僅為實際失敗與必要缺口補測，不能反覆用同類罐頭測試代替真實模型訓練。
- P1-2a exact integrated HEAD 4afb04bc3f27a932012cca2abf50266ad765b182 / CI 43669358290/job 132675721505 completed/success，完整 raw logs (221931 chars)，380 tests in 38.147s/OK，三個 test_p1_local_role_runner 方法全過、P22D-DISTILL/PROCESS-CUT 與全部品質／安全／瀏覽器 steps success；前一 code/test CI 43669302039 cancelled 不計 PASS。無實際 failure。此為假 transport 契約，並非七個已執行模型。
- 重新查核 current sandbox：command -v ollama/codex/claude/llama-cli/docker/podman/bwrap 均無輸出；Python ollama/llama_cpp/transformers modules absent；loopback 11434 與 1234 connect_ex=111，無可用服務；tool inventory 未見獨立模型/subagent 介面。不能存取使用者 Windows 主機；沒有新增下載、付費 API、Secrets、部署或實際模型呼叫。不得推定其他私有環境亦無模型。
- P1-2b source：src/p1_skill_case_selection.py blob 63490d7e203f6974da0035b50d4a6d08125cea17 commit ba802211f801ce270271665ccebac8fbce726337；src/p1_local_role_runner.py blob e9f71658a774d7e4bb2a03e3ce76d63c34c3bea7 commit 2f035acb0d4c5123a4d053d174ea1bbb35e7e7e9。原 fixed 7 call mode 保留；新增 --case-mode default/curated（兩者同 14-call 預算）。每角色獨立 first response 選擇該角色 catalog 允許 skill ID、自擬搜尋 query 及 reason；host 核對 allowlist，由 catalog 讀實際 SKILL.md，使用新 public-case-workbench 與既有 learn.task_context 檢索最多四個 observed case、排除 candidate/conflict，保存完整 material。第二次 response 用選擇技能、案例與既定上游交接，明示每筆 case 的 applied/not_applicable/理由；只允許已實際取回 ID，透過既有 learn.cite 持久保存 model-declared applicability、hash 及 raw routing/work evidence，不自動 promotion。無 prerequisites 或未完整讀取一律 candidate，不冒稱既有工作台的正式 Artifact 已完成；未執行 model-generated code、無任意工具、無動態路由，固定角色 DAG；單角色可能只有一個 allowed skill，不能據此評估 skill choice quality。所有結果仍須人類或獨立功能 oracle 驗收，沒有真實推論證據。
- tests/test_p1_local_role_runner.py blob e75c3b00b999bfa46c61fc3add0b5cd21312d024 code/test head 9e255a9ca9618dbb0c35f7cc1b5f8c4a3cbb3239；新增兩組方法：default/curated 每組 14 fake transport requests、真實 SQLite case lookup/cite、P22-CASE-004 只在 curated 可見、QA 未見開發內容、缺 prerequisites candidate、raw SHA receipts；越權 skill 或虛構 case ID fail closed。已回讀，新 CI 43688099674 in_progress/unverified，預期 382 tests 不是已通過數量。
- 實跑分階段優先序（不另授權）：① 本地 Windows 已安裝模型 probe 無 inference，核對版本/digest、cloud disabled/斷外網、具適當記憶體及資源上限；待 exact CI 後一次 B001 run，保留失敗，不盲重送。② 在相同公測題、模型/digest、runner/source、OPTIONS 下，分開新目錄 --case-mode default（原 2 cases）和 curated（8 cases），每個 14 requests；記錄模型實際 skill/query、case applicability、candidate outputs 與證據，人工檢查是否選對技能／判對案例，控制上下文和實際 token 時間差；這是公開 dev ablation，不是 blind 前後測或絕對能力分數。③ 真正盲測所需：沿 docs/WEBSITE_HOLDOUT_EVALUATION.md 與 src.website_holdout_compare 的已驗收 seal/匿名/雙評閱/仲裁機制，由未參與訓練的獨立作者私人建立至少五題並封存，評閱者不接觸版本/彼此結果；現有 protocol 專評網站規格，不直接評七角色程式功能；本 runner 目前只接受 B001-B005 公開題，不得以之冒稱獨立 holdout，需要另行接入已封存合成題、獨立功能 oracle/安全沙箱及兩位獨立評審。④ 只有取得真正模型呼叫及獨立驗收後才量測 gain；自主角色分派（不同於角色內選技能）與受限工具執行另外驗證。保留正式 release、安全與隱私獨立觀測。
- Windows minimal pending probe（無下載/付費/推論）：PowerShell 執行 ollama --version、ollama list、py -3 --version；或候選版 CI verified 後從 exact SHA repo 解壓根目錄執行 python -m src.p1_local_role_runner probe；僅回傳 model name/digest/version，保留原有模型、不要貼秘密。若本地沒有符合的模型，停止并核對硬體／授權再決定，不猜測存在。Case-mode run 前須確認網路隔離及模型本地，不將控制旗標視為網路證明。正式測試與盲測尚需真實 execution/independent author/review，不用同一聊天模型虛構。
- WRITE_OWNER: 原 Draft PR #8 候選分支，main/Release/其他 PR/外部系統不動；不寫正式個資、私人 holdout 或付費服務。 

### 2026-11-15｜P1-2c 自主專家分派、QA 退件與任務重新調度

- P1-2b exact integrated HEAD ba136ed439841209385e961b432fddd0534fc9c6 / CI 43688167223/job 132733012963 completed/success，完整 raw logs (222450 chars)，382 tests in 40.071s/OK，P12-SKILL-CASE（每組 14 fake transport requests，真實 SQLite lookup/citations，default/curated 隔離），兩組 skill/case tests 與所有 workflow steps success。無實際 CI 失敗；保留前版可用 runner。不是實際模型推論。
- 新 src/p1_dispatch_runner.py（blob e2ff893b0596196d14a8f2dd8c77bdf777fa2ffc，commit c679f784c8e0b60275f95e06aef0df18c9b84b60）：沿用 local._http/_model/_answer、p1_skill_case_selection、team_workbench/workbench_tasks，非第二套任務資料庫。以內建公開 task packet、新 private workspace 及 8 個候選工作節點（七角色，QA 分 oracle/review）執行。主管每輪收到當前 ready tasks、state/revision、退件 findings 及預算，模型選 task 或 STOP；host 以 allowlist/candidate dependency/revision/hash 拒絕越權或過期交接。每個節點仍有獨立 role skill/query 選擇及真實案例檢索，保留候選內容與原始請求/回應/receipt hashes。QA oracle 只有 intake，先於 implementation，開發可讀 oracle；獨立 QA review 取得 oracle 與 exact implementation revision/hash 後對照，模型只可 REJECT（具體 findings 必填）或 REVIEW_READY（仍非功能驗收）。
- QA REJECT 走 tasks.finish FAIL，保存被退 revision/hash/具體 findings；在明確 pilot 預授權限內 tasks.revise implementation，重開開發及相依 QA/security/recovery/learning，舊 candidate bytes 保留，原 oracle/architecture/intake 不失效，下一輪 developer 收到退件理由。Task pool unbound，candidate-captured PASS/DONE 只表示候選回應已捕捉，非正式 Artifact 驗收；沒有呼叫 bound accepted artifact commit，不冒稱 model-written code valid。限制 12 次 dispatch、2 次修復、最多 3 次 QA review（每輪通常 3 calls，QA review 另 1，最多 39 calls），上下文 byte cap，STOP/預算耗盡皆需覆核；未知 reply 保存現況拒絕重送，沒有自動 resume 或跨檔案/DB 原子性。固定 DAG 只允許 ready-order 動態選擇，非任意工作圖/平行 subagent 或實際外部工具。No paid API, deployment, private existing workspace or untrusted candidate execution.
- tests/test_p1_dispatch_runner.py（blob 58b8a361dc579627bd5b7406bb57823059dbee2f，code/test head 8b6d7ad1522f01f29e8f270980aa60503f28ff15）：三個必要 transport-contract 方法，驗證模型選擇 QA oracle 先於 architecture；一次 QA REJECT→real task pool generation 2→review ready，保留舊 candidate 且原 oracle revision 1；反覆退件停止、model STOP；越權選 task／回應遺失停止且拒絕同路徑重送。All scripted transport, no model performance. 遠端 readback，43688378116 pending/unverified；預期 385 tests 不計實際 PASS。 
- 下一步不重複相似合成應用。最新 exact CI PASS 後，優先已授權 user host 的只讀 probe（ollama --version, ollama list, py -3 --version）及實際離線試跑。新入口（需先核對實際 model name/digest、cloud-disabled 並斷外網，使用從 exact SHA 解壓的 repo 及新的私人資料夾）：`py -3 -m src.p1_dispatch_runner --task B001 --model "<actual local tag>" --digest "<actual 64-char digest>" --output "$env:LOCALAPPDATA\\SystemBuilder-Dispatch-001" --case-mode curated --confirm-offline-local-model`。不要在 CI 或本聊天冒稱已推論。實跑後才能評估模型 routing、skill selection、case applicability、QA rejection 修復有效性。真正未見題仍需獨立封存及功能 oracle、受限 sandbox 和盲態審查；若 runner 不可用，先解除此阻礙，不再持續增加其他應用測試。
- WRITE_OWNER: 僅原 Draft PR #8 候選分支，不修改 main/Release/其他 PR/外部研究系統，不下載模型、不啟動付費 API、不外部部署、不寫正式資料。

### 2026-11-15｜P1-2 受限功能驗收與真實模型執行阻礙

- P1-2c exact integrated HEAD 53f2f44f88d617797cfed8a4ef746c5280e56130 / CI 43688435072/job 132733951433 completed/success，完整 raw logs (223085 chars)，385 tests in 46.839s/OK；三個 dispatch tests、P12-DISPATCH、P12-SKILL-CASE 及所有 workflow steps success。無既有 failure 需要修正；依舊為 transport fixtures、非真實模型能力證據。
- 環境實測：command -v ollama/codex/claude/llama-cli/docker/podman/bwrap 無結果；/usr/bin/unshare 存在；未見 ollama/llama_cpp/transformers/wasmtime Python module，loopback 11434/1234 connect_ex=111；預設模型 cache paths 未觀察到；tool inventory 未見實際 inference/subagent executor。未下載模型、未啟動外部 API/部署、未取得使用者 Windows 主機存取權；不將 unshare 存在視為已驗證 native-code sandbox。目前真實模型呼叫 0。
- 本輪自行選定既有 B003 公開志工排班重疊案例（public_tasks.json blob 0e422d8d36cb1697396dc753fb98304a9b914120），而非新增合成應用。src/p1_restricted_functional.py blob 955b279de16247ae15a538d8d888942e466231ce / commit 8846ef9a4c20878bb8657d22b82226dd3915fb0b；受限純函式 has_overlap(existing, proposed)，明確 pilot policy：既有最多 32 筆、immutable tuple pair、exact bounded integer、start<end；錯誤輸入由 host 拒絕，僅評有效 input 的 candidate boolean；不能宣稱候選支援非法輸入、完整 B003 產品政策或通用系統功能。AST 逐節點 allowlist（只允許單 def、if、for item in existing、布林/整數比較、index 0/1、local assignment、return），不 compile/eval/exec/import/call candidate code，無網路、檔案、任意工具；source 6000 chars、AST 240 nodes、3000 steps upper bounds。固定 12 個 public oracle 由候選外預先定義，測空資料、相接、左右重疊、包含、相等、多筆及負數；exact source SHA/oracle SHA/case results，標記 public slice，非私人 holdout 或獨立人類評審。不宣稱為任意 Python sandbox。
- src/p1_dispatch_runner.py blob ebebbe04930dd3c46e67e873fe6cf0f9f958faf9 / commit cfe4528a9e8e4efe025382b833e62624b52ce983：explicit --functional-b003 只允許 B003，其他模式不變。將受限 function contract 傳入模型任務，不傳 oracle 測試值；Developer 產出 plain candidate source，QA review 時 host interpret exact upstream revision/sha，獨立於 model verdict 產生報告並保存。host failure 即使 model REVIEW_READY 也依既有 tasks.finish FAIL / tasks.revise 重新分派 implementation 及相依任務，提供實際 failure findings；保留舊版與原 oracle。host PASS 也只為固定 public slice、非功能全面通過/正式 Artifact 或部署認可。功能 tool 由 host 在既定 QA 關卡執行，不是模型自主執行任意工具。
- tests/test_p1_dispatch_runner.py blob 1abe0bfef5eced5555b359d85e936b3c9f933727 / head f957b8a85dc7e981184daf05a70ec34b513b5f16：三個必要 tests（真實 bounded interpreter 12-case oracle 區分 correct/incorrect；拒絕 unsafe AST/dead branch/invalid input/excess steps；fake model REVIEW_READY 但第一版實際功能失敗、host QA 退件後第二版受限函式實際通過，檢查兩代 report hashes、原真實能力 claims false）。readback，43688881282 in_progress/unverified；預期 388 tests，尚不得計入 PASS。程式執行的是受限 AST 語意，不是在 public CI import/exec 未知 Python。
- 真實實跑路徑（待 exact CI PASS）：Windows 既有 Ollama/Python read-only probe（先前已提供 ollama --version / ollama list / py -3 --version；不要求反覆執行已可取得的結果）。若本地模型已安裝，利用 exact SHA checkout、`py -3 -m src.p1_local_role_runner probe` 取得完整 name/digest；確認 cloud disabled/本地離線、私人新目錄及資源預算。首輪 `py -3 -m src.p1_dispatch_runner --task B003 --model "<observed tag>" --digest "<observed digest>" --output "$env:LOCALAPPDATA\\SystemBuilder-B003-001" --case-mode curated --functional-b003 --confirm-offline-local-model`，最多 39 chat requests、兩次修復，不自動重跑。驗收 evidence 私人保留 exact candidate/functional reports/repair history，不將本地聲明當獨立 provider 認證。當前無可用模型，不能依測試替身宣稱七專家實跑。後續真正盲測沿既有 protocol 凍結獨立題目與外部 oracle，需 verified sandbox 才能跑任意模型產出的 native Python/完整系統；獨立作者與雙評閱者仍未取得。 
- WRITE_OWNER: 原 Draft PR #8 branch only；main、Release、舊 PR、外部研究專案、真實資料不動；不啟用付費 API 或外部部署。

### 2026-11-15｜TD-001／TD-002 重新定位及最後工程基準

- 本輪 exact engineering head d2ca12006988100a500a6a6fea0f41cd73de5f85，CI 43688939298/job 132735394546 全部步驟成功；完整 logs 223987 chars，388 tests in 39.030s/OK，P12-FUNCTIONAL 12 項公開固定 oracle 實際受限語意運算、P12-HOST-QA 模型替身 REVIEW_READY 仍被真實 host fail 退件並於 revision 2 通過。此為受限工程證據，不是模型實跑或盲測成績。
- 使用者明確確認 TD-001（決策原文及分析見 training/DECISION_LOG.md）；TD-002 跨對話接續與決策保存同步。舊本地模型優先路徑被取代，所有程式、案例、測試及歷史保留不刪；不啟用付費 API、部署、跨專案寫入、不合併／發布。後續優先已授權平台上的實際工作與可遷移知識，按實際證據標示協作模式。此輪只變更文件，不宣稱新架構已通過真實工作驗收。

### 每次續作及更新協定

1. 當使用者提出訓練、續作、改善、分析、方向討論時，定位本 repo；先查 main、當前訓練 PR #8 的實際 head、最新 CI/PR，再讀該 head 的 START_HERE.md、AGENTS.md、本檔頂部及 training/DECISION_LOG.md 的有效決策，按需讀索引 review／技能／程式／測試。新候選轉移時保留本路徑並更新導航；不得用固定 SHA 當現況。
2. 以使用者最新決策、實際程式/測試與同 SHA 證據為準。歷史文件與舊對話只供導航；本節的建議不授權付費模型、外部寫入、合併、部署或正式發布。
3. 依 TD-001 優先在現有已授權 AI 平台完成有實際價值的工作、讀適用技能／案例、驗收及覆盤。缺本地 runner 不構成日常工作阻礙；沒有獨立子代理時標記單 Agent 分工。受控合成測試只在真實缺口或必要回歸時使用，不重複施工。缺特定工具或權限時只阻塞受影響步驟，不能擅自替代部署或跨專案寫入。
4. 每次實質訓練後更新本檔頂部 SOURCE_VERSION、LAST_VERIFIED_STEP、COMPLETED、NEXT_ACTION、BLOCKERS、WRITE_OWNER、SYNC_STATUS 和路線狀態；記錄真實測試命令/CI、失敗修正、產物與限制。每次具有長期價值的討論同步增量保存至原 decision log；重大分析存 reviews 並索引。區分 DISCUSSION、PROPOSED、CONFIRMED、IMPLEMENTED、VERIFIED、SUPERSEDED、REJECTED 及未執行／阻塞。使用者確認、實作及驗收分開。寫前核對版本，回讀同分支檔案、核對同 SHA CI，失敗明確回報，保留 Git 歷史；不複製訓練主檔。
5. 若候選 SHA 改變，分開記錄最後已測程式 SHA 與目前文件 SHA。單 Agent 實作/合成測試、真實 LLM 執行、獨立子代理、獨立盲測、正式 Release 均分開報告。未經授權不自行修改模型權重或宣稱已修改。
6. 本檔為訓練方向的持久化入口，`docs/CURRENT_STATE.md` 與 PR/CI 紀錄保留實際工程歷史；有衝突先查證並更新本節，不另建重複進度來源。


## 目的與邊界
此計畫聚焦本 Agent **能否完成系統開發**，非持續增加供應商來源稽核。要訓練的能力依序為：需求理解、架構取捨、可執行任務計畫、程式實作、QA Debug、跨七角色實際交接、從錯誤修正策略。適用 Repository 只有 `lily4318/reliable-system-builder-agent`；所有公開案例皆是合成，不帶外部正式專案原碼、資料、個資、API Key 或部署權限。

本 PR 與尚未合併的 Draft PR #4（目標分流）、#5（角色交接）及 #6（真實模型 runner/來源）**平行且不互相依賴**。本候選不替三個 PR 做合併決策；任何未來整合須按當時 main 解衝突、同 SHA 跑全套回歸及另行人工審查。

## 選用公開評測工作台（歷史工程操作手冊，不是 TD-001 日常前提）

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

## 選用獨立能力訓練與改善前後比較流程（非日常工作前提）

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

## 歷史基準設計時的狀態（非現況；以頂部為準）
**已設計並可在此 Repo CI 執行**：公開合成需求、參考產物、任務生成 CLI、結構評分器、受信任參考程式與單元測試、既有政策及復原基準。**仍沒有**：實際模型生成的系統成果、真正子代理執行、未知程式的隔離沙箱、獨立 holdout、真實部署驗收。以上項目不得借用之前 PR #6 的 runner／模型來源檢查狀態，或以任意合成 PASS 冒充完成訓練。
