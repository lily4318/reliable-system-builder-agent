---
name: implement-feature
description: "完成某功能、實作網站。developer 角色；交付 implementation。"
---
# implement-feature｜工作技能

## 開工
讀根 AGENTS.md、適用角色指令與正式專案來源。使用私人工作區的 `context` 取得既有產物及有效經驗，不把工作區當成正式來源或額外授權。前置產物：specification、architecture、plan。缺件時先完成必要前置或說明阻塞；不假造產物。

## 執行
先核對已授權候選工作區與規格確認；只做最小可運作垂直切片。讀現有程式及案例知識，寫實際程式與正反測，執行它們、讀完整錯誤、修復後重測。產物記錄檔案、commit、測試命令和結果；不把空函式或計畫當交付。

### 完整縱向網站訓練交付（NATIVE-WEB-014-EDITORIAL）
確認具版本需求與獨立候選寫入範圍後，優先完成同一網站從公開頁、私有工作台、資料/交易/API 到真實操作的閉環，不以孤立函式或 schema 檢查替代整體交付。按需求分離 public pointer 與 private draft、版本綁定核准及 mutation receipt；未知回應先原 actor 唯讀對帳。以階段 exact SHA/CI 及逐項需求驗收轉交；本機運行、正式部署及真人 UAT 分開。WEB-EDITORIAL-01 的 434/434 與兩種 viewport 各29實測見原訓練主檔，不泛化為任意網站成功或模型分數。

### 動態研究資料驗證與版本化交換（TD-005 Developer/QA）
依研究者核准的資料字典、欄位型別/值域、missing 與更新語意，將可接受輸入、唯一鍵、版本及 revision 守門、資料和事件更新置於同一交易。不得把 bool 當整數、缺失值補 0、靜默改研究資料或以逐列提交冒稱原子批次。匯出須明確消費者/格式、同一讀取快照、固定欄位排序與版本、可重現 bytes，必要分離機器交換與試算表閱讀格式；保留原文字及可逆契約。合成 lab 見 docs/training/reviews/2026-11-16-research-data.md；未證真試算表、正式資料字典及雲端。不要將固定合成規格套到真研究。

## 交付與接續
保存實際工作成果到已授權私人工作區並以 `handoff` 登錄 implementation；產物應包含需求來源、實際完成、驗證結果、未決與下一步。透過 `context` 回讀產物，下一技能讀內容而非只讀完成旗標。只有真實驗證才可稱完成；角色未被實際啟動時標記單 Agent 協作。外部寫入、正式部署與發布另需授權。
