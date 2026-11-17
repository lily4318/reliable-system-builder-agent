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
