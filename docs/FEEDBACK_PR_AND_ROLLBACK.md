# 改善 PR、人工驗收與版本回退

## 改善 PR 最低內容
- 使用者最新需求、實際來源 commit、已驗證的真實故障「摘要」和去識別化案例 ID。
- 人類標註的 expected_action 與證據等級（原始證據留私有）。
- baseline / candidate 使用相同 label digest 的差異報告：accuracy、coverage、false completion、unsafe mutation、樣本量。
- 公開 `python -m unittest discover -s tests -v`、`python -m src.feedback_eval compare`（只對 synthetic fixture）、原有 policy/recovery/quality gate 結果。
- 在獨立受控環境下，由第二位人類評估者執行 sealed holdout，僅附去識別化且不洩漏 case 的摘要。資料保留外部。
- 負面成績、資料不足、未知事實要照實列明。CI 通過不是正式 Release。

## PR 與 main
- 固定 `lily4318/reliable-system-builder-agent` 最新 main；任何修改開新分支。
- GitHub Ruleset `27115344` 要求 PR、CI `verify` 成功、main 為最新、禁 force push 與刪除、討論解決；仍須在合併前再次回讀最新 Ruleset。
- 目前 `required_approving_review_count=0`，因此 PR 的**人工審查是治理契約，不是 GitHub 平台強制的第二人核准**。
- 使用者明確授權人工合併前，不能由 Agent 自動合併或建立正式 tag／release。後續如設為 1，先確認合格非作者 Write reviewer，避免 main 被鎖住。

## 品質退步回退
1. 停止發佈／合併；唯讀讀取最新 SHA、問題 PR、CI 與評測摘要。
2. 確認最後可信且具實際證據的 commit/release；對已合併變更建獨立 revert branch。
3. 執行 `git revert` 建立相反 commit，嚴禁 main force push、覆寫他人工作或刪除原錯誤證據。
4. 回退 PR 同樣經完整 CI、相同標註摘要比對、人工確認後才能合併。
5. 完成回讀並更新唯一 `release/current_release.yaml`、`docs/CURRENT_STATE.md`（只有實際合併才更新正式版本）。
6. 禁止本通用 Agent 的 rollback 引起外部 Study1 正式資料或 GAS 變更。
