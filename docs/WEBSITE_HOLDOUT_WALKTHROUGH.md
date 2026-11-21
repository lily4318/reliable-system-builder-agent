# 私人建站能力評測｜使用者與評閱者操作手冊（Windows）

本手冊是 [WEBSITE_HOLDOUT_EVALUATION.md](WEBSITE_HOLDOUT_EVALUATION.md) 的操作版，不替代其中五構面評分錨點、資料隔離與授權原則。只使用 Agent 候選版。**未找到已授權的真實 runner 時，只做 A 段公開合成演練及 B 段私人案例準備；不做 C 段真實模型試跑。** 不需要提供 API Key 或建立 GitHub Secret。

## A｜先用公開合成資料熟悉操作（不需要其他評閱者）

1. 打開 https://github.com/lily4318/reliable-system-builder-agent/pull/7 ，確認 PR 頁顯示 Draft。點入候選分支 candidate-agent-capability-workbench-20261114 的程式碼頁面，按綠色 Code → Download ZIP（介面可能因 GitHub 調整而異）。解壓至自己的本機資料夾，勿選研究正式專案資料夾。確認資料夾含 AGENTS.md 和 src/website_holdout_walkthrough.py；若找不到，先確認下載的是 PR #7 的候選分支而非 main。
2. 在檔案總管開啟該資料夾，點選網址列輸入 powershell 並按 Enter。執行 `py -3 --version`，確認 Python 3.12（本 repo CI 使用 3.12）。若找不到 py，可試 `python --version`；若都沒有，至 https://www.python.org/downloads/windows/ 選擇 Python 3.12 可用的 Windows 安裝程式，使用官方安裝方式，完成後重開 PowerShell 再查。若校方或公司限制安裝，停止並請管理者確認，無須提供任何帳號憑證。
3. 在 PowerShell 執行 `py -3 -m src.website_holdout_compare protocol`，確認最低五題、每份成果兩位評閱者、0–4 分，以及模型未執行狀態。若出現 No module named src，回到包含 src 的解壓根目錄再執行。
4. 選擇經確認未共享、未同步且僅本人可存取的本機目錄；以下使用 LOCALAPPDATA 示意（仍須使用者核對權限）。執行：

   ```powershell
   $demo = Join-Path $env:LOCALAPPDATA ("AgentRehearsal-" + (Get-Date -Format yyyyMMdd-HHmmss))
   py -3 -m src.website_holdout_walkthrough rehearse --directory "$demo"
   explorer.exe "$demo"
   ```

   預期終端顯示 SYNTHETIC_REHEARSAL_ONLY、5 題、10 份規格、20 筆合成評分、差值 0；三個真實執行／案例／人工評分旗標均 false。若遇到目錄已存在，改新目錄名稱，不刪除舊檔。若權限不足，改用已允許的私人位置。不得使用正式專案目錄。

5. 在檔案總管依序查看 cases.json、manifest.json、specifications 資料夾、review-packet.json、reviewer-1-blank.json、reviewer-2-blank.json、reviews.json、comparison.json。右鍵 → 開啟方式 → 記事本（或已安裝的 JSON 編輯器）；不要將真實內容貼到聊天或雲端 JSON 工具。這個演練全部來自公開 W101–W105，**不是未見題**，填好的 synthetic 檔是固定假評分，不是人工判斷。完整合成結果留本機，CI 僅執行合成測試。

## B｜獨立案例作者：建立真正私人未見題

1. 由未參與 Agent Prompt／評分器開發者擔任作者；兩位獨立評閱者與必要的第三仲裁者先排定，另外指定對帳者。五題最低數量是既有候選規準，非統計充分性的承諾。
2. 對帳者另建新資料夾，與 A 段合成演練完全分開：

   ```powershell
   $work = Join-Path $env:LOCALAPPDATA "AgentPrivateWebsiteEval-001"
   New-Item -ItemType Directory -Path "$work"
   New-Item -ItemType Directory -Path "$work/specifications"
   ```

   若已存在，停止並改用不同名稱。確認 Windows 檔案總管 → 資料夾右鍵 → 內容 → 安全性，僅給有工作必要的人員存取；另行檢查共享與同步狀態。不得在 Git 儲存庫內或公開同步目錄內存檔。評閱者只能取得自己的評閱包與空表，不可取得整個工作區。
3. 在私人位置用記事本新建 UTF-8 的 cases.json。檔名儲存時選「所有檔案」，避免變成 cases.json.txt。照原規範的 JSON 格式，建立至少 H001–H005，各含 id、至少 25 字的 brief 與 answers 的 13 個固定欄位（purpose、audience、journey、pages、identity、forms、slots、notice、admin、privacy、integrations、experience、release）。未答填 null；不可用真實個資。可參考公開格式，但不得把已公開 W101–W106 改名當成 holdout。作者另存預期需求與評閱準則在受限位置，不交給 Agent。第一個完整格式例見原手冊第 2 步。
4. 封存：

   ```powershell
   py -3 -m src.website_holdout_compare seal --cases "$work/cases.json" --output "$work/manifest.json"
   ```

   檢查 case_count 至少 5，commitments 對應 H 編號及 64 位 SHA256，沒有 brief 或 answers 正文。封存後勿改 cases.json；若需修正須由案例作者重新凍結新版本，不得偷換舊 manifest。這只是內容承諾，不證明作者獨立或案例確實未見。

