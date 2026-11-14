# Reliable System Builder Agent｜自主開發能力訓練與基準評測（獨立候選）

## 最新訓練主檔｜2026-11-14（持續更新入口）

**使用者決策：** 將本次教材比對與訓練建議持久保存，以後每次要求訓練此 Agent，先讀本節與最新實際進度，再接續施工。此節為目前訓練方向及接續索引；下方保留既有評測協定與歷史，不將建議自動視為正式 Release 或額外授權。

- TASK_DOMAIN: RELIABLE_AGENT_ENGINEERING_CAPABILITY_TRAINING
- SOURCE_REPO: lily4318/reliable-system-builder-agent
- ACTIVE_CANDIDATE: Draft PR #8, candidate-skill-team-integration-20261114；https://github.com/lily4318/reliable-system-builder-agent/pull/8
- SOURCE_VERSION: B001 implementation/test commit d531eb09798e69003280cc981a20094969d4f381; integrated baseline 94014b1234298b92d607bcec41737abe8770d86e CI 43560882129 success; current PR head is authoritative.
- LAST_VERIFIED_STEP: B001 local functional tests 9/9 PASS; actual negative failure reproduced and repaired (8 PASS/1 FAIL → 9 PASS); both remote Git blobs identical to local tested files; full candidate CI 43561619878 in progress at readback.
- COMPLETED: 七專家、12 項技能＋總控技能、SQLite 私有工作台、13 題訪談、可編輯確認、離線任務包及評測；B001 實際合成 SQLite 報名垂直切片、並行、回退與唯讀對帳功能、9 項實測及案例記錄。
- BLOCKERS: 真實 LLM runner、獨立子 Agent 實際執行、獨立功能沙箱及未見題/人類評審尚未核驗；私人工作區未替使用者建立；不因此停止可安全進行的合成實作。
- WRITE_OWNER: 僅 Agent 候選分支；main/Release、外部專案、真實個資、付費模型或正式部署不在本次授權內。
- SYNC_STATUS: B001_SOURCE_AND_TEST_READBACK_VERIFIED; LOCAL_FUNCTIONAL_PASS; REMOTE_FULL_CI_PENDING; REAL_RUNNER_NOT_RUN; 文件新 SHA 的 CI 另查。
- NEXT_ACTION: 查 B001 同 SHA CI 結果，修正必要回歸；P0-2 將下列 B001 實測案例主動檢索並應用於 B002 設備借用，執行庫存/保留量、並行交易、故障回退及唯讀缺庫負測。比較有無經驗的測試與修復差異；不以公開事先知道的案例稱獨立盲測。

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
| P0-1 | B001 社區工作坊：需求→規格→架構→DAG→可執行垂直切片→QA；額滿候補、重複報名、需求衝突、未知寫入復原 | 獨立功能正反測、可重現的修復紀錄；公開合成實作與真實 Agent 評測分列 | LOCAL_FUNCTIONAL_PASS / CI_PENDING |
| P0-2 | B001 案例記錄、蒸餾，遷移到 B002 公用設備借用 | 相關案例被實際取用；新任務功能測試，對照有/無經驗和適用限制 | NEXT / B001_CASE_READY |
| P1-1 | 主動回饋事件、分層記憶檢索、技能專業深度、技術探索、任務池/覆盤 | 新工作階段重讀、無跨案混用；測試實際檢索與回饋行為 | PROPOSED |
| P1-2 | 專家獨立協作與交接 | 有授權平台才做真子代理；獨立 QA、交接與整合證據；無平台標單 Agent 分工 | BLOCKED_REAL_RUNNER |
| P2-1 | 隔離合成完整系統：前後端、資料庫、權限、後台、預約、復原 | 可操作成品、端到端功能及安全測試 | PROPOSED |
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
