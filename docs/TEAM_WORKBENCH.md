# 技能化團隊工作台（整合候選）

## 設計機制
參考使用者提供的 AI 團隊學員包第一天版的指令分流、SKILL 模組、共用資料、案例卡與經驗整理模式；獨立設計工程技能，不複製原始業務內容、措辭或素材。保留主框架與四候選功能：PR4 的 task_scope、PR5 的 engineering_workflow、PR6 的離線 LLM 評測與來源查核模組（保留，不再擴張）、PR7 的需求訪談、能力工作台、人工教學、可編輯確認及瀏覽器測試。重疊的品質閘、測試與設定合併；歷史文件保留在原 PR，整合版以此入口與 PR7 共通文件為準，另讀各功能專用手冊。

## 使用者如何工作
- 在 AI 可讀取本 repo 的工作區中直接說「建立網站」「整理規格」「繼續」「修好報名功能」「記錄這次修復」「整理學到的事」。AI 需先讀 AGENTS.md、對應 SKILL.md、最新正式來源。
- 七角色依需要工作；無子代理平台即單 Agent 按角色協作。每次用真實工作產物交接。不因有角色名稱就宣稱已執行。
- 新網站先訪談並確認規格、必要人工操作有逐步教學、確認選項先可編輯再送出。既有功能沿用 src.website_intake_ui、src.website_discovery、src.human_walkthrough。記憶工具不取代使用者確認。

## 本機工作區逐步操作（Windows）
1. 下載整合候選 PR 分支的 ZIP，解壓到獨立本機資料夾。打開檔案總管至含 src 的根目錄，輸入 powershell 按 Enter。
2. 執行 `py -3 --version`，建議 Python 3.12。無 Python 時依 docs/WEBSITE_HOLDOUT_WALKTHROUGH.md 的官方安裝步驟；不需要 API Key。
3. 選私人、未共享且未同步的位置，核對檔案總管右鍵 → 內容 → 安全性。以下示範合成專案用法，不能選正式研究資料夾或 Git repo：

```powershell
$work = Join-Path $env:LOCALAPPDATA "SystemBuilder-Synthetic-001"
py -3 -m src.team_workbench skills
py -3 -m src.team_workbench init --workspace "$work" --label "合成開發專案"
py -3 -m src.team_workbench context --workspace "$work" --skill project-intake
```

應見 12 項技能、專案標籤與空產物。init 拒絕已存在路徑；續作用原 workspace，不重新 init。路徑不得在 Agent repo 或其上層。

4. 由 AI 實際完成訪談紀錄，存於已授權私有位置的 requirements.md（可用記事本 UTF-8），再登錄：

```powershell
py -3 -m src.team_workbench handoff --workspace "$work" --skill project-intake --file "$work/requirements.md" --source-ref "使用者確認前的需求草稿"
py -3 -m src.team_workbench context --workspace "$work" --skill requirements-spec
```

回讀產物內容與依賴。正式確認後再保存規格；依 catalog 的 requires/produces 實際交接。更新需求會標舊下游產物 current=false，不能用來施工。current 並非語意正確、實際授權或正式版本判定。

5. 記錄真實偏好或案例：在私人資料夾用記事本寫 note.md，清楚標記證據／限制，不含憑證或個資。僅明確使用者偏好標 user-stated；有實際觀察紀錄標 observed；推測標 candidate。知識、案例和 lessons 用 kind 分別保存。

```powershell
py -3 -m src.team_workbench remember --workspace "$work" --kind lesson --topic "booking" --file "$work/note.md" --evidence "實際驗收或測試紀錄位置" --basis candidate
py -3 -m src.team_workbench distill --workspace "$work"
```

完全相同內容、依據、類別、主題與狀態的活躍紀錄會去重；同一主題有多條則列待審。這是有界去重及人工整理，不是自動語意蒸餾。若要合併語意相同的內容，可先寫新條目，然後逐項由人確認替代。只有實際獲得同意，才能以真實 ID 執行 `resolve --workspace "$work" --retired 1 --retained 2 --reason "使用者實際確認原因" --confirm`（ID 僅示意）。原始紀錄與決策仍保留。若回報衝突或依據不足，不自動挑最新日期覆蓋。