## C｜真實 Agent 執行者的停止點

目前未核驗可授權模型 runner。因此 **B 完成後只能停止，不能自行照 A 段填假輸出並進行真實能力比較**。不要求帳密、Token 或費用。若未來已有使用權限的環境，由管理者在自己的平台確認模型版本、Agent 執行方式、工具範圍、資料處理及費用授權，提供不含憑證的狀態；沒有確定的實際平台前，不假造 UI 路徑。

取得另行授權後，才能在相同模型、runner 及預算下，把相同私人案例交給兩個不同的 Agent 版本。完整記錄 Agent commit SHA、Prompt SHA、執行者與執行證據。正式 main 若尚無相同輸出契約，先釐清可比較的舊版本與固定輸出要求，不以不同任務、不同資源或補寫答案來製造提升。將每題前後版完整 JSON 存於 specifications，使用隨機不含 phase 的 UUID。PowerShell 可用 `[guid]::NewGuid().ToString("N")` 產生識別代碼，`(Get-FileHash -Algorithm SHA256 -LiteralPath "<實際完整檔名>").Hash.ToLower()` 核對檔案 SHA。依原手冊第 5 步完整填寫 bundle.json；每題兩份，不給評閱者版本對照表。

## D｜評閱者：取得原始需求與匿名規格，而不是無上下文的文件

對帳者執行：

```powershell
py -3 -m src.website_holdout_walkthrough prepare-review --cases "$work/cases.json" --manifest "$work/manifest.json" --bundle "$work/bundle.json" --workspace "$work" --output "$work/review-packet.json"
py -3 -m src.website_holdout_walkthrough rating-template --packet "$work/review-packet.json" --reviewer-id REVIEWER_A_0001 --output "$work/reviewer-a.json"
py -3 -m src.website_holdout_walkthrough rating-template --packet "$work/review-packet.json" --reviewer-id REVIEWER_B_0002 --output "$work/reviewer-b.json"
```

- 確認 review-packet.json 每項只有匿名 ID、brief、原始 answers 與 specification；輸出順序已打散。仍要人工核對規格正文是否洩漏版本或模型資訊；若有洩漏，該批盲態不可宣稱成立，須另行處理。不得直接改原始模型輸出內容或覆寫雜湊。
- 只將評閱包及各自空白表，以核准的私人方式分別交給兩位評閱者；不分享 bundle、評閱者對方結果或標準答案。評閱者使用記事本／JSON 編輯器開啟自己的表，對照 output_id 與原始需求，依原手冊五構面評 0–4；將 null 改成整數，空字串改成至少 12 字具體理由。不得改 output_id、reviewer_id 或欄位名。
- 可隨時修訂自己的文字，直到自行確認並儲存完成，**欄位或選項修改不會傳送**。此處為本機文字表單與 CLI，並非已完成瀏覽器可點選評分 UI；原規格的逐項接受、修改、不採用、另行確認契約由既有測試驗證。實際評閱介面／Agent UI 尚需真人 UAT。
- 各自確認每份規格五構面都填完，才以核准的私人方式交付對帳者。每份 10 項輸出者的評分表應有 10 筆 ratings；兩人共 20 筆（五題時）。不可用自動合成評分替代。

## E｜對帳者：合併與比較

```powershell
py -3 -m src.website_holdout_walkthrough combine --first "$work/reviewer-a.json" --second "$work/reviewer-b.json" --output "$work/reviews.json"
py -3 -m src.website_holdout_compare compare --manifest "$work/manifest.json" --bundle "$work/bundle.json" --reviews "$work/reviews.json" --workspace "$work" --output "$work/comparison.json"
```

若 combine 拒絕，檢查兩份評分是否完整、ID 不重複、分數合法、理由足夠，不用重做已通過資料。若 compare 拒絕，對帳者核對 SHA、版本配對、模型／資源一致性，以及逐構面分差。任何分差 ≥2，由兩位原評審以外的第三人依匿名需求與規格仲裁；記錄 output_id、dimension、adjudicator_id、score、reason 至新的 reviews-adjudicated.json，不覆寫原先評分，重新以新檔名比較。若無仲裁者，不生成完整比較。

打開 comparison.json 核對 case_count、rating_count、case_summaries、dimension_mean_deltas、paired_mean_delta_on_0_to_4_scale 及結構檢查。欄位中的 false 是明確的證據邊界：比較器只計算已提交評分，不證明模型真實執行、私人題獨立或 Agent 進步；真人使用體驗仍需實測。不得把特定結果當作正式部署或發布許可。

## 可重現自測

```powershell
py -3 -m unittest discover -s tests -p "test_website_holdout_walkthrough.py" -v
py -3 -m unittest discover -s tests -v
py -3 -m src.quality_gate check
```

所有公開測試只使用合成案例。完整候選規範見 [原評測手冊](WEBSITE_HOLDOUT_EVALUATION.md)。不需要使用者現時建立真實 holdout 或操作 runner；本輪只提供與測試可操作的離線路徑。
