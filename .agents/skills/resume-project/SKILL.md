---
name: resume-project
description: "繼續、目前進度。system-lead 角色；交付 resume-note。"
---
# resume-project｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：依任務所需。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
讀工作區實際產物索引、前置依賴及最近記錄；檢查正式來源與版本。找最靠前未完成且可安全推進的工作，不靠聊天摘要假定完成；阻塞時說明具體缺件並提供可操作替代路徑。

若授權工作區已配置 src.workbench_tasks，先以 review 唯讀取得 next_ready、running_review、完整決策來源、驗收歷史與阻塞依賴，再選最高優先可執行任務；未初始化不隱式遷移。RUNNING 須先核對當前實際操作者、產物與狀態，只有確證舊操作者停止且取得明確確認才 resume；不能僅因對話更換接管或重送。案例與回饋沿用 workbench_learning history/context；不要將已完成的驗收或舊產物視為新版本的自動核准。

### 修訂後接續
review 必須同時檢查 task revision、recovery_review、recovery_blockers 與舊事件。不得復用舊 session；已失效的 RUNNING 須先查核舊程序已停止及部分操作，用 recover 回 PENDING 並重新按依賴驗收。只有未失效且同 revision 的 RUNNING 經確認才 resume 到新 session。start/resume/finish 使用所讀當前 expected_revision；競寫、錯版本、未知結果先唯讀對帳，不盲目重送。已完成但因新確認需求重新開啟的任務須用新驗收證據，且同步檢視適用正式來源/產物相依；工作台不能終止外部程式或核准部署。

## TD-007｜最小打擾的跨對話下一步（已確認核心成效目標）
已取得授權且可用的私人工作台，先用原 `src.workbench_tasks review` 讀當前同版 task/revision、決策、在途與復原狀態；可用 `python -m src.delivery_next_step --workspace <已授權工作區>` 做**唯讀候選下一步**：有可安全推進的 ready 任務就不提前詢問遠期確認；沒有 ready 且真正遇到當前 decision gate 才只詢問該 gate；RUNNING/RECOVERY_REQUIRED 不自動接管，先唯讀對帳；全部 DONE 仍須獨立 QA/UAT/授權，不能當作正式發布。此選擇器無新增任務庫、無外部連接、無自動寫入／批准；具體施工仍逐步依正式來源、現行 scope、必要權限、前置和版本檢查。
在 REPO_NATIVE/READ_ONLY 模式只能依原正式進度與授權真相人工判斷相同原則，不能假稱呼叫私人 CLI。每次具實際保存價值的對話即在原授權位置更新並回讀來源 SHA、真成果、未完成、實測、阻礙及下一安全動作；未保存成功明示而不冒稱持久記憶。約兩小時為使用者經驗參照。記錄實際歷時、等待、人工介入及各項真服務證據，依功能、安全與必要人類授權驗收。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 resume-note；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。

### 跨對話的能力收斂接續（CAPABILITY-CONVERGENCE-005）
從最新主檔 NEXT_ACTION 與有效決策查有界訓練停點、原 M2-2/A07/B10/UAT 與部署授權；TP-010 先核開工記憶與真工具，R2 專業訓練不受交付餘項阻塞；不因訓練完成假定交付完成。查原 APP blob、exact CI run/checkout/tree 與各自 local/model lab 原證據；不泛化 CI 綠燈至未執行 lab。真新對話 source-only 驗收另行，歷史首版停點不阻 R2 專業訓練；外部驗收與發布另核授權，不重問已有授權或盲接下一階段。詳 [原覆盤](../../../docs/training/reviews/2026-11-16-research-handoff.md)。
