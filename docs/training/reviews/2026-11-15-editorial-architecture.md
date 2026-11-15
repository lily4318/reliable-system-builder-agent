# NATIVE-WEB-014-EDITORIAL｜WEB-EDITORIAL-01/v0.1  architecture / plan
使用者本輪明示：「我確認 WEB-EDITORIAL-01/v0.1 完整規格 R01–R13 及驗收 A01–A07，並另行授權在原 reliable-system-builder-agent PR #8 候選分支內實作此合成網站。請完成架構設計、工作拆分、前後端、資料庫及實際驗收，持續更新原訓練主檔。不授權正式發布、外部部署或跨專案修改。」狀態 CONFIRMED（規格與獨立候選寫入兩項）；原 v0.1 內容 blob 121e93d77799905c73043bbfe7971d77bd3f56dd @ 45b3e32f09107934a8aa6c94e0072446b5d89db9，無需求變更，保留歷史。非本機確認或模型產生旗標。
基準 45b3e32f09107934a8aa6c94e0072446b5d89db9 / CI 43706231648 job 132787799571：424/424，43.929s，6/6 DOM handoff。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，原 repo 題材合成、可信程式，無 private workbench、無獨立子代理、無付費服務。先讀原主檔、TD-001/002、spec、catalog、按需 role/skill、EP-02/03/06 與 src/p22_document_review.py、src/p21_equipment_site.py。EP-02 版本核准、EP-03 原子 receipt/唯讀復原、EP-06 HTTP/實際 DOM/真人驗收分層；非照搬 actor-label 模型。

## ADR-01
採 Python 3.12 stdlib HTTP + sqlite3 + vanilla HTML/CSS/JS，無新依賴、CI 已有 Chromium；受控 localhost。Flask 可減少路由/模板樣板但需依賴和版本管理；Django 提供 auth/ORM/後台但本次成本較高、仍需自定 workflow/ACL。正式公開服務須重新選擇維護/安全方案、HTTPS、Secure cookie、服務治理、容量/load 等；不以 stdlib demo 自稱 production stack。
## Components / interfaces
- src/editorial_store.py：SQLite mode=ro/rw、exclusive init、FK/schema version，accounts/session hash/expiry，articles/public pointer/version，revisions/state/immutable published content，actor-token receipt + audit 同 transaction；backup/restore 到全新路徑，restore 清 session，不覆蓋舊庫。
- src/editorial_site.py：127.0.0.1、host/origin/token 守門，JSON body cap、auth cookie/CSRF、POST login/logout/action；GET public list/detail、session/workspace/history、receipt。HTTP actor 由受驗 session 取得，不接受 client role/actor。回應 no-store/CSP；拒絕與未確認回應不自動重送。登入預先由 bootstrap nonce cookie+CSRF, login rotate; session 30min absolute。
- examples/editorial-site/：公開文章/搜尋/分頁、登入、作者草稿與歷史、編輯審稿與發布下架；純文字 DOM、錯誤/空狀態、鍵盤及 responsive。public query 僅走 pointer + PUBLISHED 同 article；private query owner/editor allowed status，遮蔽 DRAFT，audit 依 actor/revision 邊界。
- action contract：token random hex, operation, article/revision IDs, expected article version, content or reason only when needed. BEGIN IMMEDIATE revalidate session/ACL/state/version; canonical payload digest; same actor/token/payload return original effective result before state check; different payload reject; legitimate stale/state denied receipts persisted, no business mutation. On fault transaction rollback; GET own receipt only. Unknown client result freezes further action until read-only reconcile. Draft/returned edit→DRAFT, submitted immutable, approval separate from publish, clone of published/withdrawn latest only with no open draft, withdrawal affects pointer not open draft. Author/edit body mutation preserves published and historical terminal versions. audit captures state transitions and revision number, not raw secrets.
- UI/HTTP, unit/integration/actual browser CI separated. Input exact types/allowed keys/fixed enum, text 120/10000/500, 64KiB or bounded larger JSON to fit UTF-8 (128KiB), search bound, pagination 20, SQL params. Local synthetic trusted DB/filesystem only; no arbitrary schema/production DoS claim.

