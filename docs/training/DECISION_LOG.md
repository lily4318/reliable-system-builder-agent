# Reliable System Builder Agent｜訓練方向與決策紀錄

本檔是增量保存的決策歷史；唯一目前有效訓練主檔為 [AGENT_CAPABILITY_TRAINING.md](../AGENT_CAPABILITY_TRAINING.md)。先讀主檔最新決策與當前候選 PR，再按 ID 查本檔。不得以歷史建議、未核准方案或舊排程覆蓋新決策。狀態分 DISCUSSION、PROPOSED、CONFIRMED、IMPLEMENTED、VERIFIED、SUPERSEDED、REJECTED；決策確認、文件寫入、程式實作及實際驗收分開記錄。後續以新紀錄引用及取代舊 ID，不刪除歷史。涉及私人資料、真人研究、付費服務、正式 Release 或跨專案整合須另行授權。

## TD-000｜歷史方向：工程基礎與獨立模型評測
- 日期：2026-11-14 至 2026-11-15。狀態：SUPERSEDED（僅本地模型作為優先路徑被 TD-001 取代；現有能力、證據、真實評測與安全原則保留）。
- 原始目標：改善通用系統建置 Agent，七專家、十二技能、案例庫、私人工作台，工程實作及可追溯驗收。後續曾因缺獨立子代理入口而將 Ollama 本機 runner、真模型呼叫與 holdout 列為當前最高優先。
- 實際證據：歷史主檔及原 Draft PR #8；head d2ca12006988100a500a6a6fea0f41cd73de5f85，CI 43688939298/job 132735394546 completed/success，完整日誌 223987 字元，388 tests in 39.030s，P12-FUNCTIONAL/P12-HOST-QA 等全部步驟成功。沒有實際 Ollama 推論、真正獨立子代理、私人 holdout 或能力增益證據。
- 不恢復已被取代的執行優先序；保留本地工具作可選評測、研究及必要回歸。

## TD-001｜正式重新定位：既有 AI 平台上的專業工程工作系統
- 日期：2026-11-15。狀態：CONFIRMED（使用者本輪明確確認）。文件實作與 CI 狀態由主檔及 Git 歷史回讀；實際跨平台工作驗收尚待執行。
- 使用者決策原文：「重新調整 Reliable System Builder Agent 的訓練方向，以教材的專業角色、技能、記憶、工作空間及實際工作覆盤為核心，使用既有 AI 平台執行，本地模型降為選用評測工具，保留已完成的工程能力，更新原訓練主檔。」
- 問題與原因：本地模型權重、模型獨立呼叫及 Agent 的專業流程是不同層次。先前本地 Ollama 路徑為助手自行選定的替代評測途徑，不是原始必要需求；缺本地模型不應阻止既有平台實際完成工作。以本地模型成功也不能直接推論其他 AI 平台的能力。
- 方案比較：A 以本地模型 runner/固定盲測為主（可控制資源，額外維護，非必需）；B 以既有 AI 平台的任務、按需角色/技能、工作空間、案例與實際覆盤為主（採用）；C 重新訓練模型權重（非本次需求，不採用）。本地 runner/測試/盲測保留作選用或獨立證據途徑，不刪除。
- 核心架構：平台提供推理與授權工具；通用 Agent repo 提供七專家、十二技能、工作協定、工程案例與驗收；各專案保有獨立正式規格、進度、權限及資料；私人工作台限授權環境。平台無真正子代理時採單 Agent 按需切換角色並誠實標記，不能冒稱多 Agent；不要求安裝 Ollama、不要求付費 API。
- 核心學習循環：讀最新正式來源 → 選必要角色與技能 → 取用適用案例 → 完成真實任務（或明確標記的受控工程練習）→ 獨立功能/安全/CI 驗收 → 記錄成功、失敗、原因、適用限制 → 人審後更新原技能/案例 → 用不同任務觀察遷移。優先解決真實缺口、降低重複失誤；不將合成測試數或自評當真實增益。
- 教材來源：主檔既有《AI團隊實戰營_學員包_第一天_11月份(1).zip》摘要（三角色九技能、共用空間、品牌手冊、案例卡、覆盤蒸餾）。原 ZIP 本輪未重新取得；七專家十二技能是工程延伸，非原教材架構。既有 Study1 Agent 專案來源與治理規範已在前次比較中參閱，僅作觀念比較，未授權跨專案修改或轉用研究資料。
- 影響：取代歷史 P1-2 的 local-runner-first NEXT_ACTION，保留所有已完成的 P0、P1-1、P1-2 介面與 P2 工程，以及獨立盲測程序；以實際技能使用、可驗收成果及經驗遷移為後續優先。保留原 GitHub 主檔、跨對話啟動及決策索引。不得把「既有平台可用」解讀為任意平台必然有工具或權限。
- 尚待：平台原生工作流程稽核、實際任務中技能/案例使用、覆盤及知識遷移的證據；真實獨立多 Agent 與盲測如另有授權再驗收。本輪不發布、不整合外部網站、不啟動 API、部署、不修改正式 main。

