# 必要專家能力盤點與研究字典跨角色交接｜2026-11-16

## 範圍與來源
使用者明示依最新正式主檔，PM、System Lead、Learning Evaluator 盤點八角色十五技能並實作研究需求、字典、架構、開發、QA、匯出交接。本輪同一 Agent 按角色分工（REPO_NATIVE / SINGLE_AGENT_ROLE_WORK）。基準 Draft PR #8 head be7c2c226531c657cf6635829d2275a5f43cc649；[CI 43736595842](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43736595842) completed/success，run metadata，未讀完整 raw log，前一研究資料 lab 不因 CI 綠燈認定已被 CI 執行。主檔 0fa3a295600af3bfcb8f284eface9b4470f9062d；決策 b0196ce9040acde95fa393ce8d8672024d768529；catalog 1bc4f3711237694b4bb82f3c38e100ac143d9d03。核八角色檔與十五 SKILL 的責任、前置、既有案例段落；並核 test_engineering_workflow.py 3b1c961b3a8fab8b9ca1a855f94d9b3d796c1759、test_team_workbench.py 47f193e7c2f661c8d5e8804dcb69e883e27f4e58、test_workbench_revision_sync.py d0b57aecadd338bf89d0b4efbe347dff2e8162a2、test_workbench_learning.py d8ebf82e03eb7edc4df714a40cab65fae30c8c67、test_website_review_handoff.py cf3ea9b4b75e6fbd92d45c7ba6628517da0b4f3a 的測試方法清單；原訓練主檔、決策及 [原研究資料實證](2026-11-16-research-data.md)。非逐行審計或重跑全部原測試。

## 八角色／十五技能逐項盤點
下表「已有」據原正式紀錄及上述測試入口；不等於全域 L 級或獨立能力認證。P0 為本輪必要交接補強，P1 是後續依實際風險選必要缺口，DEFER 需原獨立授權／真人／長期教材，不提前。

| 主責 | 原 skill | 已有實證或實作入口 | 剩餘必要缺口／處置 |
|---|---|---|---|
| PM | project-scope | M1 PM catalog、確認範圍與工期、研究/教學 scope | P0 字典變更影響交付與需明確決策，本輪受控範圍拒絕；真研究科學確認 DEFER |
| PM | project-control | M1 stale scope、原 task pool、stop | P0 保留原 scope、只重驗受影響工作；未量測真多人進度 |
| PM | delivery-review | M1 delivery gate、QA/安全獨立 | P0 防舊 PASS 與範圍冒領；總體 UAT DEFER |
| System Lead | project-intake | 13 題六場景、實際 DOM、NATIVE-REQ-004 | P0 研究資料單位/缺失語意交接；真研究者確認 DEFER |
| System Lead | task-planning | EP-04 revision/topology/worker fence、combined revise | P0 同一需求 ID 仍有語意變動；本輪不同領域，不重做 DAG |
| System Lead | resume-project | A07 history-assisted；revision/receipt | P1 以新字典、產物與剩餘依賴接續；source-only A07 DEFER |
| Architect | requirements-spec | NATIVE-REQ-004、審閱交接 424 tests | P0 字典內容/單位、缺失語意版本；本輪加入原技能 |
| Architect | architecture-design | NATIVE-ARCH-005、PG-022/023/024、study scope 8/8 | P0 字典版本映射；P1 真語意遷移採新明示政策，非自動轉換 |
| Developer | implement-feature | editorial/equipment、M2-1 browser CSV、研究資料 10/10 | P0 拒絕 stale dictionary、export manifest；P1 研究實驗時序及中斷如適用 |
| Developer | debug-and-repair | NATIVE-TRANSFER-002、HTTP red/green、PG fix | P0 合成對照拒絕 9 個風險；非原產品缺陷；P1 真實新缺陷才修 |
| QA | test-and-acceptance | 真 DOM、HTTP、PG、研究資料快照 10/10 | P0 literal value oracle 與空匯出 manifest；P1 瀏覽器時序/中斷測試如適用；真人 UAT DEFER |
| DevOps/SRE | deployment | CI artifact 完整性、local activation/rollback 4/4 | P1 訓練必要復原資料/版本相容風險；真平台 C1/C2/C3 DEFER |
| Security | security-review | HTTP framing/RLS、study membership/revoke 8/8 | P0 合成 scope 變動拒絕；P1 真平台 session/競寫視需求；真資料/授權 DEFER |
| Learning Evaluator | learn-from-feedback | test_workbench_learning 的候選、citation、no auto approval | P0 保存受控對照與限制；無私人工作台，不偽造事件 |
| Learning Evaluator | knowledge-distillation | 原 EP 索引、curriculum validator、案例去重 | P0 將語意版本/資料交接納入原技能，保留證據粒度；指定教材 176/163/13 partial DEFER |