## Work packages DAG / acceptance (planned)
| WP | owner/skill | depends | R/A | file and acceptance |
|---|---|---|---|---|
| W0 | System Lead / requirements-spec | user confirmation | all | exact spec + scope evidence; done via this commit |
| W1 | Architect / architecture-design, System Lead/task-planning | W0 | all | this ADR, data boundaries and DAG | 
| W2 | Developer / implement-feature | W1 | R02/03/05–10, A02–05 | src/editorial_store.py, tests/test_editorial_store.py: transaction, authentication, version and pointer |
| W3 | Developer / implement-feature | W2 | R01–12 A01–03/06 | src/editorial_site.py, examples/editorial-site, tests/test_editorial_site.py: actual HTTP and UI |
| W4 | QA/UAT / test-and-acceptance, Security / security-review | W2/W3 | A01–06 | browser runner and explicit negative matrix, full CI |
| W5 | SRE / deployment | W4 | A05/07 | local startup/backup/restore/rollback, exact CI/remote readback; no deployment |
| W6 | Learning Evaluator / learn-from-feedback, knowledge-distillation; System Lead/resume-project | W4/W5 | A07 | original training master/decision, evidence+limitations, later fresh conversation resume |

Status W0/W1 document implementation; W2–W6 planned, not PASS. Prior CI is not website evidence. Use exact source and scoped writes, no formal release.


## 實作與驗收補記（W2–W6）
依原確認未改產品需求。最終 code/test ca030a15af00d3dd4459a3c9829636385c37378b / CI 43708288874 job 132794093170 success 434/434，45.381s，實際 Chromium 2x29。原架構草稿保留；schema 2 加每修訂 counter 及 audit 退回理由；UI 按已核准規格處理 lost ACK、同分頁原 actor 重新登入恢復 receipt；非跨設備保障。詳 [原主檔](../AGENT_CAPABILITY_TRAINING.md) NATIVE-WEB-014-EDITORIAL 完整工程驗收及 [本機操作指南](../../EDITORIAL_SITE.md)。W0–W5 實作及受控驗收完成；W6 已完成覆盤、原文檔與證據同步，A07 獨立新對話實際接續仍未完成。正式部署/真人 UAT/跨平台/人審升格皆未做。

## Requirement→實作→驗收 trace
| R | 實作及 observables | A |
|---|---|---|
| R01 | public_list/detail, workspace, true browser full lifecycle, CLI second process | A01/A05 |
| R02 | server session actor, role/owner, author-b/anonymous/editor negative | A02 |
| R03 | Store._change, state/public pointer, old public until publish, withdrawal/republish | A01/A04 |
| R04 | /api/articles?q/category/page, public detail, DOM 21 records 20+1 | A01/A06 |
| R05 | login/logout/session expiry/rotation, PBKDF2, local Host/Origin/CSRF; direct HTTP | A02 |
| R06 | bounded_text/content, enum, JSON cap, literal script text and parameterized SQL negative | A03 |
| R07 | one_open, expected version, actor/token payload receipt, two writers, actual cut and dropped ACK | A04 |
| R08 | local work status/reason, no outgoing integration | A01/A02 |
| R09 | role/owner/visibility, audit history incl reason/counter, direct endpoint denial | A02/A04 |
| R10 | only synthetic, backup/restore exclusive/old sessions revoked, no public hidden content | A02/A05 |
| R11 | stdlib/SQLite isolated paths; init/verify/serve and actual process relaunch | A05/A07 |
| R12 | DOM 375/1280, actual Tab, labels, no overflow, visible errors | A06 |
| R13 | source/CI, guide, backup/restore/rollback plan, no external launch | A07 partial: fresh-dialogue continuation pending |

All local gates are limited to tested contract/environment; no manual UAT or deployment. Do not count as independent blinded Agent ability scores.
