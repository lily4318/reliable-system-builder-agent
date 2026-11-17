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

## 2026-11-17｜後續明示確認及實際 M3-1 查核
使用者已確認 R1 並授權 C0–C2；前述未確認為形成時狀態，不再有效。C1 BLOCKED/C2 PARTIAL、2/6，M3-1 已授權續補，完成停 C3；A07 source-only 及其他原安全門檻維持。詳[實際查核](2026-11-17-m3-predeployment.md)。長期真任務學習提案仍 PROPOSED，不接管外部專案。


## 2026-11-17｜正式確認：TD-004／TD-005 交付後雙軌持續能力深化（POSTDELIVERY_DUAL_TRACK_CONFIRMED_DEFERRED / NOT_RUN）
使用者明示決策：「我確認首版交付後採用真實任務與教材深度學習雙軌並進的訓練方向，請保存正式決策與八位專家的能力成長標準，不提前執行長期訓練或接管其他專案。」
依原提案 §1–5（本文件），正式採納雙軌方向、八專家能力成長標準、原七階段／L0–L6、最小證據追蹤與不重複學習原則；原提案形成時 PROPOSED 的狀態已由本節取代，歷史保留。決策屬首版實際交付後的長期訓練，現不啟動兩軌，不新增首版 gate 或新訓練台帳、不新增角色／技能、不接管其他專案、不建立排程、不觸發付費模型或外部資源。未逐項選定實作任務或固定跨領域先後，待交付後由使用者依真需求、前置依賴、可讀教材、風險及獨立授權決定。首版仍優先完成 M2-2 殘缺、M3-2 與 M4；不取消 A07/B10、安全、零支出、真人驗收及正式發布門檻。C3 仍未授權。

### 正式能力成長標準（沿用 §3 既有 8 角色／15 技能）
| 角色及原技能 | 未來成長之有效實證 |
|---|---|
| PM（project-scope / project-control / delivery-review） | 真實 scope、修訂、替代方案、成本與停止決策，以及按同風險同等難度比較的需求遺漏、重工及必要人工負擔；安全與既定驗收不得被效率抵銷。 |
| System Lead（project-intake / task-planning / resume-project） | 陌生真需求確認、依賴／分工／交接產物、版本與授權追溯、來源獨立接續；核實不重工、錯 repo、過期 scope 或越權，不能以自述 GATE PASS。 |
| Architect（requirements-spec / architecture-design） | 真實限制下的替代技術取捨、ADR、研究 protocol／資料字典、相容遷移和一致性證據；研究方法與科學效度由適格研究者核准。 |
| Developer（implement-feature / debug-and-repair） | 陌生必要功能實作、可重現故障、定位因果、最小修復、獨立 oracle 正反測與回歸、在不同實作邊界的遷移；不得以已成功的同例重新計分。 |
| QA/UAT（test-and-acceptance） | 可追溯需求與預先固定 oracle、適用正負測、競寫／異常／恢復、真資料格式與 UI／遠端證據；科學測量依真設備與研究規格，非自訂科學標準。 |
| DevOps/SRE（deployment） | 真平台選型／帳號／成本／最小權限、可核版本與 artifact、HTTPS 更新／回退、未知結果對帳、備份復原和監控的實際證據；本機成功不替代 provider 驗收。 |
| Security（security-review） | 真資料最小化、權限／角色／研究範圍隔離及外洩負測、適用 Auth／RLS、保存刪除與同意界線；REC/IRB 等科學倫理由適格人核，越權不得以其他通過項抵銷。 |
| Learning Evaluator（learn-from-feedback / knowledge-distillation） | 實際來源與因果核實、失敗／修復／適用限制及必要人審、原技能案例增量，在另一真任務驗證採用／拒絕與遷移；未有新證據不升級、不假稱閱讀或完成。 |

雙軌共用原 TD-004 七階段與逐單元逐角色 L0–L6（L1 原理、L2 取捨、L3 實作正反測、L4 真故障修復、L5 陌生遷移、L6 跨角色可追溯整體驗收）。保留每單元唯一主責與必要協作、教材完整覆蓋承諾、原 curriculum-coverage.json 單一矩陣；缺檔／引用內容未核、PARTIAL 176/163/13、units=[]，不冒稱教材已學或精通。以原任務結案紀錄／證據 ID、實際人工操作與必要核准、已確認需求首輪通過／可驗需求總數、重工／同類缺陷復發／適用機會、實際修復前後與陌生遷移證據衡量，欠分母／可比情境標 unknown，不設任意數值 KPI 或角色平均分。區分真工程、受控模型、正式產品、管理治理、陌生遷移、獨立盲測；相同證據可溯源引用但不重複計分。既有 private holdout 若另授權才作嚴格版本增益比較，不是首版必需、不宣稱權重提升或八獨立模型。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK。

本輪僅正式決策及原提案、主檔索引同步，未讀新教材／執行深度訓練／安排新專案或新增驗收；C0–C2 pinned 6cdd6fe1042505143234623d95eef028a4866e00、3/6，M2-2 PARTIAL、C3_NOT_AUTHORIZED，零額預算、R1、A07/B10/C6、M4 及原管理日期保留。下次真正執行 C3 前重核最新 exact head/CI、程式及平台狀態。來源基準 77f5874f5c9c32518311d08188f20166046167d6 tree fe21ed27e7a1843a27f4b4923765307f54cfe8e9；CI 44015390360 completed/success（僅 run metadata，未重跑或讀原始 log）；原主檔、決策、本覆盤 §1–7、AGENTS、START_HERE、skill catalog、curriculum matrix、原 M3-1 查核皆重新定位讀取。寫後回讀與例行 CI 分開。


## 2026-11-17｜TD-005-R2｜專業能力優先、解除首版驗收阻塞（CONFIRMED；新訓練尚未執行）
上文「首版實際交付後才開始雙軌」與相應順序被取代；原標準、門檻、歷史成果不變。詳原[決策紀錄](../DECISION_LOG.md)。

### 八角色證據盤點（不是新實作、不是整體角色評分）
沿原 [15 skill / 28 method 證據矩陣](2026-11-16-research-handoff.md)、原 8 角色 catalog、curriculum-coverage.json 與既有專項實證。原候選 ffdfb7af86bc3d30063c0af403d98f8a8f2935b9，CI 44016059942/job 133814152466 先前實讀 517/517、完整 gate、tree 一致。新文檔 CI 另核。各欄為既有工程證據與待深化的實際缺口，非逐章教材成熟度、模型權重提升或八個獨立子代理。

| 原角色/技能 | 已有證據 | 待深化及驗收 |
|---|---|---|
| PM project-scope/control/delivery-review | scope/stale/人審測試、本案零成本部署與停止決策 | 本案反覆人工補證、目標偏航；先蒸餾阻塞分類、兩次無新證據停點及獨立續作；不同任務驗不錯置 gate、不越權、不反覆操作。 |
| System Lead project-intake/task-planning/resume-project | 13題/6場景、DAG/revision、A07 history-assisted | 陌生需求、獨立來源接續與工具能力前置；真需求修訂後正確重排依賴，A07 仍部分未證。 |
| Architect requirements-spec/architecture-design | 規格審閱、13/13 受控 JS 字典、PG 真 RLS/交易/遷移 | 學術 protocol、可重現資料契約、平台取捨/失效及跨裝置持久化；具體新條件驗 ADR/資料復原，不重跑原 PG 練習；研究者核准科學規格。 |
| Developer implement-feature/debug-and-repair | APP/CRUD、HTTP red-green、SQLite/PG、trial；GAS 28/28、18/18 受控模型 | 真瀏覽器端持久化/中斷復原、跨平台故障及真 GAS/Sheets 待工具與授權；只選未覆蓋且可測的新缺口。 |
| QA/UAT test-and-acceptance | 本機 Chromium/CSV/正負測、精確 CI；timing 11PASS/1SKIP | 獨立 oracle、研究資料/跨裝置/中斷驗收；預先核 runner 網路及 CORS/瀏覽器能力，區分 tool blocked 與 product fail，科學硬體/真人另驗。 |
| DevOps/SRE deployment | 真 artifact bytes、本機 activation rollback、Pages C3 | 遠端版本更新/回退、可觀測性、成本/權限與實際工具能力前置；待適用真任務補，不復活示範 APP。 |
| Security security-review | 真 PG RLS/ACL、HTTP 拒絕、研究範圍隔離 | 真雲端 Auth、研究資料最小權限/撤回/保存、外洩與跨身份負測；在具體安全條件深化，不搬真人資料。 |
| Learning Evaluator learn-from-feedback/knowledge-distillation | 案例去重/人審、validator、EP 索引 | 原教材按實際章節進單一 matrix，區分來源/閱讀/實作/遷移，本案失敗蒸餾；可比新任務證據，無獨立盲測不宣稱增益。 |

### 實際訓練順序（已規劃，未執行）
- P0 PM＋System Lead＋Learning Evaluator（QA/SRE 協作）：核原 project-control/resume-project/test-and-acceptance/deployment 守門，以本案跨源 helper 失敗、Work 工具缺席做真失敗覆盤；已有規則就不重寫，缺「工具存在與可達性前置／無進展停止／獨立阻塞不阻學習」才最小增量並真負測。交付可核修訂或不修改理由、正負測及 exact CI；不再測 Pages。
- P1 Learning Evaluator 主責、Architect 協作，可與 P0 獨立續作：原 matrix inventory PARTIAL、176 expected_ids、原記錄163對應/13缺、units=[]。找合法既有備份及章節索引，核檔名/可讀全文/版本/引用、缺件名單；按真內容唯一主責/前置/skill 更新原 curriculum-coverage.json 並跑既有 validator；缺檔只阻該單元，不公開教材全文、不編章名或 L1，不把盤點算學習。
- P2 Architect 主責、Security/Developer/QA 協作：依實際章節及依賴選資料模型、研究資料契約及權限一致性的第一個尚未覆蓋基礎單元；先核 PG/HTTP/SQLite 既有實證及替代方案。完整七階段、正負測、故障修復與不同情境遷移；以教材實際前置調整。
- P3 Developer/QA 分別主責不同單元：瀏覽器資料持久化/研究 trial 中斷與重現、計時/CSV、可及性及跨裝置；先核 9/9 trial、11PASS/1SKIP timing，僅未覆蓋缺口；不把模擬當物理精度、真服務。
- P4 Security/DevOps 分別主責不同單元：身分/最小權限、真平台資料及版本復原、可觀測/成本；需要工具、真雲端或外部授權者列獨立前置，不阻可安全學習。
- P5 全團隊按另獲授權的真研究/實驗/教學任務，依真需求選用單元，實際交付、覆盤、驗陌生遷移；缺真任務授權則持續教材路徑，不接管。首版餘項獨立延期；未來有工具及授權才補，不作前提。
每單元遵守原七階段及 L0–L6；原來源真讀、原理/限制、對應既有技能、可重現實作+正負測、不同情境遷移及交接；未完成不升級。逐包保留出處、原因、實際證據、未驗限制；不新增台帳、排程、角色、技能、展示網站、外部項目。原交付管理日期留歷史，不承諾正式交付；後續按真進展與使用者決策重估。