6. 續作：`py -3 -m src.team_workbench context --workspace "$work" --skill resume-project`。同一私有工作區可於新對話重新讀取，但必須由平台具備檔案讀取權限；無法自動跨平台同步。輸出包含私人內容，只能留在授權環境，不得貼到公開 PR 或 CI 報告。無需現在由你建立私人工作區；可先用合成測試驗證。

## P1-1｜任務導向檢索、回饋與跨工作階段案例引用

保留原 workbench.sqlite3、原本的 artifacts/memory/resolutions 及操作；src.workbench_learning 為同庫增量工具，不另存第二套私人記憶。只有已授權工作區才可執行 setup；先備份私人資料庫並依既有 ACL 規則限制存取。setup 加三個 learning_* 表並匯入 B001/B002 公開合成案例簡要內容、來源與可檢索標籤；重跑不重複、不復活已退休案例，遇同名未登錄舊案例則停止由人審查。不自動寫入任何外部專案。

以下 PowerShell 指令假定已依前節建立 $work，示範合成任務、無個資。以 UTF-8 另存輸入 JSON 於私人工作區，不要往公開 PR 貼上輸出。

```powershell
py -3 -m src.workbench_learning setup --workspace "$work"
```

建立 task.json：

```json
{"skill":"debug-and-repair","task":"SYN-REPORT","query":"SQLite 唯讀 缺庫 report recovery reconcile","budget":8000,"limit":5}
```

```powershell
py -3 -m src.workbench_learning context --workspace "$work" --input "$work/task.json"
```

檢查返回的 matched_terms、case topic、memory ID、證據位置與 Scope；公開兩案例為本機 SQLite 合成經驗，不保證適用遠端、多節點或正式資料。搜尋採英文字詞及中文雙字詞交集排序，不是語意模型、向量檢索或正式權限；必要產物全文和案例正文/證據受字元配額限制，索引僅列 ID、來源及 current。配額不含 JSON metadata；過期產物不傳正文，NEEDS_PREREQUISITES/NEEDS_FULL_READ 必須先補讀原產物（必要時用既有 team_workbench context），不得截斷規格後直接施工。artifact_index 目前仍是同一專案的最新產物類別，不是逐任務版本；確認來源適用當前任務。私有工作區互相隔離，不由 task ID 取代專案隔離。候選與同主題未解衝突的記憶只列 review_candidates，不進入可採用清單。

完成真實操作或判定案例不適用後，建立 cite.json（以下 ID 1 僅為示例，先核對 context 的實際 ID、skill/task/query/budget/limit 一致；evidence 需換成實際可定位證據）：

```json
{"skill":"debug-and-repair","task":"SYN-REPORT","session":"session-1","query":"SQLite 唯讀 缺庫 report recovery reconcile","memory_id":1,"decision":"applied","evidence":"實際測試檔案、案例及結果"}
```

```powershell
py -3 -m src.workbench_learning cite --workspace "$work" --input "$work/cite.json"
```

引用重算目前可選案例才能保存；decision 可為 applied 或 not_applicable。操作者宣告引用並非獨立執行證明。遇實際測試失敗、修復、QA 退件、需求修正或偏好事件，Agent 主動輸入 feedback.json；這是工作流程觸發，並非背景監聽、模型推論或自動升級規則：

```json
{"task":"SYN-REPORT","session":"session-1","event_id":"report-fix-001","event_type":"test_fix","topic":"SQLite report","content":"合成報表缺庫時拒絕操作，未建立空檔","evidence":"實際功能驗收位置"}
```

```powershell
py -3 -m src.workbench_learning feedback --workspace "$work" --input "$work/feedback.json"
```

event_type 支援 test_failure、test_fix、qa_rejection、requirement_change、preference。事件 ID 相同且內容一致去重，內容不同則拒絕；均存為 candidate，不能自動改寫正式規格/長期偏好。由既有 remember/resolve 人審流程另存已核驗記憶、處理衝突並保留歷史。新的 Python 程序或對話可用同一授權工作區重跑 context，將 session 改為新 ID，並以 history.json（內容 {"task":"SYN-REPORT"}）回讀：

