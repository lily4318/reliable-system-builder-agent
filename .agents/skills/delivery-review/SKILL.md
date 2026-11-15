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