## TP-010｜開工、需求記憶與原團隊範本對照（DISCUSSION / PROPOSED）
使用者詢問 Agent 每次如何開始訓練、需求討論後寫入何處，以及與原始團隊訓練範本的差異及改進。此次實讀已授權私人教材備份的啟動說明、團隊總規則、使用者訪談技能、回饋與蒸餾技能及九技能目錄；未讀個案或私人品牌資料，未全面審查九技能。公開 repo 不保存私人 Drive 位址、個案、手冊內容或教材原文，僅記本 Agent 的原創改善分析；完整對照留原授權對話。查原候選 START_HERE/AGENTS、主檔與決策、catalog、workbench、需求訪談流程、工程知識索引、project-intake/project-control/resume-project/learn-from-feedback/knowledge-distillation 與教材矩陣；基準 14b5c7df80226db14993697e1dee51ee0ec22866，前次 R2 CI 44018479117 completed/success（run metadata，非本輪重跑）。原 R2、P0/P1 與停用決策不改。

### 本次對照所見
- 啟動：現有訓練入口先讀最新候選主檔/決策，任務依 catalog 選必要角色與技能，EP 索引按需要選案例；然而 GitHub 原生模式靠操作者確實讀取及採用，不是獨立子代理自動初始化，更非每次都實際走完所有技能步驟。私人 SQLite context/handoff/feedback 有機制，但此次主要以 repo 原生模式運行，未證常態私人工作台。
- 需求：建站有十三題訪談、明示/推導/待確認、可編輯確認與規格交接；Agent 訓練討論則寫主檔、原 DECISION_LOG 與 reviews，規則落入 AGENTS/START_HERE 或角色/skill；各專案需求仍存各自正式規格。重要確認與普通修正/偏好的長期生效需要分層，不能只累積歷史。
- 啟動簡潔性與使用者認識：原範本使用一個持久、先讀的使用者脈絡以及清楚的交付位置，現有 Agent 多個工程證據層、版本及權限較嚴，但缺乏可快速閱讀且可核實採用的當前使用者工作偏好/有效規則入口。原主檔的長度、舊語句及個別 skill 舊首版收斂段可能讓新 R2 優先序讀取失敗；這是 P0 要測的實際風險，不是宣稱已修復。
- 回饋與蒸餾：原團隊範本強調日常明示回饋立即落入可讀的共享記憶，後續再精簡；現有 Agent 私人工作台已有候選、人審、去重衝突與歷史；公開知識索引有依任務選用，但未證每個真工作都實際採用、記錄與閉環遷移。不能讓一次性需求或不可靠結果直接變通用規則，也不能因欠私人工作區而將私人記憶搬公開。
- 真實工作成效：現有許多實作/CI/受控 lab 證據；A07 source-only 未驗、教材 matrix units=0、真任務遷移與持續記憶生效仍薄弱。既有 project-control 已有兩次無進展停止及獨立續作規則，最近 Pages 偏航是規則未落實的實例，不應先重複寫同一規則。
### 改善選項（未核准實作）
A. 維持現有分層而只增加紀錄（不建議，容易增加查閱負擔）。
B. 推薦將原唯一主檔頂部/有效決策與授權私人記憶形成小型開工閱讀順序；不另建平行主檔。開工以任務/目標/最新 source/有效決策/必要角色技能及相關 1–3 EP/真工具權限/下一成果為可查的最小證據。明示且允許保存的回饋即分類：持久偏好、專案規格、此次例外、工程候選經驗、禁止/安全；就原權責位置增量寫入、回讀、回覆實際保存位置；私人偏好只能在授權私人位置或原對話。可採原蒸餾機制定期精簡有效條目，保留歷史，不用日期自動覆蓋安全或專案正式規格。結案查實際讀/採用/拒絕及正負測，下一不同任務用實際成果驗生效；缺來源獨立性明示。P0 先核是否已有功能、修訂不一致／增加最小回歸、以真正不同任務核執行遵循，P1 教材並行；不增管理引擎。
C. 完整複製原範本的文件結構或強迫本機工作台（不建議，環境/保密/工程需求不同）。
本輪僅對照與提出建議，沒有批准 B、修改運行規則/技能、設定私人工作台、修改教材矩陣、執行新訓練或部署。P0/P1 優先仍依 TD-005-R2，原 A07/B10/M3-2/M4 與安全授權保留。


## TP-010｜確認及增量實作（2026-11-17；CONFIRMED / P0_IMPLEMENTED_PENDING_CI）
- 使用者明示採用 TP-010 改善方向：開工必讀、使用者工作記憶、日常回饋、知識蒸餾、真實運用，P0-1–5 原機制增量、正負測及跨任務，P1 同步、不建重複主檔或管理引擎。原基準 1a4801f52f06663633d9558046424ac9a7e6f391，CI 44023083755 success（metadata）。實讀原 catalog、workspace code/既有測試、適用角色技能及 R2 正式決策。
- 原 remember/feedback（候選）、distill/resolve（人工衝突）、case context/cite/history、PM 兩次停點均保留。實際缺口：舊 _context 所有記憶經 lexical filter，明示有效偏好可在新無關任務被漏；部分文件殘留舊交付優先。新增原 _context 的 work_preferences（唯一、active,user-stated、private workspace）、preference_review 衝突 ID、omitted_work_preference_ids/NEEDS_FULL_READ；不變 schema/table，不跨 workspace/公開讀取或新增管理引擎。修原啟動、共同規則、相關角色與技能；未增加新角色/skill。既有 PM 停止規則足夠，工具可達性/證據 guard 用原共同規則，下一真任務核落實。
- 新原測試兩方法涵蓋無關 task/skill/query、新 subprocess、另一私有 workspace、衝突、候選不可覆蓋、resolve/退休、預算及公開界線。未執行新 CI 前不稱測試通過；container DNS 無法取得 GitHub checkout，未聲稱本機真紅綠。實際 LLM 跨任務遵循及來源獨立 A07 待證。P1 已定位原八章備份與目錄，讀 1.1.1/1.2.1/2.2.2/2.2.4 文字（圖片/嵌入未齊），待 P1 獨立矩陣工作；不寫私人 Drive、原文或個資。R2/未驗門檻/NT$0 維持，不改 main/APP/workflow/release/Pages branch，不接管外部專案。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK。


## TP-010 / TD-004｜P1 真教材來源、逐單元主責與首個實作（2026-11-17；INVENTORY_ASSIGNED_PROVISIONAL / TEXT_PARTIAL / SQLITE_LAB_RUN）
- 原八章備份與課程總目錄已實際核讀/列出；176 目錄 ID 順序與原 matrix expected_ids 完全一致，163 個檔名/ID 一一符合、0 重複、0 額外/題名不符，缺 13：4.1.7、4.1.8、7.6.1、7.6.2、7.6.4、7.6.5、7.6.6、7.6.7、7.6.8、7.6.9、7.6.10、7.6.11、7.6.12。原 inventory pin 保留；不公開私人 Drive URL/原文。唯一原 matrix 擴增 176 個初步主責/skill，依章節標題與現有專業分工（{"system-lead":1,"architect":14,"devops-sre":28,"learning-evaluator":6,"security":11,"developer":112,"qa-uat":3,"project-manager":1}），並非正文驗收；13 BLOCKED_SOURCE（備份缺，原網頁個別未驗）、159 UNREAD、4 READABLE（僅已取得 Markdown 文字，connector UTF-8 回傳字串 SHA256 pin，非含圖或原檔獨立 byte hash），全部 L0，PARTIAL；大多依賴未核，不宣稱無前置，逐章正文再確定。所需 2.2.4 前置暫列 2.2.2/2.2.3，現未就緒，不升級。4 份 pins：1.1.1=da2b48fa86fe4f98e3b66d1ec3f593571c550f6326deca36da7a7186788a6dca；1.2.1=ff3bd10434657ac02995221297bb28bf9d508686198b9d4bd9b91827ee6e9c49；2.2.2=1d6365fe0a9ab6980d5a68a13678eb5064c92143ea932bd98f681af8c6d6a180；2.2.4=cca380edfdea316ccdf35bb0da21a5ac74600c7bf10c305275267e9f418f436e。
- 1.1.1 文字說明由資料儲存→程式邏輯→網站→應用擴展，資料庫/OOP/MVC/API/行動；1.2.1 部分正文覺察持續學習、單技術→最小案例→整合；2.2.2 文字對應自然/代理鍵、流水號/GUID 與關聯遷移；2.2.4 完整 Markdown 文字對照 NULL≠0/空字串/false、IS NULL、運算未知、預設值與 SQL Server ISNULL/NULLIF。圖及嵌入未核（2.2.4 三圖與嵌入嘗試均不可讀），未宣稱完整七階段。前 3 章未實作。原資料工程 export lab 已測 missing≠zero/CSV，故本次只測不同的 SQL 聚合、predicate/default/資料未知語意，不重跑原 lab。
- 2.2.4 主責 Architect、Developer/QA 協作：教材一般非空數值/預設值建議不適用所有研究測量；語意由研究規格決定，未知不自動變 0，需區分未收集/不適用/有效零；SQL NULL 的三值邏輯與 aggregate 排除作用不能把 default 當科學補值。SQLite 3.46.1 實際 in-memory unittest 1/1 OK、12 個斷言（含完整負測）：三筆 score=0,NULL,12，COUNT(*)=3、COUNT(score)=2、AVG(score)=6、錯誤把未知歸零為4；IS NULL vs =NULL、NULL arithmetic/NULLIF、未提供欄位 default 0 與明示 NULL 不同、NOT NULL 主鍵拒絕。不同容量情境驗 unknown/full/open：只 full=0；unknown 另外；COUNT/SUM 排除 unknown、全 missing 的 SUM 保留 NULL。實作 class 原樣加入既有 test_research_data.py，未重跑原 10 個方法、不是 SQL Server 實機/科學效度/真人 UAT、非獨立陌生 LLM 遷移。下一步補原圖、2.2.2/2.2.3 依賴、真 T-SQL 差異再判成熟度；不以此局部實作越級。
- P0 code commit 850ec9053d614b40f91c979d2165fafc7c2a6ad4 CI 44024244762 本輪查時 in_progress；待 exact raw log、讀回與不同真任務的遵循證據。P1 獨立前進、R2 不受 Pages/首版驗收阻塞。未改 main/APP/release/workflow/外部專案、未增費用或發布。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK。


