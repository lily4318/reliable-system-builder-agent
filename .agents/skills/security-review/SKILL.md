---
name: security-review
description: "檢查權限、隱私及安全。security 角色；交付 security-review。"
---
# security-review｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：architecture。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
核對資料分類、最小權限、威脅情境及故障邊界；以具體測試及修復建議交 Developer、SRE。僅要求必要的安全驗證；不把安全檢查擴成主要開發工作。

### GitHub 專案身分與授權（EP-09 / EP-10）
以正式 repo 及實際唯讀 API 證據核對資源身分，區分名稱表示、不可變資源 ID、來源版本與操作授權。對 GitHub 已驗 ASCII owner/repo 名稱做大小寫等價判斷，不因 case alias 繞過 Agent/外部專案隔離；未知 rename/transfer、URL、redirect 不自動當同一資源。維持原意圖與明確權限 gate，只有候選建議不等於寫入許可。實作及 red/green 證據見 [工程知識索引](../../../knowledge/ENGINEERING_PATTERNS.md) EP-09/10 與 NATIVE-EP-008 原決策；未測其他 provider，不宣稱普遍識別或 ACL 驗證。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 security-review；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。
