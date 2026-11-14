# 13 題網站需求訪談｜本機瀏覽器操作指南（候選）
此工具只服務 Agent 本身的需求訪談訓練，重用 src.website_discovery.build_spec。不是線上招募網站或真正 LLM。無外部依賴、無 API Key、無正式寫入、無自動部署。Python 程序只監聽 127.0.0.1；瀏覽器與本機程式交換答案，不送至任何外部服務。不使用真正個資或未見評測題。不要將本機服務對外轉發。

## 開始操作（Windows）
1. 打開 [Draft PR #7](https://github.com/lily4318/reliable-system-builder-agent/pull/7)，點候選分支 candidate-agent-capability-workbench-20261114，再點 Code → Download ZIP。解壓至本機新的資料夾；確認含 src/website_intake_ui.py 及 examples/website-intake/index.html。
2. 在檔案總管開啟解壓後的根目錄，網址列輸入 powershell，按 Enter。輸入 `py -3 --version`，建議使用 Python 3.12（CI 版本）。如無 Python，參考 [原評測操作手冊](WEBSITE_HOLDOUT_WALKTHROUGH.md) 的官方安裝流程。不要把帳密交給 Agent。
3. 執行 `py -3 -m src.website_intake_ui`。若出現找不到模組，檢查目前資料夾是否包含 src。若 8765 埠被占用，可執行 `py -3 -m src.website_intake_ui --port 8766`。畫面應顯示本機網址；打開 Chrome，輸入 http://127.0.0.1:8765/（若改埠則相應調整）。不要直接雙擊 HTML，因為它需要本機 Python 產生規格。
4. 可由已知的回答 JSON 預填：啟動時加 `--answers "C:/你的私人資料夾/answers.json"`，或畫面中選取 JSON 檔後先看預覽，再點「確認載入預填答案」。格式是單一 JSON 物件，鍵名為 purpose、audience、journey、pages、identity、forms、slots、notice、admin、privacy、integrations、experience、release；值為文字或 null。缺少欄位留空，禁止陌生欄位。請勿用真人個資。若想試用，可從畫面選 W101–W106 並明確點「載入並取代目前答案」。
5. 逐題修改自由文字，或從常用回答選「待確認／不適用／不需要」，再自行修改。點「產生規格草稿並檢視推導」。應看見完整原始回答、功能／非功能、架構、交付維運、需求追溯、測試及待確認項。
6. 每項推導選「接受／修改／不採用」，文字會預填至編輯區；修改後點「確認本項文字」。可取消或切換選項；任何文字修改使該項與整份確認失效。修改任一訪談答案會清除整份舊草稿與所有決策，重新產生。無推導事項時仍須確認整份草稿。
7. 檢視完整規格預覽及每項決策與來源題目，點「確認整份本機草稿」，此時才啟用「匯出已確認草稿 JSON」。按匯出後由瀏覽器下載文件，包含原始規格、明確的逐項決策與已修改文字、回答，以及本機確認標記。草稿中的推導仍保留為原始未核准提案；拒絕與修訂記錄另列，後續 Agent 必須依決策整合，不可以將被拒絕的提案當成正式需求。這不是正式規格核准、外部寫入或部署授權。
8. 結束時關閉瀏覽器，回到 PowerShell 按 Ctrl+C 停止。未匯出的內容僅留在目前頁面記憶體，重新載入頁面會失去修改；不使用 localStorage 或雲端。匯出的 JSON 由使用者自行存放於私人目錄，不需要上傳 GitHub。

## 六類合成瀏覽器驗收
- W101–W106 全部由 headless Chromium-family browser 實際操作 DOM：載入預填、逐題修改、生成規格、逐項接受／修改／不採用、取消、阻止空文字、手動確認、整份確認後才開啟匯出、編輯答案後舊確認失效。
- 另測啟動預填、檔案選取預覽與確認、非法 JSON 欄位不覆蓋既有需求、常用回答與自由編輯。產出 JSON Blob 從實際匯出按鈕攔截檢查，不測真實作業系統下載視窗或落盤。
- Python HTTP 測試覆蓋六題與原產生器輸出完全一致、限定本機 Host/Origin/token、無外部授權、未知鍵及過長回答拒絕。測試專用端點僅 test_mode 開啟。
- 使用已安裝 Chrome/Chromium，不下載瀏覽器或模型。測試指令：`python -m src.website_intake_browser_test`。手動指定瀏覽器：`py -3 -m src.website_intake_browser_test --browser "C:/Program Files/Google/Chrome/Application/chrome.exe"`。CI 使用 Linux 現有 Chrome，僅合成資料；測試程式使用暫存瀏覽器設定檔。只在合成受控測試中使用 --no-sandbox，不用於日常使用。
- 尚未進行 Windows 真人 UAT、真實使用者下載落盤、真正模型語意理解或七角色執行。這是離線互動與確定性推導測試，不是 Agent 能力提升證明。現有規格產生器仍採固定關鍵詞及否定分句，須獨立人工確認。