## TD-002｜跨對話接續與決策保存
- 日期：2026-11-15。狀態：CONFIRMED（專案持久接續協定；本輪依之建立決策紀錄，不新增重複主檔）。
- 問題：聊天與歷史排程易遺失最新方向，造成舊方案復活及重複施工。
- 方案：原 GitHub 的 START_HERE.md、AGENTS.md 為入口／行為契約，唯一正式訓練主檔維持原路徑，本檔保留決策歷史，重要深入分析可置 reviews/ 並在主檔索引。不依聊天記憶接續。訓練時查原 Draft PR #8 最新 head 及適用 CI；正式使用則仍依已發布 main/release。
- 每筆記錄保留問題、證據、選項、理由、使用者決策、影響、未決及狀態；未經確認的建議不能取代主線。更新原檔，寫前查 head/blob，寫後讀回及分開核對 CI；不宣稱未完成同步。GitHub 讀取權不等於寫入權。
- 尚待：每輪遵守並實際跨新對話驗證；不把本協定視為正式版本發布、外部整合、私人資料處理或付費工具授權。

## TD-002｜2026-11-15 確認補記及落地證據（延續原 ID）
- 使用者本輪明確採用：「採用上述方案，請在 Reliable System Builder Agent 原 GitHub Repository 建立永久訓練決策紀錄及跨對話接續協定，沿用原訓練主檔，整合目前已討論的訓練理念、教材分析、架構選擇與方向調整，區分正式決策及待確認建議，完成寫入與回讀。」
- 決策狀態 CONFIRMED；前一輪文件實作 IMPLEMENTED，原整合 SHA 331b1568ffca8c0ccf6cbd27be73471e6f9d3d4d，CI 43690995549/job 132741660212 completed/success，388 tests in 48.141s/OK，全部 steps pass。這是文件版本的工程回歸，不是新對話獨立驗收。
- 本輪深入覆盤：[2026-11-15 平台原生訓練覆盤](reviews/2026-11-15-platform-native-training-review.md)（commit 9285d9de17cbc3706664175921305e53cca00856，blob 7f1210c219ab35fd680322d978645c42ada15775 已讀回）。整合教材摘要、網站 Agent 架構觀察、三種方案、現有 12 技能及經驗學習限制；不存原教材或外部研究資料。
- 發現原主檔末段仍留有「真實 runner 受阻就做合成垂直切片」舊指令，依 TD-001 清理現行接續條文，不重寫歷史段落；舊內容仍可由 Git 追溯。候選分支最新整合回讀及 CI 另核對；真正跨新對話使用與各平台工具能力仍待驗證。
- 執行方式：先查 PR 最新 head 與 exact CI，再讀主檔／本 log 相關 ID／必要 review；每輪重要討論增量保存。決策取代必須引用被取代 ID、影響範圍、使用者確認及證據。PROPOSED 不等於批准；IMPLEMENTED、VERIFIED 必須各有獨立證據。

## 待確認方案索引（2026-11-15；非正式方向）
| ID | 狀態 | 問題／建議 | 確認或實作前所需證據 |
|---|---|---|---|
| TP-001 | PROPOSED | 平台原生工作空間與無本機 CLI 的持久化方式 | 實際平台能力、授權、私有資料隔離及可重讀；不得把公開 repo 當私人記憶 |
| TP-002 | PROPOSED | 技術探索、技能 references/templates/scripts/examples/tests 深化 | 真實任務暴露缺口、既有技能是否足夠，再決定擴充或新增 |
| TP-003 | PROPOSED | 既有網站與其他系統共用工程能力 | 使用者另行授權、來源／資料／權限隔離、整合方案及實際驗收 |
| TP-004 | PROPOSED | 語意檢索、自動蒸餾及記憶改善 | 實際詞彙檢索的失敗或不適用證據；保留人工覆核，避免誤升格 |
| TP-005 | PROPOSED | 獨立前後測、評分權重與跨平台比較 | 同模型與資源、未見題／獨立評閱、同條件比較；不要求本地模型 |