結論：所有角色和技能均有候選契約及某種既有工程證據；不是 15/15 實際成熟度，不宜要求每角色重做同一案例。首版 2/6，M2-2 partial 保留。真實外部部署、A07 source-only、B10、真人本機 UAT 皆保持未驗；按使用者要求暫緩討論整體驗收。

## 選擇本輪實作的根因及設計
讀 EP-01（來源語意）、EP-04（版本失效）、EP-11（功能 oracle）的索引與原證據入口。已證 revision/workbench DAG、原子更新/快照、權限隔離，故不重建任務池或 SQLite。仍需不同場景：同一需求 ID/欄名或相同 revision，研究者改變測量單位或缺失值語意時，下游舊 PASS 可能具形式一致性但語意不相容。例 v1 1ms/單位、0–5000；v2 10ms/單位、0–500；150 代表不同物理量。合成 v2 只允許本地資料、禁止自動遷移/真收件/外部部署，非真人研究決策。舊資料先保留原版本，若需轉換，另由研究者核定轉換規則、精度、無損性及遷移驗證。
方案 A：ID + PASS（刻意不安全對照）；B：同一已知合成決策完整字典、唯一必要產物種類及來源字典比對；C：真系統使用現有 workbench 版本、可信來源 digest 及具版本 schema/manifest；本輪採 B，無需建新管理平台，並將規則遷移回現有技能。canonical JSON 僅處理固定合成資料域，不是通用 RFC canonicalization 或安全簽章。

## 真實執行與交接證據
[可重現 JavaScript lab](test_research_handoff.js)，git blob bc2ffa651d073a2c5be0d43f7750bed4231cae5c。在受限 JavaScript 執行環境實際呼叫同一 runLab 函式（非本機 Node subprocess，不使用資料庫/網路），逐 case 捕捉例外並列結果；遠端保存同一函式 toString 和 Node CLI wrapper，可用 node docs/training/reviews/test_research_handoff.js 重現，未聲稱 wrapper 已在 Node 執行。
- 13/13 strict PASS；legacy 4 PASS / 9 FAIL，逐項 fail：stale_architecture, stale_developer, stale_qa, same_revision_changed_unit, old_source_not_auto_converted, duplicate_role, modified_scope, missing_semantics_changed, no_implicit_migration（最後一項與來源版本重疊，不作九個獨立缺陷）。其餘正測 current_contract、empty_export_has_manifest、valid_looking_wrong_values、bounds_and_zero 均過。刻意對照不是原產品漏洞。
- PM：合成 scope/禁止事項不擴權。System Lead：需求 ID 與語意版本一致、每必要 artifact kind 唯一。Architect：v2 完整字典與原資料版本比對。Developer：實際生成 numeric-only CSV / separate manifest，固定排序、Source revision、decision ID、row_count，空資料有 manifest。QA：另一解析路徑、固定 literal 預期 manifest/values，拒絕有效格式但 150→15 的輸出；不把 PASS 或自述當證據。Learning Evaluator：保存同源 test、結果及限制，沿原技能增量。Security/DevOps：此 lab 只證明範圍和版本守門，沒有授權/登入/真版本啟用；沿原實證分開。
- L3 層級受控工程實作及知識遷移練習，非 L6 真跨獨立代理驗收、非模型提升、非獨立盲測或指定教材完整七階段；未實際呼叫私人 SQLite workbench。fixture 原本就是 v2，不執行舊資料 migration；CSV 僅整數/null，未驗真試算表、任意欄位、外部簽章、manifest/CSV 原子發佈、HTTP/DB/並行寫入或時間量測；前輪 DB 快照實證保留，本輪不冒領。既有原產品代碼不修改，無新工作流、帳號、成本或部署。