```powershell
py -3 -m src.workbench_learning history --workspace "$work" --input "$work/history.json"
```

context/history 真正唯讀，不建缺失資料庫，舊工作區未 setup 先回報，不隱式遷移。history 保留已引用案例及回饋 ID；檢索不等於實際採用。真實跨對話、跨平台、語意蒸餾及自動事件感知仍待具備授權執行環境後測試。

## P1-1b｜技術探索及持久化任務池

同一已授權的 workbench.sqlite3 使用 src.workbench_tasks；明確備份後執行 setup，新加 task_pool、task_decisions、task_events，不改原有產物和記憶。讀取透過 mode=ro，不自動建立缺庫。以下為合成操作示例，非外部專案或產品核准。

操作命令：`py -3 -m src.workbench_tasks <action> --workspace "$work" --input "$work/task.json"`（setup/review 不需 input），輸入 JSON 為 action 的參數。每步使用當前真實 ID；可先執行 review 回讀。

| action | JSON 示例或用途 |
|---|---|
| setup | 建立三張表，可重跑 |
| question | {"decision":"D1","prompt":"錯誤輸入的 UI 提示？"} |
| add | {"task":"spec","title":"列明未決政策","priority":0,"deps":[],"gates":[],"checks":["R3"]} |
| add | {"task":"core","title":"半開區間核心","priority":1,"deps":["spec"],"gates":[],"checks":["R1","R2","R4"]} |
| add | {"task":"ui","title":"正式錯誤提示","priority":2,"deps":["core"],"gates":["D1"],"checks":["UI"]} |
| start | {"task":"spec","session":"session-1"} |
| finish | {"task":"spec","session":"session-1","results":{"R3":"PASS"},"evidence":"實際規格與待核決策紀錄位置"} |
| resume | {"task":"core","previous_session":"session-1","session":"session-2","evidence":"實際查核前一操作者已停止及目前狀態","confirmed":true} |
| resolve | {"decision":"D1","answer":"已確認的實際政策","source":"明確使用者決策來源","confirmed":true} |
| review | 唯讀取得 task 狀態、依賴、開放與已決問題及來源、running_review、next_ready、驗收次數、失敗次數、完成數與事件 |

依賴必須先存在、不得自循環，優先級 0–99（越低越高）。以 BEGIN IMMEDIATE 防止同任務競寫；RUNNING 不自動逾時接管。「confirmed」是操作者聲明，只有已有真實明確確認與證據才可使用；不等同部署或正式啟用授權。失敗結果保留歷史與證據，返回 PENDING 且不解鎖下游。既有決策不可直接覆蓋；新決策及修改任務關係需另行版本化設計，當前不支援重開 DONE 或動態改 DAG。新程序用 review 讀回後才行動；若任務仍 RUNNING，不盲目接管。例中的 UI 決策沒有真實使用者確認，正式 UI 工作保持 PENDING。

技術探索示例見 src/b003_shifts.py 與 tests/test_b003_and_tasks.py：線性與排序區間判斷對照離散分鐘集合 oracle，原型 INVALID 不是正式產品錯誤政策。此工具的驗收由操作者提供證據，並不自動執行程式碼或替代獨立 QA；記憶、任務與事件在同一 DB，任務仍不代表逐任務 artifact 版本。未建立正式私人工作區。

## 共用知識與案例
公開 repo 的 knowledge/ENGINEERING_PATTERNS.md、templates/WORK_ARTIFACTS.md 提供尚需依專案驗證的通用工作方法和格式；真實工作記憶與案例保留私有。去識別化且經人審查的案例才可循原 learning-policy 及獨立 PR 進入公共知識庫。跨專案共用偏好應另設有權限的私人工作區，經明確確認後選取適用條目，不自動混合兩案資料。持久化資料不加密、依賴 OS ACL；憑證不得保存，正規表示式只防部分常見金鑰。

## 測試與效力
`python -m unittest discover -s tests -v`；`python -m src.quality_gate check`。新增工作台測試使用臨時 SQLite、合成產物；CI 不是模型自主開發成績。現有安全門檻完整保留，不新增來源稽核功能。本候選不授權實際付費模型、部署、外部專案、merge 或 Release。