## TP-010｜P0/P1 實證回讀（2026-11-17；P0_PROGRAM_REGRESSION_VERIFIED / REAL_TASK_TRANSFER_PENDING；P1_INVENTORY_ASSIGNED_TEXT_PARTIAL）
- 真 P0 commit 850ec9053d614b40f91c979d2165fafc7c2a6ad4/tree 2ae5ff18d324ec0e6fe5a8e55082154f4dbfcf00，CI 44024244762/job133840663624 全步驟成功，原始日誌 257378 chars：test_confirmed_work_preference_across_unrelated_tasks、test_preference_conflict_candidate_resolution_and_budget 兩方法 ok，Ran 519 tests in 74.866s / OK；checkout c4e07c16b4f0723548d479c8ff7d07fdea0d243b 真 GET parents main+P0、tree 完全相等，report marker SHA256 35d3a99380fde07a4c54737f40a18aef823a5a4addee7e50609dde8b35ee5526。原 517 tests 保留；未有獨立 LLM 前後盲測、私人真工作台啟用或 A07 source-only 證據。
- 真 P1 commit baad08299c37665c8be82355de5157d576c47f97/tree 0e4b20783218b50685d1b1f4a81e2a2f52400bfd，CI 44024463577/job133841381872 全步驟成功，raw 257380 chars，test_live_matrix_valid_during_future_progress 與兩新增方法皆 ok，519 tests in 71.678s / OK；checkout 21f06008e235b01743e897d65fc2c590c181e1f9 parents main+P1/tree 完全相等，report marker SHA256 24c1fb1a6dfbcb747c88717e62cfdf75c6654988f58d0a034de137569707a71c。矩陣結構驗證非教材源完整/實力證明；review lab 另外在 container SQLite 3.46.1 實際執行新增 class 1/1（12 assertions），非 CI discover 的測試，不把 519 冒稱重跑該 lab；原無關 10 tests 不重跑。
- 遠端 P0 14檔 diff、P1 5檔 diff；合併 16 個原檔 blob/完整 recursive tree 回讀 16/16（truncated=false），主檔/決策/覆盤、matrix/source/test/lab 7 份全文工具另讀。main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57、Pages v1 b732a50171aacebfab6d99b34c8568bb6dc0ea0d 不變；repo API 真讀 has_pages=false（未由 Agent 寫 Pages、無 owner UI 獨立證據，URL 失效未驗），保留分支、C4 partial/C5/C6 not run/A07/B10/M4/3-of-6，不要求重新部署或真人測試、不影響專業學習。先前兩次 Code Mode 呼叫上限在 ref 更新前中止，真查舊 head 不變及 commit/parent/tree 再一次 CAS 快進，非盲重送；不聲稱原本地 checkout 可用。此補證為紀錄更新，不把原程式 CI 冒稱新文件 exact CI；保留真 SHA，不因每個證據文檔追加而無限重跑。
- 下一步：P0 程式跨不同 task/skill/query/subprocess/SQLite 隔離及衝突驗證完成，真正 LLM 在新真任務的遵循與遷移仍待證；P1 先深讀依賴與可完整取得的不同教材單元，媒體/缺檔阻塞僅限單元。原 176 初步分工按題名須正文核對，不認證 mastery。保留 NT$0、R2、原角色/技能、無額外排程或外部專案授權。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK。


## TP-010-AUDIT-01｜原團隊範本完整功能對照（2026-11-17；AUDIT / PROPOSED）

### 來源、方法與限制
使用者明示要求完整稽核原九技能、共享目錄、品牌手冊、學習及覆盤對照現八角色十五技能，保存差異分析，不公開私人資料。實際重開原第一天學員包的啟動說明及 AGENTS、九個 SKILL：brand-handbook、case-card、learn、threads-research、pick-topic、write-posts、check-post、make-cards、plan-week；逐項取得 17 個 references（訪談問題/產業紅線、案例卡/靈感庫格式、選題庫/筆記/報告/受眾庫格式、選題卡格式、開頭/寫法/寫完自檢/四種目的、紅線詞/檢查表、任務單/每週覆盤格式）和一個 HTML 圖卡 asset（靜態讀取，未執行）。原八共享目錄已各列檔；讀取市調、產物、週任務、案例四份通用說明；品牌手冊只檢查十章結構，不保存個人內容。原資料夾目前已含使用者工作資料，未讀真個案/留言/貼文/私有素材內容、未審實際發布成效、未修改原範本。公共 repo 僅保存以下原創概念差異與工程證據，無私人 Drive 連結/識別碼、手冊填值、帳號、原文/程式/圖或臨床資料。原範本精確私有來源由本輪對話及授權原目錄追溯；本報告不是授權搬運教材。
候選基準 49b2ffaa72e285aad7493900207d7f431e7201e6 / tree 2c6df2da8b25fd147d5c574a7368666bc720a518。讀 START_HERE、AGENTS、最新正式主檔/決策、catalog（1bc4f3711237694b4bb82f3c38e100ac143d9d03）、TEAM_WORKBENCH（1d84ea8a845b7f916c9366111cf257f9223f9ce0）、八角色、15 SKILL 與總入口 reliable-system-builder（不另計第16核心技能）、workbench 三原程式的可用函式及前輪已讀實作、EP 索引、原 11/16 research-handoff 15技能/28方法盤點。非全程式逐行資安審查。最新 CI 44024790864 job133842415564 28/28 steps success，raw 257377 chars，519 tests in 80.829s，實讀 18 個判定方法各恰一 ok（含兩 TP-010、matrix），真 Chromium RESEARCH-METHODS 375/1280及 editorial；checkout 3d4c2fd7a876ee6fde05c2be47f248cb7d9f84e8 parents main+基準，tree 相同，marker adc70fa25733a3823c2ddfd1c805092f8e5c288b7e00539cf5bbcb00c3877cde。未重跑測試、未下載 CI artifact；本次是來源與既有證據稽核。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK。
四狀態：A 已落實（具實際可核操作或受控程式證據，注明層級）；R 僅有行為規則而缺相應證據；D 已實作但目前日常環境不運作或無常態證據；M 未發現對應完整功能。域外功能標不適用而非缺陷。各功能可同時有 A/R/D，不將 evidence entry 等同成熟度。

### 九技能逐項（原技能名稱僅用於來源索引）
| 原技能 | 工程對應 | A 已落實 | R/D/M 及取捨 |
|---|---|---|---|
| brand-handbook | Lead project-intake、Architect requirements-spec、PM project-scope、Evaluator learn-from-feedback | 13題、明示/推導/未決、可編輯審閱、scope前置及 TP010 preference 正反測 | R 共同開工必讀；D 私人偏好日常持久化；M 工程版一次訪談、可人審的可用工作輪廓（在既有授權位置，不要新台帳）。原英雄旅程/受眾行銷不照搬。 |
| case-card | Evaluator learn-from-feedback、Developer debug-and-repair、Security security-review | 原工程 case、EP、事故/修復及真紅綠；feedback candidate 去重 | D 私人案例常態新增與採用；R 同次回饋分類/原來源追溯；M 真實個案的公開同意流程不移植到工程。工程需另核資料及去識別。 |
| learn | Evaluator learn-from-feedback、knowledge-distillation，Lead resume-project | remember、distill、resolve、case context/cite、跨程序及偏好衝突；原 EP 蒸餾 | D 私人偏好長期運作及下一真任務採用；R 每次收藏/回饋及精簡落實；M 持續收集已授權真使用回饋→有據改善→後續成效的完整閉環證據；無自動事件監聽。不採新日期一律勝出。 |
| threads-research | Architect architecture-design、Lead project-intake/task-planning、Evaluator knowledge-distillation | 原官方技術探索、平台選型、教材盤點、證據及限制；公開 case 索引 | R 真任務按來源找案例、適度調研；M 跨任務的已驗技術問題→候選改善自動或常態回流、用統一真使用回饋來源生成待辦（可用原池，不必自動化）。社群搜尋/七題/六類受眾不適用。 |
| pick-topic | PM project-scope/project-control、Lead task-planning/resume-project、Architect requirements-spec | 工作包/需求識別、DAG、current/revision、失效及未決阻塞測試；主檔 NEXT_ACTION | D 私人任務池日常持續領取；R 按真實來源選下一項並採用相關經驗；沒有必要複製選題卡或另建 active pointer。 |
| write-posts | Developer implement-feature/debug-and-repair、Architect requirements-spec、QA test-and-acceptance | 真 APP/CRUD/HTTP/SQLite/PG、red-green、需求改版失效 | R 跨真任務依長期偏好修改最小範圍；D 私人偏好回流。三種貼文/固定行銷格式不適用。 |
| check-post | QA test-and-acceptance、Security security-review、PM delivery-review | 真 DOM/CSV、負向oracle、RLS/ACL、版本及真人gate | R 新情境原有效規則採用；未完成真新手 B10、真人UAT、外部遠端/獨立模型；原發布同意不可降格成一般自述。 |
| make-cards | Developer implement-feature、Architect architecture-design、QA test-and-acceptance | 已有可操作 HTML 教學 APP、下載 CSV、可編輯規格UI、真 viewport/DOM | M 通用可重用、資料與呈現分離的視覺/報表模板交付能力尚未證成完整功能；現有樣板可按真需求深化，不搬原 Canvas/PNG、外部字型依賴，不新增展示APP。社群圖卡不適用。 |
| plan-week | PM project-scope/project-control/delivery-review、Lead task-planning/resume-project、Evaluator learn-from-feedback/knowledge-distillation | 原池和 revision、阻礙隔離、決策、CI及專項覆盤，原真偏航已保存 | D 私人任務池及事件長期運作；R 按工作成果覆盤；M 原任務/實際使用回饋/可比工程效果/決策後下輪驗效的常態閉環，未見正式週期成效流程；優先從真工作事件實施，非新增週報或排程。 |

### 八角色十五核心技能反向核對（A 是局部工程證據，不是完整角色成熟）
| 主責/技能 | 原範本功能 | 最新真 CI 方法（test_ 前綴）或原實證 | 剩餘 |
|---|---|---|---|
| PM project-scope | brand-handbook/pick-topic/plan-week | pm_handoff_reuses_workspace_and_stale_scope_blocks_delivery | R 真新專案協商效果/科學規格 |
| PM project-control | plan-week/pick-topic | revised_requirement_invalidates_downstream；真本案 R2 止偏航 | R 真持續遵循停點；D 日常私人池 |
| PM delivery-review | check-post/plan-week | release_with_all_green_still_requires_real_uat_and_human | R 真交付使用回饋與獨立UAT待證 |
| Lead project-intake | brand-handbook/pick-topic | bootstrap_13_questions_6_examples_prefill_no_gold | R 長期工作輪廓訪談；B10待證 |
| Lead task-planning | pick-topic/plan-week | conflict_and_competition | D 真工作隊列常態；R 避免重作採用 |
| Lead resume-project | pick-topic/plan-week/learn | real_content_handoff_and_resume；本輪實讀GitHub | D 私人接續；A07 source-only待證 |
| Architect requirements-spec | brand-handbook/pick-topic | all_six_exports_apply_edits_and_exclude_rejected | R 陌生真需求/工作偏好適用 |
| Architect architecture-design | threads-research/make-cards | pg_shared_migration_preserves_v1_history_and_old_contract | R 真跨平台取捨、完整教材 |
| Developer implement-feature | write-posts/make-cards | academic_app_real_browser_and_download | R 真跨任務最小修改；M 通用模板能力未完整 |
| Developer debug-and-repair | write-posts/learn/case-card | http_framing_incomplete_valid_json_has_no_mutation | R 真新事故案例採用及避免重犯 |
| QA test-and-acceptance | check-post | ci_must_match_exact_code_and_test_sha；真DOM | R 獨立真人與實體環境、真任務 oracle |
| SRE deployment | check-post/plan-week 的交付界線（工程新增） | matching_files_and_identity；C3 歷史真部署 | C4 partial、C5/C6未驗；R 工具預檢 |
| Security security-review | check-post/case-card | pg_shared_identity_rls_function_acl_and_foreign_cancel | R 真雲端身分/實際研究資料治理 |
| Evaluator learn-from-feedback | learn/case-card | feedback_candidate_and_dedup；confirmed_work_preference_across_unrelated_tasks；preference_conflict_candidate_resolution_and_budget | D 私人日常；R 真學習遷移 |
| Evaluator knowledge-distillation | learn/plan-week/threads-research | learning_dedup_conflict_review_and_history；test_live_matrix_valid_during_future_progress | D 私人精簡；M 真成效回流閉環；L0矩陣不得當學習完成 |
八角色指令成立，非八個實際員工程序；原第一天範本的三位員工也是文件角色，未獨立核其 runtime。現 Agent 的總入口不算第16核心技能。八角色的共享資料/產物合同優於單純固定格式，但人類實際工作結果尚未普遍驗證。

