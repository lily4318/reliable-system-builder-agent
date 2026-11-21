# 七角色工程協作｜證據導向交接契約（候選）

## 範圍
本文件訓練**公開 Agent 的工作決策流程**，不是要求它去建置之前提及的外部系統。所有案例是抽象化、無原專案個資的合成案例；不對任何外部 Repo、GAS、Sheet、郵件、部署服務發出請求。

## 從最新使用者任務到安全交付的責任鏈

| 角色 | 必須取得的證據 | 不可越過的守門 | 下一位接手者 |
|---|---|---|---|
| System Lead | 本輪明確目標、正式來源／SHA、授權範圍 | `HOLD_TARGET`／`HOLD_SOURCE`，不能拿歷史 main 當現況 | Architect |
| Architect | 需求目的、驗收條件、相依／資料流、相容與回退 | `HOLD_REQUIREMENTS`／`HOLD_ARCHITECTURE` | Security → Developer |
| Security | 資料分級、ACL、Secret、外部來源權責 | `HOLD_SECURITY`；不能以模擬權限代替遠端 ACL | Developer / System Lead |
| Developer | 同源受權 commit、原始碼、最小 patch 與 readback | `HOLD_PATCH_AUTHORIZATION`／`HOLD_IMPLEMENTATION` | QA |
| QA/UAT | 正反向結果、同 SHA CI Run、真實 UI 證據 | `HOLD_QA`、`HOLD_CI`、`HOLD_REAL_UAT` | Learning Evaluator |
| DevOps/SRE | 原 HTTP 方法與回應、HEAD／版本／部署 inventory | `READ_ONLY_RECONCILE` 優先於任何提交或部署建議 | System Lead / Security / QA |
| Learning Evaluator | 去識別化事故、對照組、品質基準、第三方審核 | 未經人工審核不能合併／發佈；不能把公開回歸當模型盲測 | Human Reviewer |

這份契約不是按順序自動跑七個 AI。特定任務可只用相關角色；**任何未知寫入**應由 DevOps/SRE 優先切入，停止盲目重新送出。需他人授權或驗證的動作不會因通過內部檢查而變成已執行。

## 結構化工程狀態判定器
`src/engineering_workflow.py` 只讀取已核實的標準化欄位，例如：
`target_confirmed, source_sha, current_head_sha, requirements_confirmed, acceptance_criteria, dependencies_mapped, rollback_reviewed, data_classified, acl_reviewed, candidate_patch_authorized, write_outcome, changed_files_readback, patch_commit_sha, positive_tests_passed, negative_tests_passed, ci_passed, ci_run_id, ci_head_sha, tested_sha, real_ui_uat_verified`。

它輸出 `decision`、`owner_role`、`next_safe_action`、`mutation_permitted=false`。只有資料的**來源真實且標註正確**時，這個結果才有工程意義。程式不解析自然語言、不驗證外部 SHA、不召喚子代理，不代表實際測試／部署。它對 `release` 最多輸出實際 UAT 或人工獨立核准的阻擋，永遠不輸出 deploy/POST。

## 正反測與品質防退步
```bash
python -m unittest discover -s tests -v
python -m src.engineering_workflow validate
python -m src.engineering_workflow evaluate --output output/engineering-handoff-report.json
python -m src.independent_acceptance evaluate
python -m src.quality_gate check
```

`evaluations/cases/engineering_handoffs.json` 為公開、人工制定預期結果、不是封存 holdout。每一筆明列 stage/權責/來源、expected decision 及 role，測試除判定是否與人工 expected 一致，也確保只產生安全下一步，所有輸出均不得直接寫入。

## 與尚未合併的前一份候選
Draft PR #4 專注「改善 Agent 本身 vs. 應用於外部專案」的第一道任務目標辨識；本候選專注「已核實目標後，七角色如何交接」。兩者**分支獨立且都以當下 main 為基底**。若人類之後決定採納兩者，需以最新 main rebase/合併衝突審查、重新跑所有同 SHA CI，不能從兩份各自綠燈推定整合版綠燈。

## 仍未具備的證據
- 真實 LLM 在自然語言需求蒐集與陌生系統的能力，未測。
- 七個子代理是否真的接手任務及成功交付，未執行。
- 真實跨服務部署、恢復與 UI UAT，未執行。
- 模型權重訓練、獨立盲測、人類 Release 核准，均未完成。
