---
name: task-planning
description: "拆解任務、規劃施工。system-lead 角色；交付 plan。"
---
# task-planning｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：specification、architecture。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
為每個工作包列出需求 ID、owner、實際檔路徑、前置工作、驗收與風險。依 DAG 先完成最小垂直切片；僅獨立任務平行，必要人工決策用可修改選項。

### 持久任務池（同一授權 SQLite 工作區）
依 docs/TEAM_WORKBENCH.md 使用 src.workbench_tasks setup；以 question 保存未決決策，add 登錄 task ID、標題、優先級、已有依賴、決策 gates 及必須逐項驗收的 checks。未決產品政策僅阻塞相關工作；先完成明確且可獨立驗收的切片。review 讀取 next_ready、running_review、決策及歷史後，start 領取可執行任務。finish 要提交所有 checks 的 PASS/FAIL 與實際證據；失敗回待辦且留歷史，不把結構化自述當驗收。中斷任務先唯讀對帳確認舊操作者已停止，再以 resume 記錄舊/new session、證據及明確確認；禁止盲目接管或重送。遇未決規則只在真有確認來源時 resolve，不能以合成測試的確認代替正式核准。review 為新工作階段與覆盤入口，案例採用與回饋由 workbench_learning 記錄。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 plan；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。
