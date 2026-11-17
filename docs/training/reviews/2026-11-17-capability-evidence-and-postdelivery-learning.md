# TD-005 / TD-004｜能力證據重整與交付後實戰學習提案（2026-11-17）
狀態 PROPOSED / NOT_RUN。使用者要求依 R1 方向規劃交付後八位專家的真實任務成長、重新檢視原驗收及精簡。本輪未確認 R1、未授權 M3/外部專案/部署/正式發布或長期執行；REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，並非八個獨立模型或權重訓練。
來源候選 c5d721da97db2d2aef32e1a1505e66431445141c tree 755e9d3098a63b6fecf23c6dda94e719226c9396，CI 44007315919 completed/success（metadata）；主檔 0a3b871dd59eef1b0c9be64fdcea2cd95678b273、決策 853ebb5dd70be8ab2c8b5bfaa2b78028f3638295、R1 59a9cccceb638301d7530505e31f1491343b7511、AGENTS 95b6e26d9f163f325b42fe4e7f78336b7d646d1d、catalog 1bc4f3711237694b4bb82f3c38e100ac143d9d03、[既有 15 skill/28 methods 證據矩陣](2026-11-16-research-handoff.md) bda69befc58606abb477e699e7dc6f75ad9b57bd、[原 A01–A07](2026-11-15-editorial-website-spec.md) de8ee98b3364e9287ff762ab30dddfbd70d0979f、[B01–B10](../../BEGINNER_ACCOUNT_ONBOARDING.md) d4727f11e4345f59ed1e6a70d63be953d54d13b6、[C0–C6](../../CLOUD_ARCHITECTURE_SELECTION.md) 442fa4a363b8b65935651e78ad07197970624618、[獨立復原](../../INDEPENDENT_ACCEPTANCE.md) 39a5d00ea59d5abe0457a16e6fa42a561e8f0522、[私人 holdout](../../WEBSITE_HOLDOUT_EVALUATION.md) b3936bdb8d77fb59e3aa15918ea5e73a2b299d6f、[教材矩陣](../curriculum-coverage.json) 04cab3bea1e83e9532361269b676923427cf9c97。以上為正式文件/原記錄覆核，不是此次重跑或所有原始日誌重新讀取。完整測試個案索引沿原矩陣/原檔，不再建立平行評測庫。

## 1 目的與證據層次
TD-001 既有平台/按需角色技能/共用空間/覆盤，TD-002 真來源及續作，TD-003 初心者引導，TD-004 深度習得，TD-005 學術領域定位與第一版交付。前四者不被第五者取消。首版是有限可用門檻、長期是能力遷移，不是完成教學 APP 或模型訓練。將技術原理及實作、陌生遷移、產品可用性、管理/安全治理分開報；同一證據可供數項適用責任引用但不重複計分，不把角色指令、CI、教材清單當精通。
 
