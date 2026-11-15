---
name: deployment
description: "部署、處理 CI 或版本。devops-sre 角色；交付 deployment-plan。"
---
# deployment｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：implementation、qa、security-review。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
先核對實際部署環境、權限與同 SHA 測試；準備備份、回退、版本、操作順序。人工設定附逐步 UI 欄位與檢查。未另獲授權只交部署計畫；不啟用真人收件、不盲重送。

### 四平台線上部署與驗收（TP-006 / NATIVE-CLOUD-016-STACK-SELECTION）
依 [多平台選型及實戰指南](../../../docs/CLOUD_ARCHITECTURE_SELECTION.md) C0–C6，先確認原資源身份、tool permissions、plan/remaining cost、source SHA/CI、backup/rollback；C3 單獨可編輯明示授權，禁止將 selection/advisory/需求確認視為外部部署授權。按 Pages artifact/URL、GAS scriptId/version/deploymentId/exec、Worker version/D1 schema、Supabase project/migration/front URL 取得實際讀回、遠端正負測、持久化與復原。未知/部分寫入先 READ_ONLY_RECONCILE；不盲送，不自動升級或正式啟用。無實際工具/授權時明確缺件與最少人工操作。

### TD-003｜完全新手的環境準備
讀 [新手引導](../../../docs/BEGINNER_ACCOUNT_ONBOARDING.md)。需求與必要平台先確認，按既有帳號/連接/真唯讀/權限/費用使用 src.account_onboarding 或同契約分流；只教目前必要的人工操作，附官方入口、預期與停點，使用者自行登入驗證與審閱同意。成功由真實可用工具回讀，失敗排除或安全替代；不讓新手自行研究、不重複註冊、不要求 CLI、不以連接授權部署。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 deployment-plan；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。