### 八個共享目錄與品牌手冊十章
| 來源目錄序號/用途 | 對應原工程位置 | 狀態與缺口 |
|---|---|---|
| 01 使用者脈絡＋收藏 | 原主檔有效決策、AGENTS、private remember、EP | A 正式決策/偏好測試；D 真私人記憶；M 統一可讀工作輪廓與真採用閉環 |
| 02 原始調研、報告、選題庫 | reviews、工程索引、原工作包與可選 tasks | A 真原工程證據、D 私人池；M 真使用問題回流尚未完整 |
| 03 當前題目與交付產物 | 原 repo spec/code/test、commit、artifact、current/revision | A 真交付與版本、D 私人 handoff 常態。不要另建副本 |
| 04 週任務/覆盤 | 原主檔 NEXT_ACTION、PM紀錄、reviews、workbench_tasks | A 進度與專項覆盤、D 私人池；M 可比真成效回流閉合 |
| 05 產業知識 | EP、原技能、curriculum matrix | A 工程索引與結構，教材深度未完成；R 每次採用 |
| 06 真使用者原始回饋 | 原需求/驗收/工單、明示回饋 candidate | A 需求/測試機制、D 私人 feedback；M 多真任務的具來源回饋與採用結果閉環。不得移入真人資料 |
| 07 一事一案例 | CASES/TRAINING_CASES、EP、原 reviews | A 原案例及真證據，D 私人 case/cite |
| 08 發布後成效 | 原 CI、真 deployment/驗收、PM進度、reviews | A 工程驗收紀錄；M 可比真使用效果/重工/人工負擔資料與後續效果驗證，不需通用儀表板 |
手冊十章對應：1定位→TD005-R2/START_HERE（A）；2服務→catalog及授權界線（A）；3個人旅程→不適用，工程案例歷史（A）；4三層受眾→研究/教學使用者需求（R、真需求依個別spec）；5三大支柱→專業能力/可靠交付/安全（A契約與局部工程測試，非品牌宣稱）；6語氣→工作偏好/人機協作（R/D）；7紅線→AGENTS/policy/安全gate（A）；8素材→原案例/EP（A）、私人收藏（D）；9未知→BLOCKERS/NEXT_ACTION/未決（A）；10學到的事→DECISION_LOG/原技能/私人記憶（A公開決策、D私人日常，M跨任務成效閉環）。不保存原手冊任何個人填值。

### 學習、成效與優先改善（建議，不變更現決策）
原範本明示回饋即記、逐次先讀、定期精簡、收藏觀察/因地制宜/原理、個案與受眾反饋轉任務、發布後固定時點對比與覆盤調整。重點是以真資料改下一次工作，不是增加關卡。TP010 已修偏好漏檢且真 519 PASS，不重寫；公開正式決策已在本輪真接續（history-assisted，不是 source-only）；私人工作台已有實作卻未常態使用。原 20 行提醒、每類上限、以日期直接取代衝突、特定行銷觀測窗/樣本或流量倍數只適用來源情境，工程不可照搬；需保留安全與歷史、同一口徑的可比較真任務結果。原範本本身存在操作文字不一致：總說明要求改稿記語氣段、write-posts指定學習段；案例目錄說明與 write-posts/check-post 對未同意案例草稿的使用有差異；不把原規範當獨立執行事實，也不移植對臨床資料的例外。圖卡 asset 有外部字型請求，不能假稱完全離線，不複製至研究APP。
建議 A（優先，沿已確認 TP010/R2）：下一個已授權真任務中最短讀取原有效決策/必要skill/EP並展示採用與結果，記本輪返工或人工介入、原因及下一任務是否改善，只用原 decision/review 或既存私有位置；不造新任務池/評測器/儀表板，不再代替正常專業學習。建議 B（有真私人位置及授權才做）：在原私人 workspace 完整保存/讀回通用工作偏好並以不同真任務驗證；沒有現成位置不要求安裝或公開。建議 C：持續教材深度路徑，現176初派/4文字/13缺、L0保留，先依最新 NEXT_ACTION；新缺才改善必要技能。尚無真陌生任務、自動週期覆盤、獨立多代理/模型增益證據；不得用程式測試、CI數或原範本資料夾存在證明常態成效。僅本次稽核及記錄，未批准/執行上述新功能、未新建任何台帳/排程、未改APP、code、main、release、Pages 或其他專案；R2專業能力最高優先及原未驗限制不變。


## TD004-DB-KEYTYPE-01｜資料識別、型別與時間語意（2026-11-17；TEXT_PARTIAL / SQLITE_LAB_VERIFIED）
使用者確認依 TP-010-AUDIT-01 持續原教材專業訓練最高優先，開工記憶、案例採用、回饋與覆盤融入每次真實工作，不另建管理機制或知識庫。此為延續 TD-005-R2/TP-010，不變其他決策/權限。基準 d8f901c7c43232c8bc499b09e642b4a7feae0d19，前次稽核 CI 44025868696 job133845937709 全28步成功；實讀 raw 257378 chars，519 tests 75.421s / OK，TP010兩方法及 live matrix ok；checkout de00c202775c5d29ac5bd5d118f9a76487a21b13 parents main+基準/tree 861fbc6b1f3bb5468ddda9fd3349f971af7f73de 相同，marker 89398818402f65644d2394c0fe221b1ecf96289606bfeee8fff192fdfeb1821c。未新重跑519。
開工實讀 START_HERE、AGENTS、主檔、決策、audit、matrix/catalog、Architect/Developer/QA/Evaluator 角色及 architecture-design/implement-feature/test-and-acceptance/knowledge-distillation；查 EP-01/13 與原研究資料測試。採用 EP-01 的來源語意與穩定ID、EP-13 的原生約束/遷移一致性與真負測，擴展為兩獨立 SQLite 資料庫之間有效 FK 卻語意錯接的問題；不用原PG shared容量/權限、空值或字典匯出 lab 重做，不將 source ID 規則等同 DB PK。本輪為 REPO_NATIVE / SINGLE_AGENT_ROLE_WORK；無私人工作台/獨立模型。
原授權備份實讀 2.2.1/2.2.2/2.2.3/2.2.4 Markdown 全文字，另初覽2.2.6–8的標題/媒體數，未稱讀完後者。2.2.1 pin 66988112c36bf9d359ff3a85a8582f0642af41afd91d56250af19755bdf9f6a0 (新)，2.2.2 1d6365fe0a9ab6980d5a68a13678eb5064c92143ea932bd98f681af8c6d6a180 (原 pin 一致)，2.2.3 44bb92fd6ffc2f4131ef708840f69d3e631c1608d76ef56c0c79b16e27ea798a (新)；pin 是 connector UTF-8文字，非原圖/原始檔 bytes。原 HackMD 2.2.2/3/4 pages、2.2.2/3各首要圖、共用 embed 實際開啟失敗；未逐圖聲稱全失敗，原圖15+14及必要內容不完整，保留 L0；2.2.4 仍沿上次已跑，不重跑。原教材不公開轉載。2.2.1/3 matrix READABLE（已取文字），共6 READABLE/157 UNREAD/13 BLOCKED_SOURCE；全176 L0、PARTIAL。
### 原理與批判（源位置為原 matrix 的公開 source_url）
- 2.2.1 §1–5：一致、可辨識的資料表/欄位命名可減少語意錯配；原 ASP.NET Core PascalCase 複數是特定框架慣例，非所有 DB 必須統一該風格。不批次改既有 schema/API/ORM，必要改名先核依賴/版本。命名不能取代單位、值域、唯一約束、外來鍵與資料字典。僅正文分析，未測命名。
- 2.2.2 §1.2/2/3/4：自然鍵與代理鍵、流水號與GUID、流程及階層跨庫、三種 T-SQL DDL。教材偏好整數及跨系統GUID、文字 GUID 方便轉換；本輪取捨：內部整數、跨庫穩定識別及業務唯一約束可共存；GUID 的不可預測不等於授權，唯一約束仍必要；自然鍵穩定時不排除，業務鍵修改與 PK 分離。錯接即使 FK 合法也可能發生；以源穩定識別及目的映射核語意與關係。SQL Server 原生16-byte uniqueidentifier、NEWID/NEWSEQUENTIALID、字符串轉換可能截斷：實讀 https://learn.microsoft.com/en-us/sql/t-sql/data-types/uniqueidentifier-transact-sql?view=sql-server-ver17 ；不能僅為顯示便利偏好 nvarchar，亦不能聲稱 GUID 永無衝突或順序必為時間；原 §4.3 DDL 有多餘 >，不照抄執行。SQL Server 索引效能、排序及分散式生成未測。
- 2.2.3 §2/3/4：文字/數值/時間型別，decimal(p,s) 意味總位數與小數位數；教材偏好 int/bit/decimal(18,4)、datetime2，查詢以日期與時間分界。實讀 Microsoft https://learn.microsoft.com/en-us/sql/t-sql/data-types/decimal-and-numeric-transact-sql?view=sql-server-ver17 （降精度可能四捨五入/overflow）、https://learn.microsoft.com/en-us/sql/t-sql/data-types/datetime2-transact-sql?view=sql-server-ver17 （合法全天範圍23:59:59.9999999、0–7小數、不保存時區；100ns表示精度不保證物理時間）、https://learn.microsoft.com/en-us/sql/t-sql/data-types/rowversion-transact-sql?view=sql-server-ver17 （SQL Server timestamp 是已棄用 rowversion 同義字，非日期時間；更新版本不能當研究時鐘）。原文 datetime2 時間範圍表一處缺2，另表正確。不能一律固定 decimal(18,4)；依核定範圍、精度、單位、語意選型，非統計測量一律改整數。非數字識別碼保留文字及前導零；確切金額/定點數避免浮點誤差。用明確時區、起點包含終點排除的區間，勿把目標日午夜當成包含整天；UTC轉換、DST、精度與時間格式需另驗。SQLite 的固定格式 UTC字串比較/縮放整數並不是 SQL Server datetime2/decimal/rowversion 的等效實作。無 SQL Server/sqlcmd/PostgreSQL executable/docker 本機環境，不付費、不安裝或外部部署。
### 真執行、正反例、不同用途及交接
自寫 class IdentityAndTypeLesson，加入既有 test_research_data.py；本機真 SQLite 3.46.1 以獨立暫存 Python 檔執行 python -m unittest -v lesson.IdentityAndTypeLesson，2/2 OK, 0.002s（非效能基準），17個 assertion code sites，含兩組 subTest 重複/非法值；本機 class UTF-8（含末尾換行）SHA256 e44f9baf8b5cc0c87b62cfb0c313048a6c0a154d5596a7e06c451026f906a011。無重跑舊 lab。
1. 兩個真正 SQLite in-memory DB 開 FK，來源 local1→source-A；目的 local1→other-B/local2→source-A。刻意不良轉移後 FK check=[]，但 join 得 other-B（固定錯誤結果）。以來源 stable_id 映射 destination local2，join 得 source-A；業務 code 001→003 仍連正確項。兩種唯一衝突及孤兒 FK 拒絕；比較 item snapshot 與 FK check。此為自建故障示範，不是原產品 bug/L4。
2. 在不同型別與報表情境，legacy INTEGER 使 '001'/'1' distinct=1；REAL sum(0.1,0.2) 不等於0.3；新 STRICT 表 TEXT + 以小單位整數 + 範圍 CHECK，保留3個不同代碼。固定UTC日窗使用 BETWEEN 含次日午夜，SUM=70；[start,end) 精確兩筆 001/1 合計30，排除40；四種非法 amount（-1/1000000/10.5/NULL）拒絕、snapshot unchanged。SQLite STRICT 可做無損 coercion，未驗拒絕所有數字字串/bool 或一般 timestamp valid dates/time offset，不宣稱通用 API validator。兩情境皆公開合成、非真人資料/真外部專案、非盲測或獨立LLM遷移。
Architect 主責：設計取捨及語意；Developer：自寫lab；QA：固定期望資料行/計數及負測；Evaluator：原matrix/skill/覆盤增量。原技能 architecture-design/test-and-acceptance 加入識別映射、日期邊界及試算表/語意限制，原 evidence/EP保留，不建新資料庫/管理 engine，不更動產品或 CI。新增技術原理的局部實證，教材圖片/前置與真T-SQL未齊，不達完整七階段；未將L0改成L3。
### TP010 工作成效覆盤
本輪實際採用最新 R2 與稽核決策，不再做 Pages/UAT/工作台改造或空值重跑；舊案例只作相關原理導航，用新情境驗證，沒有要求使用者提供人工操作。一次 SHA 自檢失敗於寫入前停止，改用原已驗 hash 算法並核 abc 和2.2.2既有pin；不計作產品錯誤或專業程式缺陷。兩組lab首次執行均pass，沒有編造red修復；0本輪人工操作請求、0既有lab重跑，無同難度基線或長期使用回饋，不能宣稱已降低工時/證明模型進步。下一輪以2.2.7正規化或獨立完整可讀正文為優先（先核必要依賴及原實證），原2.2.2–4補圖/真T-SQL待取得環境，不用相同方法無限重試。P1專業為主；保留 A07/B10/C4–C6/M4、3/6、NT$0、無真人資料/外部部署/正式發布。


