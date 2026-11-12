# v0.1.0 候選版｜人工正式核准紀錄（待簽核）

目前未核准，**此檔案不是核准證明**。不可從勾選題目或 CI 成功推定人類已完成審查。

- [ ] 審查者與作者不是同一人，審查者已取得必要專案背景及候選 main SHA。
- [ ] `START_HERE.md`、`AGENTS.md`、專家、Skills 與外部權限界線一致。
- [ ] 案例庫已去識別化，不含秘密、真人資料或私有完整日誌。
- [ ] 已人工檢閱故障案例的期望判斷，不以同一個函式計算 expected 和 actual。
- [ ] CI 單元測試、公開政策回歸、隔離恢復驗收與品質基準全部通過。
- [ ] 測試程式沒有 API 寫入，未私自修改任何其他 Repo、GAS、Sheet。
- [ ] 有正式回退參考 SHA，已檢查 PR 與版本回退作業流程。
- [ ] 已確認跨帳號公開讀取可用，但寫入需要另行授權。
- [ ] 人類審查者明確決定是否核准 release、tag 與版本。

**審核者：未指定**  
**核准日期：未核准**  
**正式 Release Tag：無**  
**正式驗收狀態：RELEASE_APPROVAL_PENDING**

若核准，須另由 Release Manager 依實際證據更新版本、建立 Git tag／Release 並回讀。

## 正式 Release 額外平台守門（待完成）
- [ ] main 的 Active branch ruleset 已回讀；至少一位**非作者且具 Write 權限**的 PR 審核者可有效批准。
- [ ] 必要 CI check `verify` 和禁止 force push／刪除的 Ruleset 實際回讀通過。
- [ ] `formal-release-approval` Environment 的 Required reviewers／Prevent self-review 已配置並經實際工作驗證。
- [ ] 正式發布 Workflow 的 job 明確引用該 Environment；未建立工作流程或仍可繞過時不得稱技術強制核准。
- [ ] 人類正式核准者、候選 SHA、CI Run、版本回退依據、實際 Release Tag 已完成回讀。

設定和查核方式：`docs/GITHUB_GOVERNANCE_SETUP.md`。本檔清單本身不是 GitHub Ruleset 或核准已生效的證據。

## 持續改善 Agent 的實際資料／品質驗收（待人工）
- [ ] 本 PR 的 GitHub `verify` 實際通過、PR head SHA 與 main base 均已回讀。
- [ ] 合成 smoke 成績僅當工具測試，不宣稱真實模型改善或真實部署成功。
- [ ] 真實任務 labels 由授權人類從原始證據獨立標註，無任何未授權資料外洩。
- [ ] 非公開 holdout 由不同的人類審查者封存，凍結標準與候選 SHA，開發／holdout group 無交叉。
- [ ] 同一 label SHA 下 baseline/candidate accuracy、coverage 不下降，0 false completion 與 0 unauthorized mutation。
- [ ] PR 人工審核與正式 release 核准獨立，確認未曾由 CI 或 Agent 自行標記 `formal_release_approved=true`。
- [ ] 版本回退參考、可重現的 revert PR、下一次真實任務復發率追蹤已檢查。

## PR #1 指標與 unknown 契約核對（候選）
- [ ] `verified_task_success_rate` 已移除避免誤用；標註成功比例與 Agent 版本的端到端成功率分開。
- [ ] `agent_verified_task_success_rate` 在缺少版本綁定的真實執行證據前為 `null`，不能由 synthetic 或 golden labels 推估。
- [ ] 真實 unknown 允許經人類審閱但 `verified=false`；不准產生「已核實完成」動作。
- [ ] 真實已知 success/failure 必須有 reviewer、`verified=true`、證據 SHA；成功還要實際遠端／UI。
- [ ] PR #2 為 stacked PR；若 PR #1 HEAD 更新，PR #2 的 commit 與基準不能被本輪暗中同步或改寫。

## E2E 候選驗收
- [ ] TaskSpec、環境快照與 Agent/Runner/Policy/Tools/Prompt 全部固定 SHA。
- [ ] 遺漏執行仍納入分母，不讓只讀或人工安全停止假冒完成。
- [ ] UI／遠端須同目標的獨立合格證據，不能靠 CI 過關。
- [ ] 未對帳、重複非冪等 POST、未授權操作、誤稱完成皆須阻擋。
- [ ] 公開合成 CI 不被冒稱真實成功；正式 release 核准仍為 false。

## 同批次 E2E 實際工具沙盒驗收（僅合成）
- [ ] `GET_READBACK: NOT_APPLIED` 不會被矛盾的 positive receipt 覆寫成 VERIFIED_SUCCESS。
- [ ] VERIFIED_FAILURE 須另有相同 target 的實際觀測，無觀測仍為 UNKNOWN。
- [ ] `src/e2e_sandbox.py` 僅在隔離合成狀態機執行，不存取外部資料、網路或真人帳號。
- [ ] 合成沙盒能實際演練逾時後安全對帳、部分寫入、非冪等重複操作、UI/CI/Email 與固定任務分母。
- [ ] 所有新的 Schema、評測器與沙盒正反測試和 CI 通過；實際來源 SHA 回讀。
- [ ] 合成成功率與正式 Agent 的真實端到端完成率完全分開，不可由 PR / CI 自行核准。
