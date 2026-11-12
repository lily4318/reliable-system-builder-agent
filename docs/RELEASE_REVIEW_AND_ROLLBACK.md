# 版本核准、人工審查與安全回退

## 唯一來源與當前狀態
- 主專案：`lily4318/reliable-system-builder-agent`；正式入口 `release/current_release.yaml`。
- **v0.1.0 尚為 Candidate**；沒有正式 tag，`formal_release_approved=false`。
- 初版已核對的歷史 baseline：commit `b1b5da9c2fecc24967854075aac492706a1ef06e`、CI Run `43203963325`。這個 commit 是「舊測試可通過」的回退參考，不代表新的恢復功能也已包含其中。

## PR／人工核准流程
1. 從最新 `main` 建分支，提出最小變更 PR，附最新來源 SHA、需求依據、去識別化案例、差異與復原策略。
2. PR 必須通過 `agent-ci.yml`：全部單元測試、既有政策回歸、獨立恢復驗收、品質基準與隱私掃描。
3. **非作者的人類審核者**檢查公開資料去識別化、是否更動正式 Agent 行為、來源競寫、測試合理性與危險能力。
4. 使用 GitHub Repository Settings → Rules / Branch protection（名稱依 GitHub 介面版本），由帳號 Owner **另外手動設定** `main` 必須 PR、至少一位審核、必要狀態檢查成功、拒絕 force push／刪除。此 GitHub UI 設定**未在本次建立或驗證**，故不能宣稱已強制生效。
5. 只有 Owner 或指定 release manager 能依審核記錄升版 `release/current_release.yaml`、CHANGELOG 與 GitHub tag/release。CI、Agent 自評或排程不得自動標 `formal_release_approved=true`。
6. 核准時須再次回讀新 main SHA、檔案、CI run 和 tag，記錄人工核准者及版本；沒有實際證據標 `RELEASE_APPROVAL_PENDING`。

## 回退（只作用於本公開 Agent）
**不要直接 force push main 或刪除原 commit。**

1. 停止新的 release／整合，鎖定最新 main 與異常的 commit SHA，查最新 Actions、案例與操作紀錄。
2. 確認最近一個可信、具有真實 CI 證據的 baseline／release；初版參考 `b1b5da9c...`。
3. 建立修復分支，使用 `git revert <壞掉的 commit SHA>`（按實際有問題的多筆 commit 倒序操作），**不要**對共用 main 做 `git reset --hard`／force push。
4. 對 revert PR 完整執行 CI、獨立恢復驗收、人工評審，確認沒有把好的安全修正一起移除。
5. 核准合併後回讀新 SHA，對比舊版 benchmark 和事件紀錄，更新 release 入口與回退記錄。
6. 若事件涉及其他專案（例如研究招募網站），**絕不從這個通用 Agent 的回退推導可修改其他專案**；外部系統另需正式授權和獨立部署／UI 安全驗證。

## 異常事件
若 API／CI 剛好失敗或遠端結果不明，狀態是 `BLOCKED`，不是 `SAFE_TO_DEPLOY`。請先按照 `docs/INCIDENT_RECOVERY.md` 唯讀對帳。