## TD004-DB-NORMAL-01｜正規化、依賴與關聯生命週期（2026-11-17；TEXT_PARTIAL / SQLITE_LAB_VERIFIED）
依使用者本輪明確要求及 TD-006 核心準則接續原專業訓練，不重建管理架構。基準 3978a8f3d66e7186eba9bee962bfda10437adf4d / tree f314f64b10b503ad08040525c3f6336c76d8524d；CI 44042533418 job133900302699 全28步成功，原始log 257385 chars，519 tests in 74.741s，matrix及TP010跨任務偏好方法ok；checkout 21a420783d6f64e650972b04fd140982a13cf5d3 tree一致、基準為parent；marker 1ebbb228280fcbf54758a251fd4af86a5d2dc49061a5d6336ca5e83072f98d0c。不是本輪新實作的CI。
開工實讀 CORE_TRAINING_PRINCIPLES/START_HERE/AGENTS、唯一主檔、有效決策、matrix、原覆盤、catalog、Architect/Developer/QA/Evaluator角色與對應 architecture-design、implement-feature、test-and-acceptance、knowledge-distillation 技能，核原研究資料實作及 EP-05/EP-13。採用 EP-05 固定來源版本與舊成品不冒稱新版本、EP-13 遷移保留原歷史/原生約束及負測；延伸不同之資料依賴與歷史版本關聯；不重跑識別碼、NULL、既有PG遷移/權限/容量。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，未啟用私人工作台或獨立多代理。
原備份 2.2.7/2.2.8 Markdown 正文及文字SQL範例透過授權來源實讀（9592/24684 chars），UTF-8 connector 文本 SHA256 1533af2a5ab3be071489efe4faa1bebaf25e4d0d23a890b6d3a4706ad7b6aa48 / 0e6dfc5846eb877119f74230c1e08bac552480d89f76d5aefd884ac9546f960f；各20/44圖及共用embed未取，不冒稱完整圖示或教材實機，原矩陣8 READABLE（文字）、155 UNREAD、13 BLOCKED_SOURCE，176單元L0保留。原 source_url 不變；不公開私人位置或原文。
原教材2.2.7 §2–3 三類資料異常、1NF單值/重複群、2NF部分依賴、3NF遞移依賴、BCNF；§4–6 OLTP以3NF起步，分析場景可衡量冗餘/物化/快照、索引優先；§8圖示未讀。批判與延伸：正式定義以所有候選鍵及功能依賴為依據（BCNF非平凡FD的決定項應為超鍵，不限最小候選鍵；3NF允許右側prime attribute例外）。教材訂單單價若代表當時成交值而非目前產品定價，不應拆回現行價；同理研究事件ค่、版本及報酬依事件語意獨立保留。拆表須核無損接合與依賴保留各自成立；BCNF無損分解可能不保留原依賴。1NF及4NF/5NF只讀概念，未做各自完整實驗。未做負載benchmark，不推論JOIN必慢或快照零影響；先核查詢計畫、負載、索引與容許延遲，再決定衍生資料、更新/失效與對帳，不以冗餘當權威。
原2.2.8 §2–4、7–9：一對一用唯一/PK外鍵，多對多以中介表與複合唯一性；NO ACTION 預設、CASCADE僅適宜生命週期、SET NULL選擇性關聯、SET DEFAULT父記錄需存在。§9 No/Id為依情境指引：刪除重建同No可能錯連不同實體，FK阻止刪除或明確復原更安全；業務號碼可在核定範圍內唯一，並非一律不可作FK；唯一鍵可作父鍵。分表不等於存取控制；FK也不保證應用可刪、不可變或符合研究倫理。SQLite官文 https://www.sqlite.org/foreignkeys.html §4.2–4.3 實查，NO ACTION不執行額外動作但仍檢查FK；RESTRICT即時，延遲約束於提交檢查，與SQL Server實機分開。FK索引按查詢、已有複合索引和寫入成本，非機械重複加；SQL Server DDL/GUI及原圖未驗。
### 實際訓練
自寫 NormalizationRelationLesson 原班級加至既有 test_research_data.py，真SQLite 3.46.1 隔離記憶體DB，python -m unittest -v lesson.NormalizationRelationLesson 3/3 OK (0.006s，非效能基準)，21 assertion sites，首次即pass，不造red/fix。原暫存class(末尾換行) SHA256 e68489d322ed2583f2d8ba0795b880705f61dd5782301197d73841e1224a1e9d。原有lab未重跑。
1. 合成研究參與平表：更新單筆造成同protocol標籤2種，無參與者不能插入獨立方案，刪掉最後所有參與列失去方案。拆 unit/protocol/person/participation，固定原行內容核join還原，修改protocol label及unit name各一次兩列正確同步，amount_at_event 100/120不受影響；無參與者的新方案可存在，刪全部參與列仍有R1/R2。此為示範部分/遞移依賴與異常，未證所有候選鍵/1NF或原資料移轉完整性、事件值不可修改。
2. 合成教學規則 (learner,topic)->mentor、mentor->topic，候選鍵(learner,topic)/(learner,mentor)。BCNF拆 mentor(topic) 與 assignment(learner,mentor)，join 原兩列；共通mentor鍵使拆解無損，但新增同learner/topic第二mentor可通過所有局部PK/FK，查 group 顯示 L1/T1 重兩筆。保留3NF關係的PK(learner,topic)可拒絕該寫入，仍需另外強制 mentor->topic；未把示意表當完整可用修復。依據業務規則與依賴保留選型，金融/研究不能為形式升級犧牲真實約束。
3. 合成研究版本複合FK：run10引用R1v1、run11引用R1v2，新增v3不變舊join；NO ACTION 拒刪被引用v1、拒引用不存在v99；CASCADE只示範run刪除後附屬可丟棄draft移除（不表示研究run可合法刪除），版本仍三筆；可選tag刪除令annotation FK=NULL而保留行，FKcheck=[]。此不限制任意UPDATE舊版本、run 刪除或可信writer，也不等於研究倫理/正式刪除政策。需後續依權限、不可變版本契約、稽核政策驗證。
### 蒸餾與覆盤
把新原理增量寫 architecture-design、test-and-acceptance：功能依賴、歷史事實與現在主檔語意不同、無損/依賴保留、生命週期及安全，保留原來源版本/案例及成熟度。無新增工作台、知識庫、角色、APP或外部服務。依核心準則本輪專業成果3方法21斷言，新案例未替代真外部任務；0人工操作請求、0舊實驗重跑，無可比較長期工時或真人成效資料，未宣稱模型能力增益。原兩單元圖像缺件沿既有已知限制，只保留待證，不再次重試相同失敗途徑。下一輪2.2.6索引（先查原已驗 query plan 路徑，測不同複合索引/查詢型態），個別圖/前置受阻改可完整取得教材。安全優先，保留 A07/B10/C4–C6/M4及首版3/6，NT$0；不部署、不改main/release。


