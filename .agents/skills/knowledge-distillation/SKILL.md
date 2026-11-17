---
name: knowledge-distillation
description: "整理學到的事、蒸餾。learning-evaluator 角色；交付 knowledge-review。"
---
# knowledge-distillation｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：依任務所需。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
讀私有 lessons 和案例卡，按種類及 topic 分組；完全重複去重，不同內容視為待核衝突。提出合併／取代建議，讓使用者修改確認後才新增取代事件；原歷史保留。僅已驗證可泛化結果才建知識卡，安全與正式來源永遠優先。

### 公開工程知識整併（TD-001 / TD-002）
在 REPO_NATIVE 或有授權的公開候選工作中，先讀原 [工程知識索引](../../../knowledge/ENGINEERING_PATTERNS.md)、訓練主檔、決策及 CASES/TRAINING_CASES；查原始驗收證據與精確 SHA，而非重新跑已驗收工作。以共同工程原理合併導航，保留原 case key、失敗、例外、來源與適用限制；每卡有任務/風險詞、catalog skills、實測證據、限制與獨立審查狀態。區分 EVIDENCE_VERIFIED、INDEX_CANDIDATE 與既有 DEFAULT/OPT_IN 檢索案例；不將索引候選編入 runtime seed 或私人記憶，不自動升格。以最小原檔增量、CAS、讀回與獨立文件 CI 記錄覆盤。沒有可用私人工作區只做 SOURCE_READ，不製造私人 citation；人審與原 learning-policy 保留。

### TD-004｜外部教材深度學習與專家分派
依根 AGENTS.md TD-004 建立唯一章節覆蓋矩陣，來源/版本、前置、單一主責、必要協作者、skill、狀態與 L0–L6 證據逐欄可追溯。先匹配既有知識，按依賴及缺口分派；主責深入閱讀、原理反思、蒸餾、實作、修復、遷移與交接，Evaluator 檢驗而非代學。教材不可讀就記 BLOCKED_SOURCE，無目錄不能報完成比例；過時與不採用保留理由。避免公開轉載或未審查執行，保留原審核流程。

驗證入口：`python -m src.curriculum_coverage`，唯一資料 [curriculum-coverage.json](../../../docs/training/curriculum-coverage.json)。工具只驗 declared inventory、owner/catalog、依賴與成熟度引用結構；BLOCKED_SOURCE 空表不是 0% 或 100%，不認證外部清單、證據或完成。取得已授權完整目錄後才宣告 COMPLETE_DECLARED，保留原來源完整性覆核，review_candidates 只是候選非開工許可；來源未取得不冒稱已學。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 knowledge-review；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。

### 必要角色及研究交接蒸餾（TD-005）
按 catalog 逐技能保留原實證、適用範圍、真缺口及下一步；不要用角色文件、測試數或重疊負例當成熟度。EP-01/04/11 的語意版本、失效與獨立解析路徑可遷移至研究字典交接；保存自寫對照及實際執行記錄，非獨立盲測、L6 或私人記憶。見 docs/training/reviews/2026-11-16-research-handoff.md。

### 既有技能的證據覆核（CAPABILITY-CONVERGENCE-005）
沿原 catalog 與已存在的覆盤增量對照各 skill 的真實測試方法、raw log、精確 run/checkout/tree、適用限制與是否為 same source。共享方法只計一次；15/15 skill 有 evidence entry 不等同獨立評測或 L6，review lab 不在 CI discover 範圍時保留各自執行紀錄、確認 blob，不自動重跑。缺口若不阻礙原 MUST 或屬未來獨立授權/真人驗收，明示延後而非製造合成訓練。詳 [15 項原始日誌對照](../../../docs/training/reviews/2026-11-16-research-handoff.md)。


### TP-010｜有效記憶精簡與遷移
原 distill/resolve 處理同 topic 去重與衝突，candidate 不取代 user-stated，不用新日期覆蓋安全。主檔頂部維持有效規則與接續，歷史保留。用原案例及不同真任務的可比實際結果查採用/拒絕，未驗不升格。