以上方案只是前次討論與原主檔建議的整理，細節與實作尚未核准。正式接續依 TD-001／TD-002 與主檔，不將索引當作新待辦清單。重要分析可續存 reviews/ 並以相同 ID 引用，不新增主檔。

## TD-001｜2026-11-15 平台原生實際工作稽核（執行紀錄，不另改主線）
- 任務 ID NATIVE-AUDIT-001。使用者授權按 TD-001 稽核七專家、十二技能、工作空間、案例記憶，修正實際流程缺口並更新原主檔及本紀錄。狀態：CONFIRMED（本輪範圍）；窄幅相容性修改 IMPLEMENTED、遠端回讀完成；新版整合 CI 及其他平台驗收尚未確認。TP-001 較廣的私人持久化設計、TP-002–005 仍 PROPOSED，不藉本輪升格。
- 來源：原 Draft PR #8 exact base-of-work 61cdb9e63b5d151e9e7d06c7dcf0c7aa51c01980；CI 43691452226/job 132742851388 completed/success，全 raw log 223992 chars，388 tests in 40.707s，P12-FUNCTIONAL/P12-HOST-QA 及所有步驟 PASS。讀 START_HERE、AGENTS、主檔、決策、review、catalog、TEAM_WORKBENCH；逐一回讀 7/7 role 與 12/12 SKILL 原文，確認 catalog 關係與應交付產物。實際工作模式 SINGLE_AGENT_ROLE_WORK / REPO_NATIVE：當前 ChatGPT 使用已授權 GitHub connector 選擇 role/skill、讀檔、寫候選、查 CI、回讀。沒有實際獨立子代理、使用者本機私人 SQLite、其他 AI 平台或外部網站的執行證據。
- 角色/技能選擇：System Lead/resume-project（最新方向與版本接續）；Architect/architecture-design（分離公開、私人、唯讀模式）；Developer/debug-and-repair（定位共通規則及無 DB 查詢缺口，改既有 learning 程式）；QA/test-and-acceptance（原 CI 原始日誌、兩個新增回歸方法、回讀）；Security/security-review（私人記憶與公開資料隔離、禁止越權）；DevOps/SRE/deployment（僅 GitHub 候選 commit/CAS/CI 查核，不部署）；Learning Evaluator/learn-from-feedback、knowledge-distillation（保存實際觀察及適用限制）。以上為單 Agent 依角色閱讀與工作，不是七個程序；未使用的新建站類技能僅讀不冒稱實作。
- 真實缺口：12 個技能及 7 個角色均將私人 context/handoff 當共通操作路徑；原 docs/TEAM_WORKBENCH 主要為 Windows CLI。GitHub-only 可讀技能與公開種子資料，但沒有無工作區公開檢索接口或明確替代可追溯交接。根因是執行環境與技能契約耦合，而非缺模型。比較 A 強制本機私人 SQLite（保留但非必要）、B 重建 GitHub 私人資料庫（不採用，越權/重複）、C 在已授權 repo 直接用原證據及只讀公共案例，保留私人工作區原規則（本輪最小實作）。不將 REPO_NATIVE 說成 SQLite 交易、私人記憶跨平台同步或同等安全機制。
- 案例 SOURCE_READ：同版 src/workbench_learning.py blob 7574a41d567586ef1f754142b3fc2c693aa07982 讀 CASES（B001、B002）及 opt-in TRAINING_CASES（P21/P22）。B001-CASE-001/B002-CASE-001：取用「缺資料庫不得因讀取而建立資源、唯讀先限制」的原則設計 public_context 無 workspace、拒絕傳 workspace、私人 actions 仍需 workspace；新回歸待 CI，不聲稱原 SQLite 測試能直接證明新功能。P22-CASE-004：取用「舊 revision 不能作當前驗收、回讀實際源與產物」原則，實際在每次 update 前查 PR head、用當前 blob SHA，更新後讀精確 SHA；不把 GitHub 更新等同 SQLite 原子任務／產物交易，existing private task pool 保留。案例採用為本次操作者聲明與 Git evidence，不是 SQLite cite receipt、模型獨立評分或已證明新任務學習增益。
- 產物：src/workbench_learning.py blob 6390fa05bb2ac56dddb451523a75985aa791b86a / commit 81d345152ed2cbc8e27853cf0ccbe683397a5152 新增 public_context/public-context：原 CASES 與可選 TRAINING_CASES、原 _terms 詞彙搜尋、有限 payload/limit、證據與 matched terms；不接受工作區、不建立或讀取 DB、不判定私人 retirement、前置核准或 citation。私人命令仍強制 workspace。tests/test_workbench_learning.py blob d8ebf82e03eb7edc4df714a40cab65fae30c8c67 / commit e0de4126366e31d7a6e9214a288a307b69d1a526 新增兩個實際回歸測試；該中間 SHA CI 43691810902 cancelled，不能算通過。
- 共通入口：AGENTS.md blob 585300f461a4aa9659cb71bfaeb186764974c489 / 5cc659f91ebf8bd988cfe7360f825281caf221ea 明確適用七角色與十二技能的 PRIVATE_WORKBENCH、REPO_NATIVE、READ_ONLY，明示共通條款釐清原角色/技能中的私人操作要求。TEAM_WORKBENCH.md blob 756b1f808b0b71010656ca6f412ab1abe6787145 / 0c4d9ace21d982fe761df73c75667e67c1374176 實際步驟、公開案例 source-read/CLI、原 repo 交接與證據、私有資料不可外流。START_HERE.md blob 6ed44b155e4214ebd7801d225de0156706a9d783 / 7cd8085e6fd9f320fea0e0526cb3b2fd6a354af0 依平台工具選模式。以上原檔同版回讀成功。角色/技能個別文件尚未改寫；由根 AGENTS 共通規則釐清，後續應查實際使用時有無衝突或平台跳過根規則，按證據修對應技能。
- 候選經驗 NATIVE-CASE-001（observed gap, candidate reusable lesson; 尚未加入已核准 active case corpus）：共享工作規則容易不知不覺綁定特定存取方式；保留能力與安全不變，明確區分工具運行模式，資料依權限分類，以原來源/真實 evidence 交接，不用假 SQLite 收據填補缺工具；用不同真實任務及跨新對話確認適用性，再討論升格／蒸餾。目前 GitHub read/write 可行；公共 CLI CI 尚待，非獨立多 Agent 能力證據。
- 下一步：核對最新整合 SHA exact CI（預期 390 tests，尚不得計為 PASS），修實際失敗；新對話讀最新 TD/案例與適用技能，用另一項實際授權工作驗證來源接續、角色/技能選擇與案例遷移；不新增不必要合成任務、不要求本地模型。不變更原 main/Release、外部專案、付費 API 或部署。