## TD004-DB-INDEX-01｜索引設計、實際查詢計畫及讀寫取捨（2026-11-17；TEXT_PARTIAL / SQLITE_LAB_VERIFIED）
依使用者明確指令、TD-006與TD004-DB-NORMAL-01續作。原 START_HERE/AGENTS/CORE_TRAINING_PRINCIPLES/唯一主檔/有效決策/matrix及覆盤、catalog、Architect/Developer/QA/Evaluator角色與四相關skill來源已重新取得並檢視；EP-08採用相同輸出、SQL plan及可量測成本，EP-13採用原生引擎與交易契約。不重跑先前資料正規化、NULL、識別映射、PG遷移/容量及NATIVE-ARCH-005/EP-011原實驗。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，無私人工作台或獨立代理。
基準 cbaca48fc86d7c2a70b7867a5e459ee3bd90c3f2 / tree f8215cb51e6b49607837735c818a2b4ec6b15f0d。前輪 CI 44043614630/job133903845315 completed/failure，原始log 116160 chars：519 tests in 86.565s，唯一 error test_academic_app_real_browser_and_download 行66讀不到 /tmp/.../profile/DevToolsActivePort（FileNotFoundError）；offline unit tests停止，後續品質步驟skipped。不是資料庫實驗失敗，真根因未確認，也不宣稱環境暫時故障已修復；歷史核心準則 CI 44042533418 成功不替代本版本。保留失敗與品質門檻，未改APP、未手動重跑舊驗收，不因單一暫未診斷的瀏覽器錯誤停止獨立專業實驗。
教材2.2.6 原授權備份 Markdown 6029 chars，SHA256 bbc5cfb3c2e3f297bcef81d4c000ba6b73baf8bc9545319381c0839f0edf07ad（connector UTF8文字，hash abc自檢通過），36圖片、共用embed未取得；不再沿已知無效相同圖像路徑重試。原文§1 Heap/Table Scan/Index Seek，§2五筆Customers及SQL條件，§3 B-Tree，§4.2-3叢集/非叢集及lookup，§5 SSMS操作多為圖像未驗。實讀原文字及SQL，不執行教材DROP TABLE於任何真DB。9 READABLE文字、154 UNREAD、13 BLOCKED_SOURCE，176 L0保留。
來源批判及延伸：Microsoft官方 https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17 和 https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=azuresqldb-current 實讀：rowstore B+ tree、heap可有nonclustered、PK clustered是預設而非必然、clustered葉為data pages，頁內邏輯順序非物理連續，不取代ORDER BY。非叢集可透過INCLUDE覆蓋，無必然key lookup；寬索引增加維護/磁碟/快取成本。SQL Server原生實機、SSMS圖示、頁分裂或鎖、INCLUDE與clustered設計未驗。SQLite官方 https://www.sqlite.org/queryplanner.html、https://www.sqlite.org/eqp.html 實讀：多欄左前綴、covering、search+sort、SCAN/SEARCH/TEMP B-TREE；EQP格式可隨版本變化，非production API。SQLite rowid表不是SQL Server heap/clustered的實測替身；SQLite covering附加欄不是SQL Server INCLUDE同機制。應依分布、實際filter/sort/projection、統計、寫入量決定索引順序；等值後範圍是此查詢適用起點而非全域定律。
### 真SQLite實作及量測
自寫既有test_research_data.py class IndexDesignLesson；本機 SQLite 3.46.1，python -m unittest -v index_lesson.IndexDesignLesson，2/2 OK、3.082s，class含末尾換行SHA256 f67f4cfab705386cf36261d1ed60bcfed802268135279ac21de063d89332e265。自寫合成工作負載，不是產品缺陷或獨立盲測。40000 rows，id INTEGER PRIMARY KEY、cohort=i%100、tick=i、score=i%37、payload='x'*80。每組新:memory: DB、固定schema/data、額外索引、ANALYZE、commit；無額外索引仍有rowid主鍵。固定 query SELECT tick,id,score FROM event WHERE cohort=7 AND tick>=10000 AND tick<30000 ORDER BY tick,id；以Python固定期望200筆逐行核值，另次set_progress_handler(n=1)計VM callbacks後移除，五批每批30次fetchall平均耗時取中位數（含Python回傳成本，未冷快取/隨機組序、非SLA）：
| 額外索引 | 實測 EQP detail | VM callbacks | 每次ms |
|---|---|---:|---:|
| 無 | SCAN event; USE TEMP B-TREE FOR ORDER BY | 123612 | 1.671986 |
| cohort | SEARCH event USING INDEX idx_event (cohort=?); USE TEMP B-TREE FOR ORDER BY | 4815 | 0.289594 |
| tick,cohort | SEARCH event USING INDEX idx_event (tick>? AND tick<?); USE TEMP B-TREE FOR LAST TERM OF ORDER BY | 104215 | 2.130724 |
| cohort,tick | SEARCH event USING INDEX idx_event (cohort=? AND tick>? AND tick<?) | 1417 | 0.195631 |
| cohort,tick,id,score | SEARCH event USING COVERING INDEX idx_event (cohort=? AND tick>? AND tick<?) | 1216 | 0.147399 |
覆蓋索引加查payload即失去COVERING，真EQP負例；逆序索引在本工作負載仍SEARCH但範圍較寬、需局部排序，耗時甚至大於scan，不能以SEARCH判效能或VM callback當磁碟頁數。
另一方法每組5個獨立重建DB，測初始page_count*page_size（已ANALYZE，包含資料與索引配置頁，不是RSS或真檔案大小）、5000筆同交易insert、按id範圍5000筆score+1同交易update，各取5次中位數；每次核逐行資料、45000筆及integrity_check=ok。四設計，不測逆序索引寫入。
| 索引 | 初始配置bytes（5次一致） | insert ms/5000筆 | update ms/5000筆 |
|---|---:|---:|---:|
| 無 | 3944448 | 5.475919 | 1.276839 |
| cohort | 4317184 | 10.062119 | 1.507612 |
| cohort,tick | 4444160 | 10.514491 | 1.326850 |
| cohort,tick,id,score | 4648960 | 9.517162 | 5.919286 |
覆蓋score增加查詢覆蓋與score更新成本；insert測值並非索引愈寬必愈慢，不做速度assert，不將偶然差異因果泛化；未測真磁碟I/O、WAL/耐久、並發、不同分布/負載、更新索引鍵、真雲端或SQL Server。計畫文字斷言只供這個引擎版本受控教學，未作產品runtime依賴。
### 蒸餾及覆盤
Architect/Developer/QA/Evaluator角色分工；既有architecture-design與test-and-acceptance增量：先確定read/write workload與固定結果，實測等值/範圍/排序欄位、covering及加欄負例、索引冗餘與維護成本；使用原技能，不新增管理或知識庫。新知支持研究事件、預約或教學平台的查詢設計，但未改外部系統、未實測獨立真情境遷移。0使用者人工操作、0舊lab手動重跑；無可比長期工時及真人成效，不聲稱模型增益。原七階段未完整（缺圖/SSMS/真遷移），L0保留。下一輪依2.2.9資料匯入的原教材及既有匯出/原子遷移證據選新缺口，例如staging與拒絕非法列，不重做既有識別映射。另以必要最小診斷處理重發Chrome啟動錯誤，不放寬守門或阻塞獨立專業學習。R2、NT$0、A07/B10、C4-C6/M4延期、3/6及權限不變；不部署、不改main/release。


## TD004-DB-IMPORT-01｜暫存、批次拒絕、原子匯入及逐值對帳（2026-11-17；TEXT_PARTIAL / SQLITE_LAB_VERIFIED）
依本輪使用者明確指令、TD-006/TD004-DB-INDEX-01接續。實讀 START_HERE/AGENTS/CORE_TRAINING_PRINCIPLES、主檔、相關決策、matrix/覆盤/catalog、Developer主責與Architect/QA/Evaluator協作角色、相關四skill，原 test_research_data.py 的Store.apply/export、已完成識別/正規化/索引與EP-01/05/13。採EP-01逐值語意、EP-05來源bytes/hash分離及EP-13交易契約；本輪不同於原逐列apply/匯出/映射，聚焦原始CSV暫存、診斷及promotion transaction內收據與對帳。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，非私人工作台或獨立多代理。無外部專案、真資料、付費、部署或正式發布。
基準 5f5669b09f73c61276ac187bc7fe7897ca4f587c/tree ae724a11e70760241d44d740acc6c4bc7b733ba2；CI 44044299687 job133906078055 28/28步 success，raw 257375 chars，Ran 519 tests in 83.735s，matrix ok、先前瀏覽器測試ok及375/1280 Chromium實測CSV 100 rows 3161 bytes；checkout ffefad7b38e38719dfae9a8b52ac73cadd5eae6a parents main+基準且tree一致；report marker8671fa78a427e2b6c773facd4a5bdffe8fae9327848dae38bf898c69cded52b9。前CI44043614630失敗保留，知悉此次恢復但無根因證明，不冒稱修復。不重跑舊lab。
原2.2.9 Markdown 9538 chars, SHA256 0ef608eb06c5c3f7159b6d5e915ed4b31d0f8b0256f72c0b03d3e50d286e73a4（connector UTF-8文字；兩次自行簡化hash自檢失敗未寫入，停止該算法改既有驗證算法，abc通過）；27圖、共用embed與郵遞區號Zip樣本本輪未取得，不重試既知無效圖路徑。原文§1招標/轉檔/開帳；§2 Excel、剪貼簿/一萬筆分界、BULK INSERT、ZipArea/City/Road DDL及TRUNCATE/匯入範例；§3 identity欄位/編碼ANSI；§4移除重複、文字流水號、串接與VLOOKUP精確搜尋。沒有閱讀未取得的圖或實測Excel/SSMS、Zip sample。原矩陣10 READABLE文字/153 UNREAD/13 BLOCKED_SOURCE，176 L0保留。
批判與延伸：保留原始bytes及來源版本；一萬筆是教材建議而非任意環境效能門檻；不可盲目DROP/TRUNCATE真庫或無核准移除重複。研究資料可能合法重複測量，依規格判斷唯一性與映射，前導零/文字保真；精確VLOOKUP仍需驗來源鍵唯一與未命中，本文不重做跨庫映射。原教材ANSI與全欄位含Id的要求不普遍適用；Microsoft官文 https://learn.microsoft.com/en-us/sql/t-sql/statements/bulk-insert-transact-sql?view=sql-server-ver17 支援版本的CODEPAGE=65001、FORMAT=CSV、format file與KEEPIDENTITY策略，版本/平台有差異。CHECK_CONSTRAINTS未指定時bulk import可能忽略CHECK/FK及改constraint trust；MAXERRORS不能當全筆業務驗收；BATCHSIZE可能導致部份提交，明確外層交易可回滾該交易所有批次，仍須核trigger、權限、編碼/分隔、實際環境。不可照抄教材DDL、TRUNCATE或推稱本輪SQL Server實機。staging/逐筆拒絕/交易內收據/對帳是依使用者指定的工程延伸，不歸於原文。
### 真實實作與驗收
自寫 StagedImportLesson，加至原 test_research_data.py；SQLite 3.46.1，隔離:memory:，python -m unittest -v import_lesson.StagedImportLesson 最終3/3 OK in 0.006s，23 assert sites；class含末尾換行 SHA256 0c91a0dc188988715380e86f60eeff6ddbd6871fb68b80e9070c4159c6e88c9f。初次3/3後增加同count/sum反例直接觀測再跑新class；非舊lab重跑或效能benchmark。來源CSV 64KiB/100筆上限、strict標頭與欄數/UTF-8-sig、保留解析後字串、原bytes digest與批次/邏輯列號。manifest/stage/rejection/receipt及target分離；promotion BEGIN IMMEDIATE內重驗stage和目標唯一性，全批拒絕與報告或全批寫入+逐行對帳+receipt+COMMITTED。stage本身先提交；「原子」指目標promotion，不是假稱全流程不留拒絕紀錄。只接受新增，明確拒絕現有代碼，不擅upsert。
1. 原CSV四筆：001/9/中文含逗號合法、A2/abc、A2/101、EXIST/20；共3錯列、5原因(2/3 DUPLICATE+SCORE，4 EXISTS)。全批REJECTED、target原1筆不變、無成功收據、原digest保留、合法001也不寫入；4個格式負例（錯UTF8、header順序、少欄、未閉引號）均拒絕，五表快照不變。不是所有可能型別或拒絕分支驗收，格式錯誤未保存durable rejection。
2. BOM與引號內換行正例；真正SQLite trigger在新增成功收據時RAISE ABORT，已有target INSERT及對帳仍被整筆promotion rollback；五表snapshot不變、stage仍可用。移除故障注入後成功2筆，保留原1筆及前導零/分數邊界/中文字換行，receipt=2；已提交批次再promote拒絕且五表不變。不是未知ACK或分散式idempotency，不冒稱process crash/耐久。
3. 自建AFTER INSERT trigger錯置兩筆分數。用savepoint實際觀察 A20/B10 仍count=2,sum=30（正確應A10/B20），回滾preview後五表不變；promotion逐值比對拒絕並回滾、移除故障trigger再成功、FK check=[]。這是故障注入及驗收負例，不是已發現正式產品bug/L4。不能以總額一致取代逐值/鍵/版本比對。
### 蒸餾、邊界及續作
更新原 implement-feature/test-and-acceptance 技能，保留原架構/約束/匯出經驗。此小型可信單連線lab未保存原始bytes（只有hash及解析值）、未驗stage被其他writer篡改/授權、原始檔隔離留存、真正DB durability/並行/未知commit、空批/超限及所有非法值、SQL Server/Excel/Zip/大量效能。dict counts與target全表比較僅適小樣本，生產應採有界分塊/集合差異，必要固定schema版本、可驗來源隔離及存取權限。原七階段未完成，L0保留、無獨立陌生真任務或模型增益。0使用者操作請求；原工作機制、八角色十五技能及唯一主檔無重建。下一輪2.2.10資料庫安全性由Security主責，先查既有PG RLS/ACL與未驗資料匯入角色權限或拒絕報告敏感資料暴露等新缺口，不重做已驗PG；C4–C6/M4、A07/B10、3/6及NT$0不變。


