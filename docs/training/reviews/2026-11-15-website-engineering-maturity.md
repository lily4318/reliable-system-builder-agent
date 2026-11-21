# 網站工程交付成熟度盤點｜2026-11-15

紀錄 NATIVE-MATURITY-012-REVIEW-HANDOFF。依使用者本輪明示任務；不是正式發布或擴張授權決策。基準 9384651b6f4243706ff9bfbf19df5afe7c71b29d；CI 43705370942，418/418。實作 560d143bd9db245f263906bc478ad5379b9eab23，CI 43705735689，424/424。以下是觀察及證據分層而非主觀百分比或整體模型分數。

## 七角色與十二技能（完整 catalog 回讀）
| 角色 | 技能 | 既有可用證據 | 完整網站尚缺 |
|---|---|---|---|
| System Lead | project-intake, task-planning, resume-project | 13題/6案例、scope gate、bound task revision、實際原PR跨對話接續 | 新網站真實需求及授權、同一完整交付的續作驗證 |
| Architect | requirements-spec, architecture-design | EP-01 結構追溯、EP-07 技術比較、EP-08實際 SQLite | 審閱後語意整合、具體驗收與目標架構；本輪完成可檢查 handoff，非完整核准規格 |
| Developer | implement-feature, debug-and-repair | B001/002、P21設備站、P22報表，近期實際 repo red/green 修復 | 依陌生規格作真實網站垂直切片而非重跑示範 |
| QA/UAT | test-and-acceptance | 正反測、actual Chromium、EP-11 bounded gate | 同一全站真實功能/負測、另行真人 UAT |
| Security | security-review | EP-03交易、防資料混淆、P21角色檢查、EP-05/08資源限制 | 特定網站資料分類、授權矩陣、負測及威脅模型 |
| DevOps/SRE | deployment | 同 SHA CI、read-only reconcile、版本/回退及人工步驟 | 具體環境可回讀部署計畫、另行授權實際遠端操作/回退 |
| Learning Evaluator | learn-from-feedback, knowledge-distillation | 11 EP、2 default 6 opt-in、近期原檔覆盤和 case evidence | 人審非重複升格、獨立任務/平台遷移效益；不自動提升 |

## 11 EP 與全站階段對照
| EP | 使用場景 | 証據或限制 |
|---|---|---|
| 01 | 需求正/負/未決及來源 | NATIVE-REQ-004；本次真實 export 對照整併；非語意評分 |
| 02 | 編輯、確認、版本綁定 | NATIVE-TRANSFER-002/NATIVE-UI-003，P22-CASE-001；本次 handoff hash/失效；非身份證明 |
| 03 | 表單名額庫存/冪等 | B001/B002,P21-CASE-003；外部資源另驗 |
| 04 | DAG/版本失效/復原 | NATIVE-TOPOLOGY-006、NATIVE-EP-009；可信同庫 |
| 05 | 檔案/報表/快照 | P22-CASE-002/003/004，NATIVE-EP-011；無 live CAS |
| 06 | 真實瀏覽器/角色/遷移 | P21-CASE-006；自動 DOM 不等於真人 UAT |
| 07 | 技術選擇/未決政策 | B003 prototype；需具體產品政策 |
| 08 | DB 查詢與物化資源 | NATIVE-ARCH-005、NATIVE-EP-011；非 production SLA |
| 09 | 跨角色守門/形狀 | NATIVE-ARCH-006、NATIVE-EP-008；本次 literal confirmations/strict schema |
| 10 | repo-native/接續/檢索 | NATIVE-AUDIT-001、NATIVE-CASE-001；非私人 DB 或自動跨平台工具 |
| 11 | 功能 oracle 與 QA 退件 | P1-2 bounded、NATIVE-EP-010；18公開案例，不是全面語意或真模型 |

維持原索引與 CASES/TRAINING_CASES，不重複升格同一工程經驗。

## 優先問題及取捨
1. 已落地 G1：使用者審閱結果無可驗證整合入口。原 export flags 明示未批准；不可把已拒絕推導又當施工需求。用原 deterministic generator/既有 UI/CLI，而非新框架、通用自動 orchestration 或另一個同類練習。已完成 **design-review input**，不能把它稱為完整 confirmed specification。實測 424/424，6個真 DOM handoff。
2. 待驗 G2：完整新網站 vertical slice，需求確認→架構→工作包→可運作前後端/資料→正反測、權限、UI→同 SHA CI/原版本及部署回退計畫。優先公共合成或經允許的實際委託，使用者先可編輯確認具體需求；不要重複既有垂直切片題目或把舊 UI 訪談誤當全站交付。使用者確認規格與候選 patch 授權分開，外部/正式部署仍獨立。
3. 待驗 G3：在另一新對話不依賴聊天摘要，從同版本原交付產物/決策定位未完成工作、辨識漂移且不重做；記錄實際平台工具、角色技能、EP 選用理由、遠端回讀與未決。不能要求安裝本地模型作為先決。
4. 待驗 G4：真正跨平台/真使用者獨立評閱、適用私人工作空間、遠端部署／回退或產品真人 UAT（視獨立授權）。這些不是 G2 的候選開工必需前提，也不能由公開測試替代。

## 可檢驗完成判準
- G2 前置：每個核心功能有穩定需求 ID、保留否定及未決、明確 acceptance、使用者的完整確認證據、具體目標及 scope；未知或衝突只阻塞相應工作。handoff hash 只核對內容。
- G2 交付：實際網站功能，來源可回讀，核心成功/拒絕/異常/權限/中斷測試，必要真 DOM，資料持久性、重複/競寫（適用時），同 SHA CI，未得部署權時交操作及復原計畫；不冒稱上線。
- G3 交付：另一實際對話讀最新正式原檔及證據，重驗過期輸入、延續尚未完成必要工作；無私人素材上傳公開 repo。
- G4 視授權：實際遠端版本、真實 UI UAT/獨立評閱、正式啟用及回退，各自證據。沒有工具時明確報阻塞並指出可做替代；公開案例 PASS 不代表模型增益。

以上 G2–G4 是可編輯的下一階段建議和判準，不自行批准新外部專案、真實使用者資料、付費 API 或發布。
