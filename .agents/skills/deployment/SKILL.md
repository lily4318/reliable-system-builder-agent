---
name: deployment
description: "部署、處理 CI 或版本。devops-sre 角色；交付 deployment-plan。"
---
# deployment｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：implementation、qa、security-review。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
先核對實際部署環境、權限與同 SHA 測試；準備備份、回退、版本、操作順序。人工設定附逐步 UI 欄位與檢查。未另獲授權只交部署計畫；不啟用真人收件、不盲重送。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 deployment-plan；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。