## TD004-DB-SECURITY-01｜匯入角色、封存與拒絕報告隔離（2026-11-17；TEXT_PARTIAL / SQLITE_LAB_VERIFIED）
使用者明示續2.2.10由Security主責、Developer/QA/Evaluator協作，深入匯入最小權限、暫存保護、正式寫入限制與拒絕診斷去敏感，不重做既有PG RLS/ACL/交易。實讀核心準則、START_HERE/AGENTS、主檔、決策、matrix/覆盤、四角色及技能、原EP-03/05/13/PG-023/024覆盤、原StagedImportLesson；採EP-05來源隔離、EP-13可信writer邊界、EP-03未知結果不盲重送（本次無未知結果），改以SQLite連線級SQL授權驗新風險。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，無私人工作台或獨立多Agent。基準 46ff7f6e8be1b0b610889cc2ff1dddb84a6a2c10/tree 827a9a1fd50e123f1e683d014691b7b81c4df0d8；CI 44045288347 job133909339514 全28步success，原log Ran 519 tests in 79.666s、Chromium 375/1280 CSV 100 rows/3161 bytes；checkout 9c7e6fa83505d7b94c2354bdab93d11764ef859a parents main+基準/tree一致，marker33d504ffee8d55ebd52bffe52936a4ac17c9d965bf7b83d547fcfd0ac3384d4f。先前Chrome根因不明保留。
原2.2.10授權備份Markdown 7879 chars，SHA256 52dbcb97594a0b3dfbba213173dda4e0bf39e381b1111b7d885d1f81096bf9c2（connector UTF8文字，abc自檢pass），34圖引用與共用embed未取得。§1 ERP/CRM庫與Users/Orders示範DDL/DML，§2 客戶端/外包需求、管理與最小欄位；§3/4 SSMS圖為主未讀，原樣本可能含個人識別資料不複製、不執行原DDL/DML。§2.2外包Orders所有權限、Users限必要欄與§2.4外包表只列特定views SELECT不一致，不自行決定正式寫權；UserNane拼字/姓名不一致不搬；共用外包帳號降低個人可追溯性，sa不當日常應用帳號。Microsoft官方 https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/getting-started-with-database-engine-permissions?view=sql-server-ver17 與 https://learn.microsoft.com/en-us/sql/relational-databases/security/permissions-database-engine?view=sql-server-ver16 查核登入/角色/物件/ownership chaining、sysadmin/dbo bypass、column grant例外；view不是單獨的授權，必核基表與間接路徑，不等同匿名。原教材SQL Server未實機，圖/GUI未驗。SQLite官方 https://www.sqlite.org/c3ref/set_authorizer.html 、https://www.sqlite.org/c3ref/c_alter_table.html 、https://www.sqlite.org/security.html 查核engine prepare-time callback、触發器/檢視來源與可信schema、拒絕及資源限制；authorizer由可信host安裝，每連線一個，可由host撤除，非原生帳號/RLS/對DB檔案的存取控制。
### 新實作與真正驗證
本機Python3.13.5 SQLite3.46.1；無PostgreSQL/SQL Server執行檔，不安裝、不外部服務。新class ImportSecurityLesson 真暫存檔DB，每次獨立fixture、各角色各自連線，cached_statements=0/trusted_schema=OFF，default deny唯SELECT/TRANSACTION與明示main物件、欄/來源trigger允許；無函式、DDL、ATTACH、PRAGMA的白名單。初版三方法通過，擴充promoter成專用受限入口與額外負例，再執行本輪新class 4/4 OK in 0.261s，23 assertion sites，class含末尾換行本機SHA256 5f3a7bc077cddc390a2410054441c4a8b243895bb29ff23bb93260f8f8c341cf。非產品真事故或獨立模型盲測。原SQL匯入/PG等其他lab未重跑。
1. uploader只可INSERT incoming_a；固定server schema將寫入限制A批次，trigger核OPEN與重複列，拒直接stage/target/manifest、讀stage/view、DDL/PRAGMA/ATTACH、提前promotion等12條；實查SQLite SQLITE_AUTH與四表snapshot不變。OR REPLACE/OR IGNORE重複明確RAISE ABORT防靜默改寫或忽略；封存後追加拒絕，原列保留。
2. reviewer只可讀report_a(batch,n,reason)與result_a(batch,n,score)，拒直接raw/base table、manifest、stage、寫入、同名TEMP VIEW、PRAGMA及promotion等11條，查B批次為空。A報告的reason為預設合成fixture，非完整驗證錯誤產生服務；私有raw欄不出現在結果中，不能推論所有side-channel、日誌或真個資已匿名。
3. promoter只可透過promote_a，trigger核SEALED、request、全批數字canonical/range及目標衝突後寫A與狀態COMMITTED；未封存拒、四個直接寫/讀操作拒；正常匯入A/2/42且B/1/99不變，reader/uploader不能修改target；可信host例外直接映射固定IMPORT_REJECTED client診斷、原表不變。三角色合計29條SQLITE_AUTH拒絕（12+11+4+2）逐次snapshot，另有業務IntegrityError負例。
4. 42x非法值即使OR IGNORE仍拒，另一admin預設衝突fixture即使OR REPLACE仍拒且快照不變。是受控負試，不是實際正式故障。沒有重做原receipt及跨庫身份映射。
封存限制僅不可信角色，不防有檔權、owner或可信host改stage（admin負例刻意展示仍可修改）；未核封存digest/原始bytes/approval revision、真正競寫、斷電、大量、resource exhaustion/query side-channel/錯誤日誌/HTTP/Auth、加密或服務端使用者撤權。固定A只是合成schema view，不可用來泛化任意tenant ACL，SEALED為本機owner設定非真人審核；client_insert為固定代碼示例，非全部外部錯誤映射；不宣稱SQLite callback隔離任意程序。原資料匯入策略與真研究權限/倫理需獨立授權。
### 蒸餾與覆盤
增量原 security-review、test-and-acceptance（不新增技能或管理）；區分資料分類、受限入口、DB/host/file信任邊界、sealed/approval、原始診斷隔離及逐項權限驗證。原課只有文本及受控延伸、34圖/SSMS未取得、完整七階段及真陌生遷移未驗，矩陣11 READABLE文字/152 UNREAD/13缺/176 L0。0使用者人工操作請求、0舊lab重跑；未測長期效率或獨立模型能力。下一輪依3.1.2結構化查詢語言與3.1.1前置核讀，選尚未驗證的DML/查詢語意（例如受控條件更新、影響行數/版本、NULL predicate/集合語意），或原2.2.5圖可讀則核必要資料模型圖，不重做既有CRUD/交易。保留C4-C6/M4/A07/B10/3-of-6、NT$0；無外部專案、付費、部署/main/release變更。


