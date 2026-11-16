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
