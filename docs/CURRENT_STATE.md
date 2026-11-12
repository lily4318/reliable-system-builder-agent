# Agent 專案接續點

TASK_DOMAIN: RELIABLE_SYSTEM_BUILDER_AGENT_BOOTSTRAP
SOURCE_REPO: lily4318/reliable-system-builder-agent
WRITE_OWNER: lily4318
RELEASE_FILE: release/current_release.yaml
LAST_VERIFIED_STEP: GitHub main 寫入並實際 CI 後再依 commit 與結果更新
COMPLETED: 公開可攜式入口、7 專家角色、去識別化案例、安全評測及 CI 框架（須回讀）
NEXT_ACTION: 查最新 GitHub CI、修正失敗測試與 docs；人工核可後升正式 release，原專案整合需另行授權
BLOCKERS: 不具外部專案部署權限、獨立盲測或真正模型權重訓練
SYNC_STATUS: 初版 candidate；CI 和正式驗收獨立

## 本次增量候選（仍未正式 Release）
TASK_DOMAIN: RELIABLE_SYSTEM_BUILDER_INDEPENDENT_RECOVERY_ACCEPTANCE
SOURCE_REPO: lily4318/reliable-system-builder-agent
BASELINE_SOURCE_SHA: b1b5da9c2fecc24967854075aac492706a1ef06e
BASELINE_CI_RUN: 43203963325
RECOVERY_SOURCE: src/recovery_reconciler.py
RECOVERY_CASES: evaluations/acceptance/recovery_cases.json
QUALITY_GATE: src/quality_gate.py
RELEASE_REVIEW: docs/RELEASE_REVIEW_AND_ROLLBACK.md
LAST_VERIFIED_STEP: 以本輪最終 GitHub commit / Actions readback 證據為準；未通過不可宣稱完成
BLOCKERS: 人類正式核准及獨立盲測仍未完成；沒有外部專案執行權限
WRITE_OWNER: lily4318
SYNC_STATUS: Agent Repo main 單獨增量更新；外部 Study1 系統維持未操作

## 2026-11-12 GitHub 管理設定接續
TASK_DOMAIN: RELIABLE_SYSTEM_BUILDER_GITHUB_MAIN_GOVERNANCE
SOURCE_REPO: lily4318/reliable-system-builder-agent
OBSERVED_BEFORE_ADMIN_SETUP_SHA: 0c577a3e43237f4beda4db86e216c8a4a54881d9
CHECK_NAME: verify
BRANCH_PROTECTED: false（設定前實際 GET）
RULESETS: []（設定前實際 GET）
PR_REQUIRED: NOT_CONFIGURED
PR_REVIEW_REQUIRED: NOT_CONFIGURED
CI_REQUIRED: NOT_CONFIGURED
FORCE_PUSH_BLOCK: NOT_CONFIGURED
FORMAL_RELEASE_HUMAN_GATE: NOT_CONFIGURED
OWNER_ACTION: 依 docs/GITHUB_GOVERNANCE_SETUP.md 的 GitHub Settings 步驟配置
BLOCKERS: GitHub connector 無管理設定寫入權限；需合格第二審核者；Release environment/job 尚未設定
SYNC_STATUS: 只同步公開 Agent 管理設定操作指引；未設定的 GitHub 平台規則不得標為已生效

## 2026-11-12｜持續改善回饋系統（只提交 PR）
TASK_DOMAIN: RELIABLE_SYSTEM_BUILDER_REAL_FEEDBACK_LOOP
BASE_MAIN_SHA: c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57
WORK_BRANCH: feat/evidence-feedback-holdout-v01
SOURCE_OWNER: lily4318
WRITE_SCOPE: 只有 lily4318/reliable-system-builder-agent 的候選分支／PR
NEW_MODULE: src/feedback_eval.py
PRIVATE_EVIDENCE_POLICY: 真實標註與獨立封存 holdout 保留原專案權責環境，不提交至公開 Repo
RELEASE: v0.1.0 initial-candidate; formal_release_approved=false
LAST_VERIFIED_STEP: 以 PR CI / head SHA 實際回讀為準；未合併不得宣稱 main 已更新
BLOCKERS: 真實人類審核標註尚未收集；獨立外部保留測試尚未實施；第二位人類 PR 審核者尚未建立；正式 Release 人工門檻尚未完成
NEXT_ACTION: 檢查 PR CI 和程式案例；取得人工標註流程授權，封存資料後再進行真正的独立 holdout; 人工決定是否合併
SYNC_STATUS: PR_PENDING_MERGE; 外部 Study1 任何 Repo/GAS/Sheets 未操作