## TD004-SQL-SEMANTICS-01｜安全條件更新、版本及集合語意（2026-11-17；TEXT_PARTIAL / LOCAL_LAB_VERIFIED）
依使用者明確指令、TD-006、TD004-DB-SECURITY-01接續：Developer主責，Security/QA/Evaluator協作，REPO_NATIVE / SINGLE_AGENT_ROLE_WORK。實讀最新核心準則、START_HERE、AGENTS相關契約、主檔、決策、矩陣、覆盤、角色及相關skill、原test_research_data.py Store.apply與MissingValueLesson、EP-01/05/13；採用固定語意與逐筆證據、版本/權限原則，將全庫revision延伸為逐記錄條件mutation及SQL結果語意，不重跑原CRUD、交易、匯出、NULL基本值或PG RLS/ACL。
基準 798a6e936ce466164b37e2c27d1d37ec1da97a80/tree f0c010f5e4578a92441e3aba80c0c3dc71a1da10；先核CI44046296216 job133912697393 completed/failure，原始日誌 Ran519 tests in88.242s FAILED(errors=1)，唯一錯誤test_academic_app_real_browser_and_download line66 FileNotFoundError DevToolsActivePort；offline unit tests後守門skipped；再次出現先前44043614630相同症狀。原測試啟動stderr=DEVNULL、15秒期限且deadline後直接讀portfile，能確認診斷資訊缺失及逾時後未檢查檔案，不能確認Chrome根因。保留最新CI失敗，不用先前green替代，不重開UAT、未改瀏覽器測試或APP；建議另輪受控啟動診斷與實際修復，不阻塞本輪獨立專業訓練。519為既有tests回歸數，不將其當本輪review lab的CI執行證明。
原授權備份正文實讀3.1.1/3.1.2/3.2.2（1541/5899/8562字元；SHA256 connector UTF8 a36d2bcb5326be084aaedc4bb72cc660b43e31decdbfa7ccf02ff337fdd41fe7 / b9fdd4df141cf073b615346472366e77d60cfffb9d6b5ab10ce7336f425527ea / 114696864d061c7bf01d7e06a14e26544a87671ec35817be3a844df5d016b2c5；abc自檢通過）；分別6/5/20圖及共同embed未取得。3.1.1 §2/3建立sqldb schema/initial data，SQLDemoTable與SQLDemoData preview真open失敗且Drive精確名稱未命中，不冒稱取得或執行。3.1.2 §1–6關聯模型、SQL史與ANSI/ISO標準/方言（歷史細節未獨立驗），§7 DDL/DML/DCL/TCL（依原分類SELECT屬DML，其他教材也可分DQL，TRUNCATE/DDL交易語意依引擎）；標準化非任意引擎等效或保證效能。3.2.2 §1.2/1.3 UPDATE SET WHERE、§2單/多欄及運算/DEFAULT、§3 CASE/JOIN/聚合；§3.1文字D02/D03不一致，SQL SELECT年份2001–2015但UPDATE只篩D03且CASE無ELSE，未命中會成NULL或違NOT NULL而拒；原前後預覽未涵蓋被錯改的範圍外列。本輪以自建研究合成fixture重現並修正，非對原教材sqldb執行。先SELECT後UPDATE仍有間隙，不保證真正競寫下相同目標；固定身份、預期版本、狀態和可寫範圍需在UPDATE predicate及必要交易核對。SQL Server JOIN多來源值不唯一時UPDATE FROM未定義，未實測本輪該引擎。
官方查核 https://www.sqlite.org/lang_expr.html CASE/NULL及IN/NOT IN/EXISTS、https://www.sqlite.org/lang_returning.html 直接修改列回傳、新值非AFTER trigger最終值且非commit、https://learn.microsoft.com/en-us/sql/t-sql/functions/rowcount-transact-sql 受影響列與後續statement可能改寫rowcount、https://learn.microsoft.com/en-us/sql/t-sql/queries/update-transact-sql?view=sql-server-ver17 UPDATE及不確定FROM來源、https://learn.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql/ OUTPUT，不能以SQLite代替SQL Server實機。NOT EXISTS等集合比較是本輪延伸，非聲稱3.1.2明列各語法；3.3.1/2原章未讀，後續按原來源接續。未取SQLite lang_select頁，集合結果以實測核對。新矩陣14READABLE文字/149UNREAD/13BLOCKED_SOURCE，176 L0保留。
### 實際本機訓練
Python3.13.5 SQLite3.46.1，獨立新class SqlSemanticsLesson 真:memory:與temp file兩連線，python /tmp/sql_semantics_lesson/lesson.py 3/3 OK in0.043s（非效能基準），30個self.assert程式位置，class含末尾newline SHA256 a8852ca9801a1345d0d165115be778d3d695b21d65272f91db9f347dce83e6bb。新方法追加原 test_research_data.py，未手動重跑舊lab。合成資料，不涉及真研究。原reference red以真錯誤值為期望的反例，不是假稱既有產品L4缺陷或獨立盲測。
1. payment A組四列年份2004/2010/2020/NULL加B組同ID，所有amount100；預覽A年份2001–15只有1/2。模擬教材CASE無ELSE且只篩A，rowcount4，1→200、2→150、3/4→NULL，B不變；savepoint rollback核快照。修正WHERE同範圍且ELSE保留原值，RETURNING兩筆1/2及正確值，固定完整五列核對。用nullable欄實際證明風險；不聲稱測原薪資型別或實際網頁。原預覽及update不是不可變批准清單或真競寫保護。
2. 每列version/state及trusted study/id參數在同一UPDATE WHERE與RETURNING核對。兩真DB連線先讀v1，第一連線提交A1→v2 approved，第二舊v1更新回空；現v2但非draft、缺ID、SQL樣式文字作綁定值均空；A2獨立成功不需全庫revision；B1不變。非真並行鎖/撤權或server身份驗證。故障注入AFTER trigger：RETURNING B1=v2/approved但實際SELECT flagged，明確raise回滾與另一連線舊v1/draft一致；另UPDATE SET status=status rowcount=1（匹配且執行UPDATE不等於實值改變，此表有AFTER trigger，已回滾），不把rowcount當完整副作用。無未知ACK、正式幂等或崩潰耐久驗證。
3. expected A/B/C，observed A/A/B/NULL。NOT IN因NULL回空；NOT EXISTS/EXCEPT正確C；INTERSECT A/B，UNION四distinct（含NULL），UNION ALL七列；GROUP BY識別A重複，單獨計NULL一筆。兩方向EXCEPT比較有效A/B集合都空仍有三行vs兩distinct keys；保留multiplicity/NULL與scope，不能以集合相等替代資料對帳。只核這個非NULL expected ID契約，真NULL equality/排序/collation/效能及其他引擎待驗。
### 蒸餾、覆盤及續作
增量原implement-feature、test-and-acceptance：預覽predicate與mutation範圍一致、CASE ELSE和NOT NULL、同一SQL逐列版本/狀態/身份、回傳鍵與提交後真狀態分離、scope前提、集合與bag multiplicity。只用新技術實證、不另建知識庫/管理。0使用者人工操作，0舊lab重跑；無獨立模型/真外部任務/長期work outcome，不宣稱能力分數。下一輪原3.2.1 Insert/3.2.3 Delete/3.2.4 Select或3.3.1 Join依實際前置和原已有證據選新缺口（非唯一join、外連接過濾、集合聚合），另輪可對Chrome故障做最小診斷。缺圖/preview/SSMS保留L0不阻其他單元。原TD-005-R2/TP010/TD006及C4-C6/M4、A07/B10、3/6、NT$0、無外部寫入/部署/main/release維持。


## TD004-SQL-JOIN-01｜資料粒度、外連接與聚合正確性（2026-11-17；TEXT_PARTIAL / LOCAL_LAB_VERIFIED）
依使用者本輪指令、TD-006及TD004-SQL-SEMANTICS-01接續。重讀核心準則、START_HERE、AGENTS有效條款、主檔、決策、matrix/覆盤、四角色與既有skill/EP-01/13、原research lab方法清單及前輪實證。Developer主責，Architect/QA/Evaluator協作，REPO_NATIVE/SINGLE_AGENT_ROLE_WORK，無獨立代理或私人工作台。採EP-01逐值/完整鍵與EP-13顯式INSERT欄位/約束，延伸查詢grain而非重做CRUD/CASE/版本、匯入或NULL反集合暨PG權限。
基準 bef931725fc5690836d734743de41023c37efa5d/tree 59b40eb95d6cabfb2bce077b68ec7bfd77b41f79，CI44047731069 completed/success job133917515066 全28步success、raw log257380 chars，Ran519 tests in88.890s，實際Chrome375/1280 CSV 100 rows/3161 bytes、checkout b999272022d10c51092a45eb72ffae3923cc36b3、report marker62f30dae306f86d38fc6f9608af386bcd55ec642c0036def50f18f3c0e676c48。未另核merge tree；前次Chrome error未再現但根因未明，不宣稱修復或新lab已由CI discover覆蓋。
來源：3.2.1/3.2.3/3.2.4/3.3.1原授權Markdown正文與文字SQL，5399/10693/15983/12777字元，connector UTF8 SHA256 4c6ffa7183a7d8a25749091fd411fae000228cf673d5957c5526eb8883b1152d / 08536161b9092f723f117817c564168ebdd63de8cb1dc804554d4b2098b25382 / 3956c7cb97737cb967ba1ad53cde5974ef80166a56bb028c5263f75b9334c24b / 3ca13980e50ec22d63bb37bfa09fee78d97df48fc1772f233583cccbcf5ed8ca，abc自檢成功。9/32/44/50處圖引用及共用embed/原sqldb未取，共135處引用非唯一圖數。原3.2.1 §4部分欄位及§5 IDENTITY_INSERT/GO、§6批新增及INSERT SELECT；3.2.3 §3/4條件/子查詢/重複清理、§5 DELETE vs TRUNCATE、§6先SELECT再DELETE及交易；3.2.4 §3–7查詢、DISTINCT/WHERE/ORDER/TOP/聚合/HAVING，§8.3/4分組與子查詢統計；3.3.1 §2.2 JOIN類型、§2.4 ON/WHERE、§3.7–9多表/過濾/聚合。非完整媒體及原生SQL Server實驗。
批判：3.3.1 §3.9 HAVING SUM(s1.Amounts) IS NOT NULL排除無匹配或全NULL金額，後段說明卻稱保留無訂單客戶；依需求決定保留/排除，不一律COALESCE測量缺失為0。§3.8 WHERE右表條件只取高額訂單，若目的本就是排除則正確；若要保留全名單則ON限制右表。§2.2 CROSS JOIN ... ON示例與§3.5無ON矛盾，SQL Server語法待原生核查。3.2.3 §4.3同名/同部門與MIN(ID)只是特定假設，不可視為身份重複或真刪除授權；§4.1只示SELECT TOP，未給刪除指令，無穩定排序不保證特定列；§5 TRUNCATE回滾依引擎，不操作真資料。3.2.1 INSERT SELECT需定目標grain、明示欄位及來源匹配；3.2.4平均與比例需核合法分母、空群組、日期與資料粒度，分母0及其他比例樣例未實測。官方SQLite https://sqlite.org/lang_select.html §2.3–2.4 與 https://sqlite.org/lang_aggfunc.html ：outer join null extension在ON之後 WHERE之前；count(*)數列、count(X)非NULL、distinct對值去重、avg/SUM缺失語意。
### 實際本機實作
Python3.13.5 SQLite3.46.1 :memory:；新 JoinGrainLesson 3/3 OK，新增HAVING斷言後再跑同一新class 0.004s、22 self.assert程式位置；class含末尾換行SHA256 f84a13365e70be1a1021b09dc60f4dc6cdc18ad6c718cd62cf872070ae2b190d；命令 python /tmp/join_lesson/run.py（原測試檔imports及main可重現），未重跑舊lab。真引擎自寫合成資料，非產品事故/獨立盲測。
1. A組4人P1/P2/P3/P4，P1 post兩次10，P2 post40，P3只有pre20，P4無測量；B組同P1有post90。LEFT JOIN後WHERE phase=post僅2人/3列，WHERE phase=post OR m.mid IS NULL仍漏P3；phase置ON保留4人/5列。逐人COUNT(*)與COUNT(m.mid)/AVG核對，P3/P4各1個null-extended row但0實測、均值NULL；A總名單4、post測量3、post有資料者2；HAVING SUM非NULL僅P1/P2。缺study鍵join把B的P1錯接A，完整study/id避免；非身份ACL。
2. P1兩測量×三報酬(100,100,200)=6配對，錯SUM報酬800；P2一測量×一報酬50；直接inner多表共7列/2人，總850，SUM(DISTINCT amount)=350也錯；真報酬4筆/450。各子表先聚合到study/id再LEFT JOIN，逐人oracle P1=(2,10,3,400),P2=(1,40,1,50),P3/P4=(0,NULL,0,NULL)，加總450；錯連接avg=100/7、事件等權20、受試者等權25（僅觀測到post的兩人，非全入組或推論統計）；EXISTS篩有post者P1/P2不擴列。CTE僅預聚合工具，未聲稱3.3.3已讀；未量測大型資料/執行計畫/其他引擎。
3. INSERT SELECT直接join建一人一筆cohort，P1重複觸PRIMARY KEY，目標空；明示欄與EXISTS後只P1/P2且來源不變。故意依study/id/phase/score及MIN(mid)去重，實際將合法P1第二測量mid2刪除；savepoint復原核來源快照。無真資料刪除授權。
### 蒸餾及接續
增量原 implement-feature/test-and-acceptance：定grain/完整鍵、外連接右篩選、保留母群、各child先依目標grain聚合、分母口徑與合法同值、存在性及衍生名單唯一性。18 READABLE文字/145 UNREAD/13缺，176 L0保留，原圖/原生範例、真外部任務及獨立模型增益未驗。0使用者操作、0舊lab重跑，無新管理或知識庫。寫入腳本首輪語法括號錯誤在解析階段未調用API，修正後重新核head。下一輪3.3.2 Union/3.3.3 CTE選分組、遞迴終止或跨來源型別/欄位對齊等新能力，避開既有集合基本實驗。Chrome根因另必要最小診斷，不放寬品質守門。保留R2/TP010/TD006、C4–C6/M4/A07/B10/3-of-6、NT$0及授權限制。無外部專案/部署/main/release操作。
