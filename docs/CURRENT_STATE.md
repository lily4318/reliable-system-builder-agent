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

## 2026-11-13｜Agent 對話任務範圍辨識候選訓練（需 PR 審查）
TASK_DOMAIN: AGENT_SELF_IMPROVEMENT_TARGET_ISOLATION
SOURCE_REPO: lily4318/reliable-system-builder-agent
BASE_MAIN_SHA: c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57
CANDIDATE_BRANCH: agent-scope-training-20261113
SOURCE_ID/PATH: src/task_scope.py, evaluations/cases/task_scope.json, tests/test_task_scope.py, AGENTS.md, START_HERE.md, CI/quality gate
LAST_VERIFIED_STEP: CANDIDATE_PR_AND_CI_PENDING
COMPLETED: 新增結構化意圖守門、公開合成反例及品質門檻（通過前不得聲稱已完成訓練）
NEXT_ACTION: 審查候選 PR diff／同 SHA Actions verify；人工評閱標註與目標範圍後再決定是否合併
BLOCKERS: 真實自然語言意圖盲測與權重微調均未做；GitHub 平台 PR/Ruleset 狀態須另核
WRITE_OWNER: lily4318／此 Agent Repo 候選分支；外部專案不得由此任務修改
SYNC_STATUS: candidate_only; formal_release_approved=false; external_project_writes=none
