---
name: requirements-spec
description: "整理規格、修改需求。architect 角色；交付 specification。"
---
# requirements-spec｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：requirements。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
讀需求及實際使用者決策；將接受、修改、拒絕真正反映在功能矩陣、資料、權限、介面、非功能及驗收。標識衝突、差異及未決，附可編輯逐項確認。未確認不作為施工基準。

### 跨規格欄位的需求一致性（NATIVE-REQ-004）
- 先分出「使用者原始明示需求（含否定／未決）」、「整理後的規格表示」、「推導提案」及「已核准決策」。同一需求使用穩定 ID、來源鍵與實際版本，不能用欄位數量或相似文字充當追溯。
- 若規格 schema 定義某欄位是原回答的直接副本，須逐值核對原答及未決狀態；功能、非功能、架構引用、施工優先序不能暗中反轉否定或填補未決。若是合理摘要或設計推導，不要求逐字複製，但須保留原答、標示推導及適用限制，請人審查語意。
- 規格草稿內每個審閱項應對應一個確切且唯一的提案，接受／修改的預填文字必須對應該提案，不以陣列順序、碰巧相同的數量或舊確認當來源。進入下一階段前驗證缺失、重複、錯配、未決與否定的正反例。真正變更需求時，保留舊版並重新核對受影響的設計與驗收，不自行核准。
- 本 repo 既有 13 題 schema 的可重現檢查：`python -m src.website_scenario_eval evaluate`，配合 `python -m unittest discover -s tests -p test_website_scenario_eval.py -v`。此契約驗證不能證明任意自然語言或整體架構合理；適用來源見原決策紀錄 NATIVE-REQ-004，勿把公開 fixture 當真人需求或能力分數。

### 網站審閱結果的實際交接（NATIVE-MATURITY-012-REVIEW-HANDOFF）
原本機 export `local_reviewed_website_draft` 用 `src.website_review_handoff.prepare`（或 `python -m src.website_review_handoff --review <私人 JSON 路徑>`；可另帶先前可信 `--expected-sha256`）。對話/REPO_NATIVE 沒有 CLI 時按同等契約核對原回答、原草稿、完整確認決策，明示實際工具使用與未執行檢查。不得把被拒絕提案並入施工功能、不得遺失修改文字。完整13原答、拒絕/修改/未決與 source digest 分離；先解決語意衝突、具體驗收、範圍及真人整份規格確認，再以同版完整 specification 交 architecture-design。設計審閱 packet status/sha 或本機確認絕非正式核准/寫入權。只在已授權適當私人位置保存原需求及產物，不將 stdout/私人內容傳公開 repo。原 [操作指南](../../../docs/WEBSITE_INTAKE_UI.md)，[CI 43705735689](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43705735689) 424 tests、6 actual DOM。無真人/跨平台/全站驗收證據。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 specification；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。

### 研究字典的語意版本與交接（TD-005）
需求 ID、欄位名、revision label 相同仍不代表單位、值域、缺失、精度或衍生語意相同；從研究者已核准版本核對完整資料字典與資料來源版本。上游變更由原 revision/依賴守門重驗受影響設計、開發與 QA。保留舊原始資料，不默默重解讀、轉換或補值；實際遷移需明確政策和獨立驗收。參見 docs/training/reviews/2026-11-16-research-handoff.md；合成 lab 不證真研究科學效度。
