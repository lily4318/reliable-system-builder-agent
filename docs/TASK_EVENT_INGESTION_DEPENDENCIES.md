# PR #2 的來源／相依與接續

TASK_DOMAIN: RELIABLE_AGENT_TASK_EVENT_PIPELINE
SOURCE_REPO: lily4318/reliable-system-builder-agent
MAIN_VERIFIED_BEFORE_WORK: c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57
PR1_BASE: main
PR1_HEAD: 99a53db2e384c75545f10741a4f9fbaefd855707
PR1_URL: https://github.com/lily4318/reliable-system-builder-agent/pull/1
PR2_HEAD_BRANCH: feat/offline-task-event-ingestion-v01
PR2_BASE_BRANCH: feat/evidence-feedback-holdout-v01
WRITE_OWNER: lily4318
AUTHORIZED_SCOPE: 此公開 Agent Repository 新分支及 PR；不得修改 main、其他 Repository 或 Study1。
SOURCE_OF_TRUTH: docs/TASK_EVENT_INGESTION.md + 原 PR #1 的 src/feedback_eval.py + 人類正式核准
REVIEW_CRITERIA: source SHA、人工授權、離線只讀來源、完全丟棄自由文字、待審佇列、證據 SHA、不產出真人成功判定。
NEXT_ACTION: 審閱 PR #2 的差異、全部 CI、相依的 PR #1；PR #1 合併後才能確認 PR #2 是否安全改指 main。
BLOCKERS: PR #1 未合併、真實私有資料未授權取得／未提供、真實人工標註工作台與外部證據稽核尚未實作。
SYNC_STATUS: PR_PENDING_MERGE（本檔只存在候選 PR，尚非 main 正式來源）。
