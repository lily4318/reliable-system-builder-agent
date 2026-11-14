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

## 共用知識與案例
公開 repo 的 knowledge/ENGINEERING_PATTERNS.md、templates/WORK_ARTIFACTS.md 提供尚需依專案驗證的通用工作方法和格式；真實工作記憶與案例保留私有。去識別化且經人審查的案例才可循原 learning-policy 及獨立 PR 進入公共知識庫。跨專案共用偏好應另設有權限的私人工作區，經明確確認後選取適用條目，不自動混合兩案資料。持久化資料不加密、依賴 OS ACL；憑證不得保存，正規表示式只防部分常見金鑰。

## 測試與效力
`python -m unittest discover -s tests -v`；`python -m src.quality_gate check`。新增工作台測試使用臨時 SQLite、合成產物；CI 不是模型自主開發成績。現有安全門檻完整保留，不新增來源稽核功能。本候選不授權實際付費模型、部署、外部專案、merge 或 Release。
