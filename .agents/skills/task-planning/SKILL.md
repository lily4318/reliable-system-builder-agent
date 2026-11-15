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

### 需求修訂與重驗
已確認需求變更先 review 確定受影響的最上游 task 與當前 revision，依操作手冊使用 revise 保存正式來源、明確確認、修訂 title/deps/gates/checks（需要時）、原子使所有下游失效，不沿用舊 PASS。已決政策另建 decision ID、更新 gates，不覆寫舊政策。若有 RECOVERY_REQUIRED 或 recovery_blockers，先確認舊操作者停止、唯讀查核部分操作再 recover，不以 resume 復活失效任務。以新 revision 與從未用於該 task 的 session 執行 start/finish，失敗或版本競寫須回讀。同步正式來源與適用 handoff，任務池不會自動監聽需求或替代外部版本/授權。

### 依賴重接及舊 worker 隔離（NATIVE-EP-009-RECOVERY-FENCE）
revise 與 extend-topology 皆不得利用新圖解除舊 worker 保護。真正改變 deps 集合時，先在同一交易核對 affected（該 task 及傳遞下游）是否 RUNNING/RECOVERY_REQUIRED；若是，整筆拒絕且不寫需求 artifact、revision 或事件。確認舊操作者停止、唯讀核對部分操作、依 recover 或原正常完成流程處置後，再以最新 revision/來源重新評估。相同依賴及內容修訂仍走原失效守門，獨立支線不停止。此防護不保證已被舊版重接的歷史資源圖可還原；需人工核對，不直接重試。原 EP-04、CI 43703424124 red / 43703631052 green 及主檔記錄。

### 已綁定池的增量拓撲
任務拆解遇已綁定池，不直接 add 或用分開寫入繞過 guard。review 同一 snapshot 取得全任務 revision 與 artifact_heads，依正式來源使用 extend-topology 明確新增節點與前置邊；檢查唯一 producer、catalog 祖先、DAG、gate、受影響既有 worker。保留無關 DONE 與歷史；受影響 DONE 及產物重驗。活躍受影響 worker 先對帳，不改其依賴；未知提交查 extension-status，禁止盲重送。詳細契約見 docs/TEAM_WORKBENCH.md；根需求仍用原 combined revise。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 plan；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。
