---
name: delivery-review
description: 依交付約定與獨立驗收證據判斷階段完成、阻塞或停止
---
# delivery-review｜階段交付與停止
主責 project-manager；前置 delivery-scope、delivery-progress；產物 delivery-review。核對 current scope、版本與真實成果、適用 Architect/QA/Security/DevOps 證據、使用者必要 UAT 及獨立授權。資料缺失不能以自述、測試數或 handoff 的 current 替代；適用 QA/安全驗收與原程式守門仍有效。此技能是協調判定，不是自動部署 gate 或發布批准。

- 必要驗收全過，且交付不需尚未取得的動作授權：READY_STOP，提供可使用成果、使用/維護方式、已知限制、驗收證據及後續改善清單；停止本階段，不啟動下一包。
- 已知核心缺陷、必要證據/權限缺失或未知結果：BLOCKED，說明缺項，按既有守門只做已授權且安全的針對性工作；日期到不構成豁免。
- 需重大範圍/日期/成本/授權抉擇：NEEDS_USER_DECISION，列可編輯選項與影響，不替人做決策。仍有必要工作且有有效進展及授權：CONTINUE_WITHIN_SCOPE。
候選試用、線上驗收、正式發布分別標記；真實部署按 C0–C6，C3 另明示准許，正式 release 按原清單及人審。對研究/教學交付，檢驗使用情境和資料/參數/輸出正確，不能用技術成功代替研究者科學/倫理確認。無獨立模型、未驗證新手操作如實揭露。保存真證據與下一個需授權動作至原紀錄。

### 研究資料交付的語意一致性（TD-005）
PM 核已確認 scope/字典與架構、實作、QA、匯出版本；各自 PASS 不代表同一契約。要求固定預期值的內容驗證與零筆資料仍可追溯的 manifest，未核准遷移/科學政策不得以交付期限放行。合成 lab 只為訓練，不當真人或正式交付驗收。見 docs/training/reviews/2026-11-16-research-handoff.md。

### 訓練停點不等於交付驗收（CAPABILITY-CONVERGENCE-005）
分開報必要技能 evidence-converged 建議、M2-2 等工作包真實完成、A07/B10/真人 UAT、C3/M3/M4。尚缺獨立證據即保持原 gate；不因已有 28 個測試方法支持 15 skills 或同 tree CI 全綠而代替真正使用、部署與人審。使用者未確認下一階段，不要求提前真人操作。詳 [原能力收斂覆盤](../../../docs/training/reviews/2026-11-16-research-handoff.md)。