## 剩餘最小必要訓練
本輪交接閉環可標 LOCAL_SYNTHETIC_LAB_VERIFIED，不標整組訓練完畢。優先 P1：線上心理/行為實驗的時間戳、單調計時、刺激時序、失焦/中斷、trial 紀錄完整性與研究者預先確認的有效性規則；先查 M2-1 教學 APP/原 browser 與其他正式案例證據，選一個未覆蓋且必要的受控垂直切片，非強制新網站或真實科學精度驗證。待此能力盤點之後，按實際缺件決定是否需補資料字典真遷移、復原或其他必要專業能力，避免無限增加合成案例；不自行提前 M3/C3/M4、不要求真人。原日期 11/22、11/29 與 NT$0 保留，可能因訓練順序影響，未另承諾交付日期。


## 2026-11-17｜必要能力收斂（TD-005 / CAPABILITY-CONVERGENCE-005）
### 來源與實際證據查核
使用者明示 PM、System Lead、Learning Evaluator 逐項查核八角色十五技能，優先真正阻礙首版的必要缺口、同步原 GitHub，不重做、不提前真人驗收/部署。基準 PR #8 6143a8868b185bf91846eb4793cd5c3349214ae8、tree 194aaf8c09d114e704612e537490723ab8ee4270；主檔 9577e381a426f2d367cdf6bdf27b59155578c06d、決策 6b0d75c553200d71192878b68833a54889526803、catalog 1bc4f3711237694b4bb82f3c38e100ac143d9d03。實際讀 START_HERE/AGENTS/release/policy、最新決策的 TD-005 M0/M1/M2-1/M2-2/次序修訂與最近訓練；八角色指令（PM/Lead/Evaluator 全文，其餘角色責任/技能段）、十五 SKILL 的責任/實證段及相關測試方法入口；非全面逐行審計所有產品。沿用原 REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，未啟動三個獨立模型、無私人 workbench 寫入。

[CI 43899826677](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43899826677) job 133413100085 completed/success；實讀原 log 257003 chars：Ran 517 tests in 85.051s / OK；RESEARCH-METHODS-BROWSER_PASS 375 與 1280 各 actual_csv_rows 100 csv_bytes 3161、EDITORIAL_BROWSER_PASS；CI_EVIDENCE_BOUND run_attempt 1 checkout bd9a760838179b5a32f4d70ec506f66ad66ec171 report_sha256 004a353acd5267260f3891027a18c74637974927733bdf063122bfb75b38ab4a。實查 merge commit parents main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57 + candidate 6143a8868b185bf91846eb4793cd5c3349214ae8，tree 與候選相等。未再下載原 CI artifact 或獨立核其 bytes；不要將 marker 當簽章。原 43724770963 的獨立 artifact 驗證仍保留。現 workflow discover tests 及既有 browser steps 並無 reviews labs；原 log 未見 trial lab，不能把 517 綠燈冒稱這些 lab 重跑。原 APP 三 blob index.html 2254022d7b8eccdaa63b0a9d026b2d53da7c0c57、style.css 644e3481d307ec1e7d2afec822b709b562bd09ae、app.js df98563e19bea4b5919ee52b23316eaaaaa2c6b6，實際讀回與 M2-1/M2-2 紀錄一致，不重建 ZIP/APP。原 file:// 真人驗收未證。

本輪實際執行一次唯讀 JavaScript 程式交叉比對已讀 catalog 與原 job log：每個 skill 對下列既有方法的精確名稱逐一要求恰一條「... ok」；15/15 catalog entry 對應、8/8 角色、28 個不同 method 皆匹配，無額外 skill。相同 method 支援不同角色責任只計一次，不等同十五獨立技能分數。此為新證據覆核，不重跑舊測試、新合成模型或新增管理 engine。原 test_team_workbench 的 PM method 實際內容顯示未具前置拒絕、scope 改變使 progress/review stale、重發新產物、需求修訂使 scope stale、authorization_granted=false、model_or_subagent_invoked=false；不能把手工 fixture 當真人 PM 授權。下表為此次確實對照的 log 方法（皆前綴 test_），保留既有實證與限制。