## 2 原驗收全類別與精簡對照（群組覆蓋，不重跑每個測試）
| 原驗收 | 真正證明 / 未證 | 建議 |
|---|---|---|
| 歷史公開 policy/quality/recovery cases、W101–W106、單元與 CI | 確定性流程、拒絕危險、需求格式、回歸、精確 artifact；非未知需求泛化/真遠端或模型成效。原獨立 recovery 為另一 oracle 路徑，非第三方。 | 保留安全/回歸門檻，版本變更照既有 gate；不要重複人工跑公開案例或計能力總分。 |
| A01 真瀏覽器編審發布；A02 真多角色拒絕；A03 邊界注入；A04 競寫/收據/未知；A05 持久化備份復原；A06 兩 viewport DOM | 原 WEB-EDITORIAL-01 受控本機跨層功能、安全與復原；是真工程，但非 production 全量資料/雲端/真實用戶。 | 沿原 A01–A06 實證，真需求出現不同技術邊界才驗；不再建另一合成網站。 |
| A07 原追溯交付/真跨對話接續 | 工程交接及來源重建、首答正確；source-only 獨立性 PARTIAL，原暫時聊天已關閉。 | 保留 Gate，不重做同測；不同可查證環境才補，非盲測。 |
| B01–B09（16 methods） | 帳號/成本/錯目標/工具/授權守門的受控路由，不證真人理解或真所有平台。 | 自動回歸沿用；按真任務必要帳號場景，不為測試額外註冊。 |
| B10 | 真新手引導與理解，非程式能力全驗；已有連接僅 partial。 | R1 待確認後併必要設定與 C6，無適用新手時按原限制人決定，不自動 PASS。 |
| M1 PM/roles/catalog、stale scope、handoff | 八角色十五技能及前置/失效/停止規則可執行，非八模型或真團隊績效；原 516/516。 | 保留最低管理安全契約；不新增 PM 引擎或重作 catalog。 |
| M2-1 APP R1 重現/分派、R2 負測、R3 CSV、R4 UI/資安、R5 合成限定 | 一個靜態產品的真瀏覽器及資料契約，原 517/517、375/1280、三 blob；非 RT 物理精度、正式研究、真資料庫/Auth、line-of-business 全能力。 | 不增 APP；技術驗收完成，R1 若核准則只線上核心真人流一次，file:// NOT_TESTED/NOT_PROMISED。 |
| 專項 HTTP/SQLite/PostgreSQL/DevOps 真 lab | 有真故障重現、修正、回歸、SQL 競寫/RLS/migration、artifact byte/本機 rollback 等工程證據；精確版本與範圍限定，不外推平台。 | 真任務重用；遇不同 DB/HTTP/權限/部署語意才重驗。 |
| 近期研究 scope/data/handoff/timing/trial、GAS 兩 lab | SQLite/WAL/Chromium 部分真；JS 受控模型 13/13、28/28、18/18，timing 11 PASS/1 SKIP、trial 9/9；非真 Google、IndexedDB/跨裝置/光學精度/實際並行等。 | 保留真試驗結果、標示層級及來源更正；不同真需求驗，不為分數強加到靜態 APP。 |
| C0/C1/C2 | 真技術與成本/權限/資料邊界取捨及 artifact/復原準備；不等於上線。 | 另授權才做；優先一條零新增成本適用路徑；不四平台強制真部署。 |
| C3 | 明示精確外部操作授權，是治理非技術能力。 | 必須保留，不自行放行。 |
| C4/C5 | 真 HTTPS、功能/安全/版本更新/可回退是真平台實作證據；靜態 C5 DB/競寫等 N/A 有理由。 | 完成唯一同案例，原遠端正負測由 Agent；不降低零成本/未知寫入/資安。 |
| C6 / UAT | 產品可用、人類理解、啟用及維護決策；不是完整八專家能力。 | R1 一次共用 UAT、啟用另核；不重複本機與線上。 |
| M4/release checklist/ruleset/Environment、非作者審查 | 正式發布治理＋版本證據，非工程專精；未證必要治理則只候選。 | 原守門保留、不增假審核、非作者仍須實際人核。 |
| TD-004 七階段/L0–L6、教材 validator、私人前後盲測 | 教材覆蓋與成熟度按單元；L5 真陌生遷移、L6 真交接/整體。validator 只檢結構；私有至少五個未見需求、同模型/資源、雙盲評分的工具已備，未實跑。 | 不把公開分數/517 tests 當泛化；不要求本地 runner/盲測為首版必需，將私有評測作另授權選用嚴格增益驗證，保留安全規則。 |
原八組 MUST、6包、NT$0、11/22/29 目標不變。本輪未重跑/逐一重新驗證所有歷史證據；列的是現行及歷史主要驗收群組。首版仍2/6；M2-2 partial，R1 未確認，M3-1/C3/M4 未授權。
 
## 3 八專家 × 十五技能：交付後依真需求主責及可驗進步
| 主責/原 skills | 下一類真任務及能力證據（示例，非委託） |
|---|---|
| PM project-scope/control/delivery-review | 真研究專案一頁 scope、需求修訂、風險/成本決策、停點/交付；驗 scope drift 被拒、原驗收無跳過、人工操作及重工是否下降。不可只看管理文件數。 |
| System Lead project-intake/task-planning/resume-project | 不同研究/實驗/教學需求，自然語言確認、DAG、角色/產物、來源 identity、跨真對話交接與修訂失效；驗需求追溯、未重工/錯 repo/未授權。 |
| Architect requirements-spec/architecture-design | 報名容量與多角色 ACL、實驗 protocol/版本/字典、課程互動；以 ADR 的替代方案及實際約束、相容 migration/快照一致證據驗，研究設計由 PI 核准。 |
| Developer implement-feature/debug-and-repair | 真表單/資料/刺激流程、持久化/錯誤、跨裝置與匯出；重現缺陷→最小修復→獨立 oracle 回歸，運用原 HTTP/PG/GAS 等證據但核平台差異。 |
| QA test-and-acceptance | 原需求逐條正負測、異常/並行/恢復、真資料格式及 UI/遠端；科學時間另按研究規格及真設備，不自訂排除閾值；固定預期不自驗自評。 |
| DevOps/SRE deployment | 環境/成本/最小權限、精確不可變版本、安全更新、故障對帳、復原備份/回退、監控；真遠端讀回與演練，避免盲 POST，原先 local 證據不代 provider。 |
| Security security-review | 真實研究識別資料、同意/資料最小化、角色/研究範圍/列權限、保存/刪除、外洩負測與安全審核；真匿名與適用 auth/RLS；REC/IRB及科學倫理由適格人核。 |
| Learning Evaluator learn-from-feedback/knowledge-distillation | 失敗與修復的可驗因果、與舊案例比較、限定適用條件、人審候選知識；在另一真任務確認採用/拒絕和遷移，保留失敗及版本，不把自述/新規則數當成長。 |
並非每個任務強迫啟動全部角色；只按風險/依賴選用，無獨立模型標 SINGLE_AGENT_ROLE_WORK。可用於不同實際學術場景的訓練建議（不指定或讀寫其他 repo）：(a) 研究招募/報名/預約/問卷與安全資料流程：優先 Architect/Developer/QA/Security，容量競寫、撤回、重放、資料權限/匯出與備份；(b) 心理/行為實驗：Architect/Developer/QA/Security/SRE，版本化 protocol、刺激授權、隨機/平衡、RT 校準、失焦、trial 中斷復原、missing vs zero、可重現資料；(c) 教學 APP/互動測驗：PM/Lead/Developer/QA，學習目標、正確回饋、可及性、不同裝置、低成本、交付；涉及學生識別/成績適用 Security。選最近有真需求、可安全授權且具遷移價值的一個小工作包，不編造新網站委託、無需求不開工。
 