### NATIVE-AUDIT-001｜驗收補記
- 2026-11-15：exact code/tests/common-mode documentation SHA 7cd8085e6fd9f320fea0e0526cb3b2fd6a354af0，CI 43691876099/job 132744079996 completed/success；完整原始日誌 224366 chars，Ran 390 tests in 43.728s/OK；兩項 PublicContextTest 方法均 ok，所有 workflow steps success。公開案例檢索、預設/擴充隔離、無 workspace CLI 和私有命令拒絕缺 workspace 的工程契約 VERIFIED。
- 七份當前檔案於 ee431ec707a62269c44c272a35a6786529042f51 回讀一致；該文件整合 CI 43691956604 查核時 in_progress。不得將前一 SHA 的 PASS 當最新文件 SHA CI。仍未驗證全新對話、其他平台、私人工作台實際協作、獨立多 Agent 或能力增益；候選經驗未升格。下一步按原主檔，優先真正不同的授權任務。

## TD-001｜2026-11-15 NATIVE-TRANSFER-002：人類確認契約的真實缺陷修復
- 範圍 CONFIRMED：使用者要求另選有實際價值的任務、驗證 NATIVE-CASE-001 的遷移、修復、回讀、更新原主檔與本紀錄。未授權外部專案、發布、付費服務或自動核准。選擇既有 human_confirmation.py，不重新做公開案例檢索或模型 runner。不是新決策方向。
- 前置驗收：head 06837374dd38b1a275a5a52fe0c23ce481acaeab / CI 43692011890/job 132744517975 completed/success，完整 raw logs 224367 chars，390 tests in 40.884s，兩項 PublicContextTest 及所有工作步驟 pass。讀 START_HERE、AGENTS、原主檔、決策、相關 review、catalog、release/current_release.yaml、config/agent-policy.yaml、docs/HUMAN_FIRST_WEBSITE_WORKFLOW.md。政策要求點選不送出、可編輯、另行確認，確認文字不授權部署。
- 工作模式 SINGLE_AGENT_ROLE_WORK / REPO_NATIVE；System Lead/resume-project 版本與授權；Developer/debug-and-repair 定位並重現核心函式缺陷；QA/test-and-acceptance 固定回歸、實際前後執行及讀 CI；Security/security-review 原授權邊界（僅文字確認，不傳送、不核准外部操作）；Learning Evaluator/learn-from-feedback 保存根因與證據。直接讀適用角色、resume/debug/test/feedback SKILL；沒有私人 SQLite、獨立子代理或使用者電腦操作。實際交接：原 policy + 版本 → 兩項缺陷重現與固定測試 → 修正 blob → 測試輸出與精確回讀 → 本紀錄；沒有假 handoff/cite 收據。
- SOURCE_READ：原 DECISION_LOG.md 的候選 NATIVE-CASE-001（前次驗收已確認）與同 SHA src/workbench_learning.py 的擴充 TRAINING_CASES，明示 opt-in；P22-CASE-004 舊修訂失效原則適用，P21-CASE-006 提醒核心測試不等於瀏覽器／真人驗收；B001/B002 SQLite 缺庫原理這次不適用於純函式狀態。未呼叫 public-context、私人 cite 或其他模型；來源讀取及採用理由由本 Agent 聲明。
- 問題：src/human_confirmation.py 原 blob 0bafdfb39c65d35f76383510bfe3df4cdb4218c1，Python 原始碼複製到隔離暫存環境以 git hash-object 核對相同 blob，實際 h.confirm(d,'false') 給 explicit_confirmation_received=True；confirm(A,True) 後 select(B) 的 DRAFT_EDITABLE_NOT_SENT 仍有 A confirmed_text。根因：Python truthiness 代替嚴格布林，展開 state 保留已失效欄位。原介面不傳送、不授權，沒有證據外部動作曾受影響。
- 修復比較：只靠特定 UI 轉型／清畫面（其他呼叫者仍可能繞過） vs 在原平台無關核心純函式統一拒絕非 literal True、重新選擇清除 confirmed_text，保留原歷史物件及 sent=False / approval_granted=False（採用）。沒有新增 host、權限或資料庫；true 值只是呼叫者輸入，不是人類身分或事件的獨立證明。HTML 示範、其他 UI adapters/同步、任意不可信 state 及完整輸入 schema 不在本輪修復及驗收範圍。
- 測試證據：隔離暫存 Python unittest 兩項 regression test，原檔實際 FAILED (failures=6：五個 truthy 非 bool subtests 與 stale confirmation)；同測試修復後 Ran 2 tests / OK。測試另外確認合法 True、修改後文字、重新確認新版、原歷史、sent/approval 仍 False。修復程式 git hash-object a40069b607e5c102c44196baa944f9c2b2c96521，遠端讀回同 blob / commit 04724a59287ee94ea3f0b7233fa74ccc65bcdca2。新增 repo tests/test_human_confirmation.py blob 4b7d9a0323293e721940b299f9038c4ba5db564d，commit f0e3c09a8c8419cdff11f7560f6ebd926be17641；與暫存測試相同測試內容但使用 repo 的 from src import，讀回。Exact code/test CI 43692337646 pending at check；預期 392 tests，不能計作成功。
- 遷移觀察：NATIVE-CASE-001 的「核心規則與執行環境分離」已實際用於另一類真實問題（人類確認純函式，不靠平台 UI 正規化）；P22-CASE-004 版本失效原理用於改選後移除舊 confirmed_text。此為有前後程式證據的單 Agent 實際應用，非對照實驗或獨立能力增益；NATIVE-CASE-001 保持 candidate，待使用者審查是否升格。新的候選細化：平台互動旗標須檢查確切型別，改選要讓舊確認失效，文字確認永遠不等於外部授權；只適用純函式契約，不能代替可信 host 事件。
- 後續：核對最新 exact CI、修實際失敗；查 HTML 示範編輯後是否仍顯示舊確認與其他輸入邊界，必要時以真 DOM/本地可信測試修復。不同平台實際互動、全新對話、獨立子代理與盲測仍未實測；不擴充本地模型、不跨案、不發布。TP-001–005 不升格。