| 主責 / skill | 2026-11-16 job 133413100085 實際通過的方法（省略 test_） | 既有能力及本輪結論 |
|---|---|---|
| PM project-scope | pm_handoff_reuses_workspace_and_stale_scope_blocks_delivery; requirements_and_acceptance_before_architecture | 已證必要範圍/前置/失效；原確認 MUST 不削減 |
| PM project-control | pm_handoff_reuses_workspace_and_stale_scope_blocks_delivery; revised_requirement_invalidates_downstream | 已證修訂與 stale progress；原六包及停止條件可用，非真多人時程績效 |
| PM delivery-review | pm_handoff_reuses_workspace_and_stale_scope_blocks_delivery; release_with_all_green_still_requires_real_uat_and_human; missing_human_review_blocks | 已證人審與停止守門；不得提前驗收 |
| System Lead project-intake | bootstrap_13_questions_6_examples_prefill_no_gold; no_write_or_deploy_authorization | 既有訪談/六種合成場景/原 DOM；新手真人 B10 尚待 |
| System Lead task-planning | revised_requirement_invalidates_downstream; conflict_and_competition | 原 DAG/revision/fence 及真交易；不重做 |
| System Lead resume-project | real_content_handoff_and_resume; after_commit_lost_acknowledgement | 原內容接續、復原與 M2-2 source-assisted；A07 source-only 未關閉 |
| Architect requirements-spec | all_six_exports_apply_edits_and_exclude_rejected; stale_missing_duplicate_mismatched_and_malformed_block | 原規格審閱與語意字典交接 13/13 受限 JS，研究政策仍由人核 |
| Architect architecture-design | architecture_dependency_and_rollback_before_code; pg_shared_migration_preserves_v1_history_and_old_contract | PG 真遷移/隔離、選型与 trial/GAS 契約；真平台適配另查 |
| Developer implement-feature | academic_app_real_browser_and_download; transaction_failure_rolls_back_stock_and_receipt | 真 APP/CRUD/DB、動態研究資料及 trial；原教學 APP 不需新增 DB |
| Developer debug-and-repair | http_framing_incomplete_valid_json_has_no_mutation; form_framing_incomplete_reserve_cancel_return | 原真 HTTP red/green；GAS-DIAG-002 為模型、Cookie 為使用者回報 |
| QA test-and-acceptance | academic_app_real_browser_and_download; ci_must_match_exact_code_and_test_sha | 真 DOM/CSV/正反測；真使用者、硬體精度另驗 |
| DevOps/SRE deployment | matching_files_and_identity; wrong_sha_run_attempt_and_repo; unknown_and_partial_write_override_every_other_green_signal | 既有 artifact byte 驗收/local activation restore 4/4；真 HTTPS/C3/版本更新/回退尚未驗 |
| Security security-review | security_data_and_acl_hard_gate; pg_shared_identity_rls_function_acl_and_foreign_cancel | 原 RLS/HTTP、study scope；真雲端 Auth/真人研究隱私另驗 |
| Learning Evaluator learn-from-feedback | feedback_candidate_and_dedup; candidate_preference_never_applied | 原私人工作台工具及去識別案例；本輪未操作私人庫 |
| Learning Evaluator knowledge-distillation | learning_dedup_conflict_review_and_history; adoption_requires_analysis_and_reason | 原知識去重、validator、EP；全教材與獨立盲測未證 |

