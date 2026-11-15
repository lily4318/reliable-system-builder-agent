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

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 knowledge-review；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。
