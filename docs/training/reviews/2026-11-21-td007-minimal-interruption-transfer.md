# TD-007｜高自主、低干擾、跨對話持續交付：最小打擾合成遷移（2026-11-21）

狀態：**使用者正式確認方向；原生程式與新測試已寫入並回讀；完整 CI 與真服務端到端驗收待證**。本 review 是 TD-007 的實作證據索引，不是訓練主檔、正式發布或新管理引擎。

## 來源與原則
- 權責：唯一訓練主檔 `docs/AGENT_CAPABILITY_TRAINING.md`、`docs/training/DECISION_LOG.md` 的 TD-007；保留 TD-004 七階段、TD-005-R2 專業能力優先、TP-010 工作偏好與回饋；現有八角色十五技能不變。
- 前置候選 PR #8 HEAD `769020142cbdcf1532a3563eb475fadac1f9d4de`，決策新增 `8de5849a2324d9256bb50a0f7432320d01f93421`、主檔新增 `8d4c1667e63442555d8794e53a5c9308de2c18d3`，GitHub 兩筆父子關係及檔案 blob 已回讀。
- 課堂技能包僅參考「逐步引導／使用者重要授權／工作進度跨對話」的抽象流程；不保存、複製或部署包內 GAS/LINE 程式、品牌個資及第三方教材。原工作台已具備 task/revision/fence/decision gates，不能再造任務池、重跑舊 SQL/SQLite 單元。

## 原創差異與取捨
既有 workbench_tasks.review() 會列出全部 open_decisions，適合稽核卻可能讓操作者在網站、資料表等已可先行完成時提前問遠期發布許可。目標是 **只提出當下阻塞的必要問題**，其餘已授權、相依可行且安全的工作連續進行；不減弱既有授權或資料版本守門。

採用小型 **純唯讀衍生檢視** `src/delivery_next_step.py`（程式提交 `a8ab3d2b0f32315fe3060c2b63473308dc3ea8d3`，已取得精確內容回讀）：接受現有 review 快照，按 priority/id 選可行任務；只要有 ready 任務，`ask_decision_ids=[]`；全部無 ready，且最早真正可開工任務僅因未解人類決策閘阻塞，才回報最小 gate 清單；RUNNING/RECOVERY_REQUIRED 無可行工作時轉 READ_ONLY_RECONCILE，不自動接管；全 DONE 仍標 `TASK_POOL_DONE_REQUIRES_INDEPENDENT_REVIEW`。每個輸出均標 authorization_granted=false、deployment_verified=false、independent_acceptance_verified=false。這不是排程器、權限 grant 或獨立真模型執行證據。

## 合成原生新驗收
- `tests/test_delivery_next_step.py`（提交 `6c2c28f72dfb231b118b48600bb977c846e50fa3`，檔案內容回讀一致，三個新 test 方法）：
  1. 7 個合成任務：spec → website/sheets → gas → LINE（D_LINE）→ qa → launch（D_LAUNCH）。前四項可推進時完全不問提前授權；只能在 LINE 就緒但缺授權時要求 D_LINE；真實 SQLite 中不具確認旗標必拒，外部新 Python 程序重新讀取同庫；read-only 前後 DB bytes 一致；LINE 合成失敗後依原 session 守門重試；必要 QA 完成才詢問 D_LAUNCH；任務 DONE 不冒稱已正式驗收。
  2. 已有在途 owner 的情境下獨立 ready 工作仍可做，沒有其他 ready 時轉唯讀對帳，不接管舊 owner。
  3. 缺工作、缺資料及不合法快照均明確 fail closed，不建立新任務資料。
- 原 `.agents/skills/resume-project/SKILL.md` 最小增量提交 `1f334380a084bacab76ed9a0843785b1ac53c4f1`、`.agents/skills/project-control/SKILL.md` 提交 `9af41e1ae237256038ee60aa5abae325e7c34b45`；兩個 blob 實際回讀與預期一致。
- 既有跨 session、原子修訂、資料庫競寫及舊 SQL/.NET 實驗仍保留，**不是此次新增單元的功勞**。三組新測試僅是在新的多服務交付場景對既有機制做有界組合與新選擇器行為回歸。
- CI：工作中的 Actions `44910697060` 最初於提交 `9af41e1ae237256038ee60aa5abae325e7c34b45` 進入 pending；此前中途提交跑次因後續提交而 cancelled。此時**尚無本次新測試 full CI 原始日誌／PASS 的證據**；後續以最後文檔提交對應 exact CI、job、raw logs、checkout SHA 及正常門檻驗證，不繼承舊 588/588 作為新單元結果。

## 真正成效與未驗邊界
- 120 分鐘目標僅適用事先確認範圍、帳號／存取工具／環境／合法授權已就緒的標準網站、LINE、GAS、Google Sheets 整合；測量始末、等待、人工介入、重工、遠端具體成果與安全/QA/真人 UAT。不得把合成流程的模擬執行當作已完成真服務連通、GAS 發布、OAuth/LINE、Sheets 交易、120 分鐘或跨 ChatGPT 對話實際自主工作。
- 原 TD-004 5.3.8–9 已驗不重做，5.3.10/5.3.11 舊 NEXT_ACTION 保留；獨立源驗 A07、實際真人 B10 與原 TD-005-R2 延期門檻不變。
- 工具／權限不足不得靠使用者反覆確認、揭露金鑰、關閉安全設定、盲重送未知 POST 或擅自替人批准來達時間。真正跨對話持續保存依正式 repo 或已授權私人位置，僅 UI 自述與聊天記憶不等於持久化。

## 可安全接續
1. 先驗目前候選 PR #8 最新 HEAD、最後相符的 CI 完整原始日誌及三新測試；若紅燈，讀失敗原因最小修復，不下修 oracle 或反覆重跑其他已通過舊實驗。
2. 在已確認來源及授權下實際以 `resume-project` 的 read-only 選擇器做另一次合成工作演練，觀察問句是否只在當前必要人類決策產生，並保留跨 Python process 真 DB 證據；對 LLM 在另一聊天獨立遵循仍標 UNVERIFIED。
3. 未經獨立授權，不得連真 LINE/GAS/Google Sheets 或正式部署；未形成端到端時間與人工負擔的可比較真證據前，不宣稱「兩小時已達標」。專業原課程 5.3.10–11 仍可平行接續。

## 原始日誌與修復接續（2026-11-21）
- [CI 44911019927](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/44911019927)，job 136867550198，候選 `96252a7` 的三個新方法均通過。整體 591 項有 1 個錯誤，發生於既有 Chromium 首次 `GET /json/list` 等待回應。後續品質步驟在該跑次被跳過。
- `7e0101402ea9c6d18f9b2763a375d54bcd6f8b31` 將頁面 target 查詢納入啟動期限，原功能驗收照常。新固定回歸覆蓋 TCP/HTTP 回應延遲（注入 TimeoutError）及空 target 名單後恢復。[CI 44912044275](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/44912044275) job 136869720465、checkout `f3516a6721dfc9865edbdaa3be05da0a0f822722`：592/592，真 Chromium DOM／CSV、三個 TD-007 方法及品質守門皆通過。歷史 runner 延遲根因、外部服務及真人驗收仍待證。
- Windows 隔離環境另行實跑 Chrome 在期限內仍未收到本機 target 回應（`TARGET_ENDPOINT_UNAVAILABLE`，同時有 `DEVTOOLS_LISTENING`）；此項本機真瀏覽器結果保留失敗，Linux 託管 CI 的真 DOM／CSV 另有獨立通過證據。未確立兩環境延遲同一根因。