### 最近專項成果與獨立證據層級
實際讀回現 candidate 的下列程式 blob（與原覆盤相符）：test_research_scope.py 02e74e638851283de5f47bc7ce293bbeeae9beb0（8/8 本機 SQLite）；test_research_data.py 59d95f775a05913b8e6f1632be45189eef7cfdd6（10/10 真 WAL/快照）；test_research_handoff.js bc2ffa651d073a2c5be0d43f7750bed4231cae5c（13/13 受限 JS）；test_experiment_timing.py 7dfc5339de6b6e6c151c7b2706c0e3a8ffeb64f4（11 PASS/1 SKIP 真 Chromium，真分頁/物理精度未驗）；test_gas_diagnosis.js d4576be629c81ef84234485a293a73341ea4c428（28/28 受限 JS）、test_gas_data_integrity.js 3180eb961a1e1643bf073ab40764e07c27fa831c（18/18 受限 JS 模型，非 Google）；test_trial_recovery.py 9489ea3f4195c1495760fffa2543e1594dd5b65b（9/9 本機 Chromium+SQLite host bridge，IndexedDB/HTTP/GAS/真並行未證）。結果沿用前輪原日誌紀錄與同 blob，這輪只核來源/存在，不重新執行或偽稱原始 local log 重新取得。GAS-DATA-003 CI 43898561110 已 success（前輪查核）；上述前輪 lab 和本輪 CI 證據不同。L3/部分原真工程缺陷修復證據不等同各角色整體 L4/L5/L6、獨立模型提升或完整教材七階段；沒有新增學習完成率。

### PM / Lead / Evaluator 決策與交付風險收斂
- PM：原 M1 與 M2-1 兩包完成，M2-2 partial；首版唯一已核准 APP 為合成雙組分派、資料模擬/CSV 的靜態研究方法教學 APP，非所有研究系統同時完成。原 MUST、六包、11/22 checkpoint、11/29 candidate aim、NT$0 保持。現有資料庫、後端、實驗、GAS 能力可支援架構取捨及基本工作，不代表第一版必須增加真資料庫、GAS、登入、計時或多個 APP。未辨識新的可在既授權範圍內且確實阻礙首版的程式/技能缺陷；不為訓練數量再開 lab。此為有界訓練停點建議（NECESSARY_TRAINING_EVIDENCE_CONVERGED_FOR_CURRENT_SCOPE / PROPOSED_STOP），不是 M2-2 READY_STOP 或使用者確認整體能力。未充分證實真實跨平台操作能力。
- System Lead：A07 真新對話 history-assisted 已有；URL+task-only 獨立來源仍 pending，APP 真人本機 UAT/B10 pending；都是原交付證據而非需要重建軟體。使用者要求不提前真人驗收，保持 deferred，不發測試指令、不要求操作。M3 / C1 remaining actual permissions/cost / CLOUD-A C2 / C3 distinct authorization / true HTTPS、版本更新與回退/適用 C6、M4 正式核准仍缺；只有獨立授權後才進相應工作，不能用本機證據頂替。M2-2 不得以歷史摘要、同聊天或重新取包判完成。下一步先由使用者決定是否結束本輪必要訓練並另議首版驗收順序（不是進行驗收），確認前不開始 M3/C3/M4。可先做不涉及操作的方案或必要證據查核，非無限重複。
- Evaluator：教材 176/163/13、引用與矩陣 PARTIAL 不變，依 TD-004 後續學習；真原生 IndexedDB、完整多 Trial/科學精度、真 GAS/Sheets transaction、真 Supabase Auth/跨 writer、schema 語意遷移等屬具體專案需求觸發或合適環境/新授權的未完成能力，不是已驗收項目；PG 已有歷史 migration 真證據，不能為「遷移」標籤重複；若之後實際需要新語意轉換再驗。未宣稱全八角色專業精通、不減必要安全/人審門檻。新增的是原證據索引與真 log 對照/停止條件，不改原程式、workflow、APP、主分支、release、資料、部署或成本。
- 選項取捨：A 持續泛化合成 lab（不採，缺明確首版風險）；B 收斂原證據、保存明確未完成及請使用者決定下一階段（採，符合本輪授權）；C 直接 M2-2 真人測試或 M3 部署（禁止提前）。如後續出現新確切必要缺口，先記錄 MUST 關聯/實測失敗/影響/可安全修復範圍，核原證據不重做，再獨立針對性實作。保持原交付 2/6、M2-2 partial、原 A07/B10/UAT/C3/release pending；以本次覆盤作建議，未擅自宣布使用者已確認所有必要能力或批准驗收。
