# GitHub main 與正式 Release 保護｜管理員設定與回讀清單

## 2026-11-12 實際核實基準

- 唯一 Repo：`lily4318/reliable-system-builder-agent`，Public，個人帳號 `lily4318` 具 Admin 權限。
- 當時 main：`0c577a3e43237f4beda4db86e216c8a4a54881d9`。
- GitHub `GET /repos/.../branches/main`：`protected=false`；required_status_checks = off。
- GitHub `GET /repos/.../rulesets`：`[]`。
- CI 實際成功 Run：`43207132079`，唯一 GitHub Actions check 名稱是 **`verify`**（不是 workflow 的整句名稱）。
- 現有 Releases：0；`release/current_release.yaml` 仍是 `0.1.0` candidate，`formal_release_approved=false`。
- `solactw-star` 目前有 `read`，**不能作為要求 Write 權限的 PR 核准者**。請不要自動提升其權限。
- 目前 GitHub 連接器**沒有 Admin Ruleset／Environment 寫入操作**；進階 branch-protection GET 回傳 403，故平台設定必須由 Repository 管理員在 GitHub 網頁執行，不能把本文件視為已啟用。

## A. 安全地啟用 main 分支 Ruleset

> GitHub Repository → **Settings → Rules → Rulesets → New ruleset → New branch ruleset**。
>
> 正式文件：https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository

請填：

| 欄位 | 建議 |
|---|---|
| Ruleset name | `main-pr-review-ci-no-force` |
| Enforcement status | **Active**（不是 Evaluate／Disabled） |
| Target branches | Include default branch（或明確 `main`） |
| Bypass list | **空白**（不要放管理員或 AI App 的例外） |
| Restrict deletions | 開啟 |
| Block force pushes | 開啟 |
| Require a pull request before merging | 開啟 |
| Required approving reviews | **1**（但務必先備妥至少一位非作者、具 Write 權限的可信 reviewer，詳見下方） |
| Dismiss stale approvals | 建議開啟 |
| Require conversation resolution | 開啟 |
| Require status checks to pass | 開啟 |
| Required check | **`verify`**，來源選 **GitHub Actions**（若能選） |
| Require branches to be up to date before merging | 建議開啟 |

**必要防死鎖步驟**：在要求 1 人審核前，先有一位可信且非 PR 作者的 Write 級審查者。GitHub 不允許作者自行核准自己的 PR；`solactw-star` 目前僅 Read，不會算入 PR 核准人數。若暫時沒有可審核者，請先只啟用 PR 必要、CI 必過、禁 force push／刪除等規則，但先將 Required approving reviews 設為 **0**；直到你正式邀請並確認一位合格 reviewer，再改為 1。**此過渡狀態不等於使用者要求的完整治理已通過**。

如果你不希望讓 `solactw-star` 擁有 Write，請選擇另一位可信 reviewer；本 Agent 不會自行變更協作者權限。

## B. 正式 Release 的人類核准（不同於 PR）

目前沒有正式 Release 發佈 workflow，單靠上述 Ruleset 不會自動阻止有人在 GitHub 網頁手動建立 Release。

建議另外建立一個 GitHub Actions **Environment**：

1. Repository → **Settings → Environments → New environment**，名稱 `formal-release-approval`。
2. 在環境保護規則中啟用 **Required reviewers**，選一位授權的人類審核者；Environment reviewer 只需要對 Repository 有 **Read** 權限，因此可由你另行選擇是否讓 `solactw-star` 承擔此角色。
3. 啟用 **Prevent self-review** 並停用「Allow administrators to bypass configured protection rules」（若 UI 提供）。
4. 要有真正的技術門檻，未來**正式發佈 job 必須明確引用 `environment: formal-release-approval`**；若尚無此 job，建立 Environment 本身不會限制 GitHub 網頁手動 Release。
5. 正式放行仍需 `release/REVIEW_CHECKLIST.md` 人工審核證據、核准者、採用的 main SHA、CI Run、品質基準和回退點；未核准不得把 `formal_release_approved` 設為 true，也不得建立正式 tag 或 Release。

**本次只有設定說明／核准流程，沒有建立 Environment 或正式 Release 發佈 job；不能宣稱 Release 平台門檻已技術生效。**

GitHub 官方 Environment 文件：
https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments

## C. 必須在 GitHub 重新回讀的驗收

設定並按 Create 後，至少核對：

- [ ] `GET /repos/lily4318/reliable-system-builder-agent/branches/main` 顯示 `protected=true`。
- [ ] `GET /repos/lily4318/reliable-system-builder-agent/rulesets` 至少一筆 **Active**，包含 main。
- [ ] 規則明確有 Pull request、至少 **1** 位核准者、Required status check `verify`、Block force pushes、Restrict deletions，沒有寬鬆 bypass。
- [ ] 用**測試 PR**實際確認：未經 reviewer 核准不能合併；CI `verify` 未完成／失敗不能合併；核准且 CI 成功才能合併。不要使用真實憑證、個資或 Study1 研究資料。
- [ ] 在受保護的測試工作流程上實際確認 Environment **Required reviewers** 與 Prevent self-review 生效；在正式發佈 job 未連接環境前，不得標示正式 Release 技術守門完成。
- [ ] `release/current_release.yaml` 維持 candidate，未經人類批准仍 `formal_release_approved=false`。

## 狀態定義

- `BRANCH_PR_REQUIRED_VERIFIED`：PR Rule 真實 Active、main 命中並有受阻／成功實測。
- `BRANCH_REVIEW_REQUIRED_VERIFIED`：至少 1 位非作者具資格 reviewer 的有效核准規則已測。
- `CI_REQUIRED_VERIFIED`：`verify` status check 必須通過才可合併。
- `NO_FORCE_PUSH_VERIFIED`：禁 force push 已 Active，並由規則查核。
- `FORMAL_RELEASE_HUMAN_GATE_VERIFIED`：Release job 與 Environment 連結，必須經另一個人類批准並已測。
- 未完成者只標 `BLOCKED`／`NOT_CONFIGURED`，不得把規格文件或一次 CI success 冒稱管理設定完成。
