# 任務目標辨識：改善 Agent 本身與應用 Agent 的分離（候選訓練）

## 目的與已觀察的泛化失敗型態
在多輪對話中，協作者可能把「使用者要求**訓練／改善 Agent 自身**」誤讀成「沿用上一個專案的程式施工」。這不是外部專案的 Bug，而是 Agent 的**任務辨識、來源路由與權限隔離**問題。本候選以去識別化合成案例描述此類錯誤，不導入任何外部專案的私人資料。

## 執行前的必填目標確認
1. 從**本輪最新明確使用者指令**抽取 `TASK_MODE`：`IMPROVE_AGENT`（改善本 Agent）、`APPLY_AGENT`（拿 Agent 處理指定專案），或 `UNRESOLVED`。
2. 固定列出 `AGENT_REPO`、`TARGET_REPO`、`PROPOSED_WRITE_REPO`、`AUTHORIZATION`。這些值都須有來源，不可因舊對話、Agent URL、前一個工作 Repo 或對話總結自行填入授權。
3. `IMPROVE_AGENT`：僅本公開 Agent Repository 指令、評測、測試、原 CI 與候選 PR 可成為修改目標。不得因相關經驗涉及某網站，便修改該網站。改善規則不是 LLM 權重重訓。
4. `APPLY_AGENT`：外部專案的讀取、程式寫入、部署、真人資料各需獨立的目標與授權，不得因能讀取本 Agent Repo 就推論有外部權限。
5. `UNRESOLVED`／來源競寫／跨 Repository 目標衝突：停止寫入；可安全唯讀查證或提出精確問題。最新使用者對目標的更正立即生效。
6. 從錯誤新增合成案例與負測，只有獨立分支、PR、CI、人類審核完成後才能升為正式 Agent 版本；不能自我核准。

## 可重現的結構化守門
```bash
python -m unittest discover -s tests -v
python -m src.task_scope validate
python -m src.task_scope evaluate --output output/task-scope-evaluation.json
python -m src.quality_gate check --output output/quality-gate.json
```

`evaluations/cases/task_scope.json` 的 `example_utterance` 是**供人類查閱的合成示例**。評測程式**只**檢查已明確標註的 `intent`、`target_repo`、`proposed_write_repo` 和授權欄位，故只能證明「當前置意圖標註正確時，程式是否守住目標」；不能證明 AI 能從陌生對話推對意圖。此集合公開且非獨立盲測。不得把 100% 政策通過率說成模型訓練完成或真實任務辨識準確率。

## 未來真正的 Agent 能力評測
由獨立標註者準備不同語境的**新對話**，請實際 LLM 先輸出 `TASK_MODE/TARGET_REPO` 而不提供標準答案，分別計算目標誤寫率、混淆矩陣、遇更正的恢復率、拒絕未授權寫入比例。需保存模型版本、提示版本、資料切分、評分程式與人工複核證據。訓練底層模型權重則需額外模型／資料、可重現訓練流程與授權，非此 PR 的範圍。

## 本候選可宣稱與不可宣稱
- 可宣稱：已有結構化任務守門、合成正反例、品質檢查、受審查的 Candidate PR（僅在實際 CI 回讀後稱通過）。
- 不可宣稱：模型已微調、對話意圖自動辨識率已驗證、具有真實外部系統執行能力、已替使用者部署其他專案、正式 Release 已核准。
