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