## 2026-11-12｜PR #1 成功率語意與標註契約修正（僅原分支）
TASK_DOMAIN: RELIABLE_AGENT_FEEDBACK_LABEL_CONTRACT
SOURCE_REPO: lily4318/reliable-system-builder-agent
PR1_BASE_HEAD_AT_START: 99a53db2e384c75545f10741a4f9fbaefd855707
WRITE_SCOPE: 僅 feat/evidence-feedback-holdout-v01 增量提交；不能合併、不能動 main 或 PR #2
PR2_HEAD_BASELINE: c60008679b7190133ef33f20fd75652cb7b64219
CHANGED_CONTRACT: 未知一律 verified=false；真實資料每筆必有 reviewer；已知真實結果必有 verified evidence digest；實際 success 要遠端或 UI 證據
METRIC_FIX: label_success_fraction_known ≠ Agent success；agent_verified_task_success_rate=null，需另有執行軌跡與人工回讀才能另算
NEXT_ACTION: 原 PR #1 更新後查 CI、回讀 SHA；PR #2 仍停留原 HEAD，需後續明確授權再同步相依
BLOCKERS: 真實任務資料與獨立保留測試尚未提供、真人正式審核未完成
SYNC_STATUS: PR_PENDING_MERGE, MAIN_UNCHANGED, PR2_UNCHANGED

## 2026-11-12｜PR #1 P0/P1 安全守門增量修正（僅候選分支）
TASK_DOMAIN: RELIABLE_AGENT_FEEDBACK_COMPLETION_GUARD
SOURCE_REPO: lily4318/reliable-system-builder-agent
SOURCE_HEAD_BEFORE_PATCH: 0968a45e30545e9efe4dd0ecb00096ec7ec27275
WRITE_SCOPE: 僅 feat/evidence-feedback-holdout-v01，不更新 PR #2 或 main
PR2_HEAD_BASELINE: c60008679b7190133ef33f20fd75652cb7b64219
P0: action=REPORT_VERIFIED_COMPLETE 或 claims_complete=true 任一為真即視為完成宣稱；不一致另計數並阻擋 candidate comparison
P1: 復原時間排除 NaN/Infinity/-Infinity、布林及超界數值；有效有限值維持合法
TEST_SCOPE: 正反邊界、完成動作與旗標矛盾、既有 22 policy/21 recovery、完整 CI
BLOCKERS: 尚無真實驗收資料與真人 Code Review；PR #2 需另行同步相依
SYNC_STATUS: PR_PENDING_MERGE，待最新 GitHub SHA 和 CI 實際回讀

## 2026-11-12｜E2E Execution Evidence 整合候選
TASK_DOMAIN: RELIABLE_AGENT_E2E_EVIDENCE
SOURCE_REPO: lily4318/reliable-system-builder-agent
BASE_MAIN_SHA: c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57
PR1_DEPENDENCY_HEAD: 34fe85c7960062b609d2efefc9d2a1d5072a3dcb
PR2_UNMODIFIED_HEAD: c60008679b7190133ef33f20fd75652cb7b64219
WRITE_BRANCH: feat/e2e-execution-evidence-evaluation-v01
WRITE_SCOPE: 新 Agent 候選分支／PR；不合併、不改 PR1/PR2/main、不得接觸 Study1
SOURCES: src/e2e_eval.py, schemas/e2e-execution-bundle.schema.json, evaluations/e2e/synthetic-*.json
COMPLETED: Agent 版本與任務快照、獨立驗收、部分寫入、失敗歸因、成本及合成 baseline/candidate 判定
BLOCKERS: PR #1/2 未合併、PR #2 相依衝突；真實資料授權／獨立封存／實際 Runner 和人工 Release 尚缺
NEXT_ACTION: 核對本輪 PR CI 和 GitHub blob SHA、完成正式程式審核；另行授權才處理 PR2 合併相依與私人實際評測
SYNC_STATUS: PR_PENDING_MERGE, MAIN_UNCHANGED, NO_REAL_DATA, NO_STUDY1_WRITE

## 2026-11-13｜PR #3 E2E 模擬執行與安全門檻整批增量
TASK_DOMAIN: RELIABLE_AGENT_E2E_SANDBOX_AND_EVIDENCE_HARDENING
SOURCE_REPO: lily4318/reliable-system-builder-agent
SOURCE_PR3_HEAD_AT_START: 2da73e85b990d1cb4b498999129bfb2b934ae024
DEPENDENCY_PR1_HEAD: 34fe85c7960062b609d2efefc9d2a1d5072a3dcb
PR2_UNMODIFIED_HEAD: c60008679b7190133ef33f20fd75652cb7b64219
WRITE_SCOPE: 僅 feat/e2e-execution-evidence-evaluation-v01；不合併，不動 main/PR1/PR2/Study1
COMPLETED: P0 矛盾 negative readback 不得轉成功、負面裁定需實際觀測；合成 deterministic sandbox runner、schema、fixture、正反測試與 CI
BLOCKERS: 真實 Agent Runner／正式資料權責核准／私人真實驗收／獨立封存盲測及真人 Review 尚未完成；PR2 相依衝突仍需另外處理
LAST_VERIFIED_STEP: 需依最終 commit/PR/CI 回讀填報，CI green 不等於真人成功
NEXT_ACTION: 獨立人工 code review，先處理 PR1 及 PR2 相依，再評估 PR3；外部資料與部署需獨立授權
SYNC_STATUS: PR_PENDING_MERGE，NO_STUDY1_WRITE，NO_REAL_DATA
