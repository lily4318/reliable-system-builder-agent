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

## 2026-11-13｜真正 LLM 需求理解與架構規劃評測候選（獨立 PR）
TASK_DOMAIN: RELIABLE_AGENT_REAL_LLM_REQUIREMENTS_EVALUATION
SOURCE_REPO: lily4318/reliable-system-builder-agent
BASE_MAIN_SHA: c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57
CANDIDATE_BRANCH: candidate-llm-requirements-evaluation-20261113
PR4_AND_PR5: open Draft, unmerged, independent (must re-evaluate integration SHA if merged)
SOURCE_PATHS: src/llm_requirements_eval.py, evaluations/llm/public_dev_cases.json, tests/test_llm_requirements_eval.py, docs/LLM_REQUIREMENTS_EVAL.md, original Actions verify and quality gate
COMPLETED: External actual-model subprocess evaluation protocol, synthetic public developer examples, independent sealed holdout format, label/reviewer contract, unit/CI checks proposed
LAST_VERIFIED_STEP: NEW_CANDIDATE_PR_CI_PENDING
NEXT_ACTION: Commit candidate, inspect complete diff, same SHA GitHub Actions; test real LLM only after independent holdout/reviewer and explicit runner become available
BLOCKERS: no configured/approved real-model runner; no external human-labelled sealed holdout; no true measured natural-language accuracy or architecture semantic human grading
WRITE_OWNER: Agent candidate branch only; no external projects; formal_release_approved=false
SYNC_STATUS: candidate_only; no auto-merge, no public model invocation, no real data
ADDITIONAL_CANDIDATE_ARTIFACTS: src/llm_architecture_review.py; tests/test_llm_architecture_review.py; optional private architecture packet outside repo; no actual review scores.
ARCHITECTURE_SEMANTIC_STATUS: review_contract_implemented; no_real_model_output_or_independent_human_review


LLM_REQUIREMENTS_INTEGRATED_CI_20261113:
- TASK_DOMAIN: RELIABLE_AGENT_REAL_LLM_REQUIREMENTS_EVALUATION
- SOURCE_OWNER: lily4318/reliable-system-builder-agent, candidate-llm-requirements-evaluation-20261113, Draft PR #6
- PRE_MAIN_SHA: c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57 (main has not been modified)
- VERIFIED_CODE_SHA: 92344087285f0595d07f1b6ad7fac3c18e568cba
- VERIFIED_CI: GitHub Actions Run #43453202512 / verify Job #131980515373, completed/success on exact VERIFIED_CODE_SHA.
- TEST_CI: 49 unittest PASS; 22/22 deterministic public policy PASS (18/18 critical); 21/21 independent recovery PASS (20/20 critical, unsafe=0); 20 public synthetic LLM dev scenario protocol valid; public privacy heuristic and candidate quality_gate PASS.
- PREVIOUS_FAILURE: Run #43453003170 on c4b7080830fc13545aafa568ae3eb56b2ec0c2ba had 36 tests / errors=8 because new architecture_outline was incorrectly made mandatory in gold labels. Fixed by separate GOLD_FIELDS from REQUIRED_FIELDS (no fabricated gold label), reran full same SHA CI above.
- LAST_VERIFIED_STEP: CANDIDATE_CODE_TESTS_VERIFIED_ON_9234408; this progress append will create a docs-only SHA needing its own same SHA CI readback.
- COMPLETED: human-provisional 20 public synthetic dev cases; protocol for real LLM subprocess runner; strict separation of gold from messages; private model-pseudonymous architecture outline packet; two-independent-reviewer structure and 0/1/2 rubric; sealed holdout SHA/attestation check and nonpublic paths; positive/negative tests, timeout/invalid-response/unsafe-scope safety gates.
- UNVERIFIED: genuine model runner NOT configured/invoked; actual LLM classification or architecture quality NOT measured; two human annotators NOT assigned and independent holdout NOT created/sealed; external reviewer attestation NOT independently authenticated. Test-doubles and public labels are not model-performance proof.
- BLOCKERS: authorized private execution environment/model, independent adjudicated labels and sealed unseen dataset, real model provenance/params, independent human semantic architecture scoring.
- WRITE_OWNER: candidate PR only; no other repo, no deployment, no signed communications, no formal Release/tag.
- NEXT_ACTION: independent PR/security review; provision a permitted real LLM runner and independently sealed holdout before reporting model accuracy; PR #4/#5 remain separate Draft and unmerged; on any future integration rerun all tests on merged code SHA.
- SYNC_STATUS: draft_candidate; main_unchanged; formal_release_approved=false; human_review_required=true; external_project_writes=none


## 2026-11-13｜LLM runner 授權與輸出來源唯讀預檢（仍為 Draft PR #6）
TASK_DOMAIN: RELIABLE_AGENT_LLM_RUNNER_PROVENANCE_AUDIT
SOURCE_OWNER: lily4318/reliable-system-builder-agent
SOURCE_MAIN_SHA: c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57
CANDIDATE_PR6_BASE_SHA: 0134bfb6a52a6385d96b5c164b37e7e81ecb992b
READ_ONLY_FINDINGS: PR6 候選樹僅有評測器與公開 mock 測試，無具可驗證實際模型身份、來源與授權的真實 runner、供應商 request 回應證據或私人評測核准。原 PR6 同 SHA CI Run #43453558517 49 unittest PASS，但只執行離線／mock，與模型評測不得混用。PR6 reviews/comments 仍無批准的模型證據。GitHub Actions variables 權限端點未開放，亦不能據此認定私人帳號絕對沒有設定。
CANDIDATE_CHANGE: 新增 src/llm_runner_preflight.py 及專用否決負測，唯讀確認外部 runner 腳本位元組 SHA、Prompt 與 evaluator SHA，以及公開開發集範圍聲明；即使核對全部相符仍維持 MODEL_PROVIDER_UNVERIFIED、APPROVAL_UNVERIFIED、NO_LIVE_AUTHORIZATION。不把假 runner 的正確輸出自述成真正模型成績，並加入只讀 CI 診斷步驟。
STATUS: RUNNER_MODEL_VERSION_PROVIDER_VERIFIED=false; APPROVAL_INDEPENDENTLY_VERIFIED=false; PROVIDER_RESPONSE_ORIGIN_VERIFIED=false; ACTUAL_LLM_EVALUATED=false
LAST_VERIFIED_STEP: NEW_PREFLIGHT_CANDIDATE_CI_PENDING
BLOCKERS: 尚無受控、可驗證、可授權 runner 環境；實際供應商型號／版本與呼叫回執；人工權限／用量授權；獨立封存 holdout 與雙人標註。
WRITE_OWNER: Agent PR6 候選分支 only，未修改 main、其他專案、遠端服務、正式 Release。
NEXT_ACTION: 回讀此候選的 GitHub 實際 CI 與新 SHA；待真正模型供應商及執行權限取得後，才可安排公共合成案例的受控真實試跑。