## 4 真任務學習循環與原 TD-004
先鎖定該專案唯一正式來源/目標/授權/風險/預算/資料界線；核現有案例/版本/前置，不足才讀可核教材/原始來源，記實際讀取、原理、限制/替代與證據；用已確認 scope 實作，固定驗收 oracle/負例/復原，先解決問題再抽取通用經驗；人審後只增量原技能/role/EP/decision 或私有工作區，不改正式科研規格、不把特定私有案例/PI資料搬至公開 repo；另一不同真任務記 evidence of transfer，若不適用或失敗保留理由、修正與回歸。以 AGENTS 原七階段、L0 未學/L1 原理/L2 取捨/L3 實作/L4 真缺陷/L5 陌生遷移/L6 跨角色整體驗收逐單元判定，不以角色平均分升級。
保留 TD-004 已確認延後教材補齊與專家分工：盤點 PARTIAL 176目錄/163對應/13缺，章節與引用未全面核對；沿唯一矩陣（units 空不是已學），一單元一主責/必要協作，取得合法可讀材料後，另授權按缺口/依賴/真任務學。不能只做需求驅動而永遠忽略互補基礎知識；真任務短板與延後教材為兩條共用同一矩陣的路徑，不重複讀與不假進度。
 
## 5 精簡後的成效追蹤（提案而非新增首版 gate）
以一筆實際任務結案/原證據 ID 為單位，在原覆盤和 skill/case/矩陣上寫最少：版本、環境、授權、需求/主責、原能力、真缺口、採用/拒絕知識及來源等級、修復前後客觀結果、未驗限制、下一個不同任務驗證、人工批准。避免另建儀表板/平行台帳/自我打分。每任務只計實際人工操作/必要批准、已確認且可驗需求的首輪通過/總數、同類缺陷的再發/適用機會、可重現紅→綠、實際復原/真轉移通過/符合條件機會；分開工具阻塞、需求變更與 Agent 原因。首次真任務作 baseline，後續同風險/難度/版本可比者對照；分母/環境/原始證據缺失記 unknown，不捏造百分比或設硬性不安全速度目標。危險越權/資料外洩/未核准寫入不得放行，安全 gate 不用平均分抵銷。若要主張 Agent 系統版本的能力增益（而非單次成功），另按原 private holdout 固定模型與預算、隔離未見案例/雙評閱者的協定執行；模型權重增益不是本訓練承諾。每個真工作包結束既結案亦覆盤，無通用新知則不改 skill，無新的有效任務不做重複練習；不新增排程。
 
## 6 證據來源更正（EVIDENCE-PROVENANCE-CORRECTION-007）
更正之前 GAS-ACCESS-SESSION-001、GAS-DIAG-002、GAS-DATA-003、TRIAL-RECOVERY-004 及 A07 Temporary Chat 相關說明的官方引用：先前網頁調用未提供可核讀正文，將連結/一般原理記成已實讀/官方佐證並非有效證據，撤回相關肯定標籤，原連結僅 REFERENCE_LINKS_UNVERIFIED。尤其撤回 Sheets 2026-09-03、later 2026 超額計費公告及精確 quota/限額為當前實讀結果的宣稱，不可作成本依據。實際需要時真讀當時官方正文和帳戶/plan/費用，不確認即停。心理實驗 timing 文獻的完整原文閱讀亦未獨立核證，保留引用為待覆核；不能把文獻連結算教材已習得。原 user-reported Cookie 復原（根因未確證）、JS 28/28/18/18、trial 9/9、timing 11 PASS/1 SKIP 及其他真工程證據維持；更正不撤銷實際執行，不推論已重跑。A07 首答與原 GitHub 事實核對仍保留，無法證明平台隔離，只保留使用者回報。不聲稱所有歷史官方來源均無效；逐一按真可得證據審查。原歷史文字由本更正優先解讀，保留 Git history 和未證限制。
 
## 7 提案及停點
推薦兩條並行但分開核准：先確認 R1，另授權 M3-1 走一條真部署路徑，不增加展示 APP；第一版實際交付後，確認本提案，再依新真任務獨立授權逐包推進，教材按原 TD-004 後續方案另准。不以前述學習規劃自動接管、跨專案寫入、付費、真人研究、外部部署、main/release。現行 NEXT_ACTION、A07 PARTIAL、B10/UAT、2/6、R1 PROPOSED/NOT_RUN、NT$0/日期均不改。本輪只有文件查核、提案及證據標記更正，無技能新功能、實測或部署、無新案例練習。