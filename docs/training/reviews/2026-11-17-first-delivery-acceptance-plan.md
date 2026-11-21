# TD-005 首版整體驗收方案（ACCEPTANCE-PLAN-006，2026-11-17）
狀態：集中必要專家訓練收斂方向已由使用者確認；本文件是 PROPOSED / NOT_RUN，待使用者確認驗收方案及下一步執行授權，不是驗收報告。原 M2-2 授權歷史保留，本輪明示只規劃；C3、M3、M4、正式發布各獨立授權。

## 來源及不變條件
基準 Draft PR #8 cdaba6eb2662b74f008f5b95786e0390d9e1ee71 tree f62dc85395be3236389765588e8ff784430dcb74；CI 43996320793 completed/success（run metadata，本輪未讀 raw 或重跑）；主檔 9f12a69c95670c84e9919d9da358ae104b27b3b1、決策 3154d02abc4d3006dbe27b2d5537b1c21c89c608。START_HERE fa25602a81595e9f73675adec3b08b497ef9c224、AGENTS 95b6e26d9f163f325b42fe4e7f78336b7d646d1d、release 6babe416f2ed652509b44d90d3eb98637a0886f3、policy 5fb5e2e5e3a41c2361769f7dc0ae42454d09d058。讀 M0/M1/M2-1/M2-2、A07 PROTOCOL_PREPARED / NOT_RUN、CAPABILITY-CONVERGENCE-005、[APP 規格](../../RESEARCH_METHODS_APP.md) 7dad2a37313ba8da79480b19565894ba01559f20、[B10](../../BEGINNER_ACCOUNT_ONBOARDING.md) d4727f11e4345f59ed1e6a70d63be953d54d13b6、[C0–C6](../../CLOUD_ARCHITECTURE_SELECTION.md) 442fa4a363b8b65935651e78ad07197970624618、[獨立復原](../../INDEPENDENT_ACCEPTANCE.md) 39a5d00ea59d5abe0457a16e6fa42a561e8f0522、[正式發布](../../RELEASE_REVIEW_AND_ROLLBACK.md) 1c08b4f4d6033115649f49efce8e5848baa81734、[治理設定](../../GITHUB_GOVERNANCE_SETUP.md) 0290cea817583b4637f5af3d2b18bf841aa0e40c、[原審查清單](../../../release/REVIEW_CHECKLIST.md) 38e3b22b843e5ed8c64b177413a62a8cddaca771。歷史 517/517 raw CI 43899826677 job 133413100085 已核於上一輪，15/15 skills 28 distinct methods evidence；不再次執行。
維持一個已確認合成研究方法教學 APP、8 roles/15 skills、6 工作包、2026-11-22 管理檢查點、11-29 候選交付目標、NT$0、原 TD-004 延後。M0 確認、M1 及 M2-1 READY_STOP，共2/6；M2-2 partial，M3-1、M3-2、M4 pending。不得自行新增網站/登入/DB/功能、重建 APP、要求另學全部教材、付費、外部專案、部署、main 或發布。本輪不測 A07/B10/真 UI，不更改帳號設定、平台、CI workflow。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK。

## 原首版八項完成條件的操作化對照（不新增或降低 MUST）
| 編組（本方案整理，非新 gate） | 當前證據 | 完成判準/剩餘位置 |
|---|---|---|
| 1 PM 管理/按需團隊 | M1 516/516、8/15 catalog、stale scope | 原確認 scope、上限、專家/交接、無擅自增功能、停止；沿用，不冒稱獨立八模型 |
| 2 自然語言到研究/教學規格 | 原 13題流程、M2-1 R1–R5、原確認 | 研究目標/參數/字典/限制可讀且一致；原已核准規格，不重問；任何改動另確認 |
| 3 可操作學術 APP | M2-1 真瀏覽器 | 原 APP 可直接使用、正確展示與 CSV、真人 local M2-2 |
| 4 正確資料/QA/security | 原 CI 517/517、原 R1–R5 | 適用同版本真測、正負例、安全無個資；M2-2 與遠端 C4/C5/C6 補缺 |
| 5 A07 跨對話 | history-assisted 另對話成功 | source-only 真新對話、最小任務、來源及隔離證據 |
| 6 B10 必要新手引導 | 現有連接調查及離線 16 tests | 真適用初心者任務與人類理解/操作證據；無適當人/環境則未驗限制，不造帳號或自動 PASS |
| 7 真 HTTPS/版本更新與回退、C6 | local rollback、平台唯讀部分 | C0–C2→C3 獨立許可→C4/C5→C6 真遠端與人核 |
| 8 交付/維護/停止、M4 | 原 PM 停止規則及候選 | 操作/維護、版本/已知限制、原 release checklist/治理/非作者人審及另行發布授權 |
原 A01–A06/公開回歸沿用；以上八組為原 MUST 的整理（PM/按需隊伍合併、交付/維護及 M4 合併），不新增官方 A/B 編號、獨立盲測或模型提升要求。

## 工作包3（M2-2）：來源接續及真人使用，待本方案確認後才執行
A07 沿原 11-16 PROTOCOL_PREPARED：專案外真正新對話，優先 Temporary Chat 或可用不含舊專案歷史的獨立環境；實際可用工具/記憶/自訂指令情形需核當時產品文件與環境，由使用者自行操作，不要求改安全設定、刪除歷史或分享 secrets。只貼 repo URL 加已授權 M2-2 任務；不附 head/CI/答案/摘要/驗收表。指令草案：『https://github.com/lily4318/reliable-system-builder-agent 請依最新正式來源接續 TD-005 M2 第二工作包，完成已授權的接續查核與必要交付指引；不重建 APP、不增加功能、不部署或正式發布。』新對話先只讀查核，報真實分支/head/blob、來源、證據、有效授權、完成與下一安全工作；如無寫權就明示，已授權原對話只保存必要去識別證據，不強迫新對話寫入。人保留首則指令、環境/隔離與完整回覆/來源證據（脫敏）；原評閱對話固定當時 head 交叉核對，避免把舊聊天或指定回答當來源。真來源讀取、原狀態/授權正確、未重做/越權、實際下一安全步驟與可查證證據全具備才 PASS；不能隔離或讀取資料→PARTIAL/BLOCKED_ENVIRONMENT，錯版、假操作、擴權→FAIL。不能把本輪計畫或同聊天當 A07。
APP human local UAT：Agent 先依原包/三 blob 準備可下載 ZIP（若原附件不可用，僅依當前同 blob 重包並核內容，不造新 APP，保存實際 SHA，不宣稱原 ZIP bytes 重新取得）；使用者在 Windows 檔案總管右鍵解壓縮全部、以 Chrome 開 index.html；n40 seed1 →「產生模擬資料」→ A/B各20、同 seed 重播一致、seed2 改變結果；改21→舊資料清空、禁止下載、產生錯誤；改回40/1→生成並下載 research-methods-40-1.csv，40筆+標題、六欄/值與畫面及 sim-v1 參數一致；檢基本鍵盤/可讀性、合成標示。先存有效結果再測非法值，返回合法條件再下載；使用者只回非敏感結果/遮蔽錯誤與 CSV（合成、可選）。技術比較/欄位核對由 Agent 代做，不要求 CLI。遇政策封鎖停止，不改安全或公開；已授權本機靜態預覽可作替代，但如實記 file:// 未驗；不能以先前 loopback CI 算人測。所有適用 R1–R5 及人類核心使用項通過才 PASS，錯誤需最小修復後重驗受影響範圍。
B10 同一整合使用流程盡量合併取證，不要求多餘帳號。若適當且自願的真正新手可參與，給一個當前步驟（位置、輸入、預期、錯誤處置），由人操作/回報是否理解，Agent 真查可用工具/目標/權限/成本，觀察已有帳號跳過、需要開帳號的適用分支、連接錯誤適用分支；不刻意製造錯帳號/付費/新帳號。離線 APP 本身無帳號，M3 如真需 Pages 步驟另取證，不能把 APP 可開、既有連接或 CI 當所有 B10。無適當獨立新手則按原 TD-005 記 NOT_TESTED/PARTIAL、限制與後續計畫，由使用者明確確認候選交付如何揭露，不降級成 PASS。A07、UAT、B10 分開記；M2-2 PM 適用必需達成、B10 原許可限制明確處理才 READY_STOP，不自動進 M3。
 
## 工作包4（M3-1）：C0–C2 準備（另授權）
首選評估既有 CLOUD-A GitHub Pages，同一合成 APP，不代表平台已選定或可用。C0 確定僅三份公開靜態資產/單一案例、受眾、無登入/DB/收集、NT$0、版本與回退；C1 先讀真目標 repo/現任 owner、Pages 是否已有站點/部署來源、可用權限、目前 plan/條款/quota、Actions 用量/成本、所需工具；如有既有網站衝突、費用/綁卡/權限不明，停並提可核零成本替代，不改私人 repo visibility。C2 設計白名單 artifact-only（不發布 repo 根目錄、訓練文檔、憑證、其他研究資料），核相對 path/base path、資源、密鑰與隱私掃描、候選 SHA、原 regression/實際 artifact bytes、可重現版本與 rollback，提供 C3 具體 target、變更、受眾/公開、有效期、成本、回退/清理。同一工作包只限獲准候選準備，不觸發遠端部署；如需 workflow 準備亦必須避免自動部署觸發，另核工作範圍。C0–C2 PASS=真 account/target/plan/必要 quota/安全與可部署 artifact/同 SHA 證據、rollback 皆滿足，未知不通過。PM 停在 C3 許可之前。
 
## 工作包5（M3-2）：C3–C6 真實發布測試（獨立授權；非 Agent 正式 Release）
C3 由使用者核准精確資源、公開範圍、操作、版本、NT$0、有效期限、更新/回退及必要清理；C1 新核權限/費用。Agent 優先代做有權限操作；若確須本人，參原 Pages 指引 Repo→Settings→Pages→Build and deployment，僅在無現有衝突且核准後選適用來源（可能 GitHub Actions）；當時先核 UI/條款，不預先要求 Save/開帳號。C4 實際部署、回讀 URL/HTTPS、build/deploy run/artifact digest/SHA、真匿名與非部署者無需登入能開、版本與資產一致。C5 同一 URL 先 v1、後僅核准無功能擴張的可辨識版本變更 v2（版本標記策略待 C2 明確，不修改科學參數），再切回已核 v1；每步真遠端 fetch/DOM、source/artifact identity、完整功能及 CSV、非法參數、375/1280、無私檔/外連/意外公開、跨帳號乾淨 session（不因 cache 誤判）、保留已驗回退點。真 provider 狀態、使用者所見、commit/版本與 artifact 各自核對，不以 HTTP200 或 deploy success 代替。資料交易/登入/DB/migration 為本靜態案例 N/A 並說理由，不標真動態驗證；危險或 UNKNOWN/PARTIAL 先 READ_ONLY_RECONCILE，不重送、不盲切版本。C6 真人從真 HTTPS URL 按核心合成流程操作與回報；充分的 M2-2 同一規格證據可重用，但遠端版本及真使用不能省；明確使用者啟用核准、維護責任、故障回退、用量/成本、資料保護。驗收用測試部署與正式公開啟用依 C3/C6 分開，不自動擴公開範圍。工作包5結束停，M4另授權。
 
## 工作包6（M4）：交付審查及治理、正式 Agent release 另准
Agent 出具已核准範圍/可用 APP/版本/URL/操作及維護方式/限制與原證據清單、目前候選 SHA、品質守門、回退參考、TD-005 6包狀態，依原 release checklist。保留非作者真人審查、資料去識別、expected/actual 獨立、CI/privacy/原 recovery/quality thresholds、真跨帳號公開讀取。原治理文檔 11-12 時 main 無保護、rulesets空、無正式 Release workflow；此為歷史，不是本輪即時平台調查。實際執行前只讀重核；需 Owner 介面設定時給 Settings→Rules→Rulesets、Environments 的當時官方逐步指引，只在另授權後操作。原要求 Active main 規則、至少1位非作者且具 Write 的可信 reviewer、verify 必過、禁 force push/delete，合理無繞過；另 formal-release-approval Environment、Required reviewers、Prevent self-review、實際正式發布 job 明確引用；適用阻擋與通過測試/回讀。沒有合格 reviewer 不自動提升權限；無法安全配置/功能不可用/費用不明則 BLOCKED、保留候選，不把過渡規則或 Environment 存在當完成；不宣稱可以封鎖所有網頁手動 release。不得為驗證而提前真正合併 main 或建立正式 tag；安全治理驗證的測試範圍另核。非作者人審與 Owner/Release Manager 對 exact candidate/main SHA、CI、rollback、tag/版本獨立核准後，另明示正式發布才做實際 merge/版本/tag/release 及真回讀。M4 準備可做到候選報告；gate 未滿或未獲批准只交標記限制的候選，不稱正式發布。
 
## 結果、人工參與、停止規則
每項只記 PASS/FAIL/PARTIAL/BLOCKED/NOT_TESTED/N/A及理由、日期/環境、實際 SHA/版本/run或證據位置、預期/實際、責任人角色、權限及下一步；證據去識別，私密內容留在已授權私有環境，公開 repo 不留帳號、Cookie、Token、真人資料/私人 URL。只有當前適用 MUST 和安全守門都過才算該包完成；B10 特例按原規則明示未驗限制後由人決定，不自動 PASS；M2-2、M3、M4 的未授權永不改已驗。
人工僅需：真正新對話並保留首答、實際使用 APP 與回報理解、有需要的本人登入/OAuth/設定/成本或授權決策、真遠端 UAT、合格非作者審查/Owner 發布決策。Agent 承擔查核、程式、測試、文件、對帳、可授權的工具操作；不得索取密碼、驗證碼或憑證，不要求 CLI、全部平台連線、重複註冊。各階段只給一個必要步驟，先不用操作。遇實際缺陷最小修復、重驗受影響 gate；重大 scope/cost/date/authorization 由使用者另議，高風險立即停，同一阻礙兩次無新進展改安全替代，不因目標日期放寬。原11/22與11/29不保證、不得假設背景工作；本輪不新增成本/資源/工作包。
方案確認可接受／調整順序／要求唯讀查核，確認方案不等於執行或部署/發布授權；若同一新訊息明示 M2-2 實際驗收則只執行該包並停。保留 TD-004 長期學習。此次僅正式來源查讀、寫入規劃文件與決策及回讀；無驗收測試、部署、main、release 變更。GitHub 文件提交可能正常觸發既有 CI，不視為本輪驗收。


## 2026-11-17｜方案核准與執行狀態（PLAN_CONFIRMED / A07_AWAITING_FRESH_DIALOGUE）
使用者已明示確認整體方案及授權 M2-2 剩餘驗收，先 A07 再 APP 真人與適用 B10；原方案中的未核准標記為形成時歷史，現僅 M2-2 有實際執行授權。現行只提供 A07 新對話操作：Temporary → Unpersonalized（[最新官方說明](https://help.openai.com/en/articles/8914046-temporary-chat-in-chatgpt)，非個人化不用 memory/custom instructions/plugins；有限安全上下文與工具可用性仍有界線）。首答/環境證據尚未取得，不標驗收通過。只讀原 GitHub 並記錄授權，未執行真人測試或 APP 新操作，不改程式/外部部署/main/release；2/6、M2-2 partial、原 B10 條件及其他獨立授權不變。詳原決策紀錄。


## 2026-11-17｜A07 首答評閱（CONTENT_CORROBORATED / SOURCE_ONLY_PARTIAL）
使用者回報真新非個人化暫時聊天，提供 task-only 首答。評閱真核候選 3adf61ba6ea1afcc3920c7e6eb051886d8e0ff36、main/PR #8、CI 43997739513 / 43730072106 completed/success exact head、三 APP 檔兩版內容及 blob 一致，回覆內容及授權/進度相符。首答同時自述部分先前對話背景，未定是否含本專案，沒有另一對話原始工具/環境證據；不可將內容正確或使用者模式回報視 source-only PASS。A07 PARTIAL 非產品 FAIL；只補原對話仍可得的來源/背景分類證據，不重跑；如原對話已關閉或仍不可隔離，保留 gate 並請使用者決定替代或另行確認先驗 APP 的順序。依本輪條件尚不開始 APP/B10；6包2完成、無新部署/發布。詳原決策。


## 2026-11-17｜原 A07 暫時聊天已關閉（ORIGINAL_SESSION_FOLLOWUP_BLOCKED）
使用者回報原暫時聊天關閉；不要求重做同一測試。原首答與 GitHub 事實核對成果保留，獨立性 PARTIAL 不取消。建議經使用者確認後先完成原 APP UAT/適用 B10，再以不同可驗途徑補 A07，避免整包卡住但不改通過標準。現停在次序決策，未執行 APP/B10或部署發布。詳原決策紀錄。


## 2026-11-17｜修訂提案 ACCEPTANCE-PLAN-006-R1（PROPOSED / NOT_APPROVED / NOT_RUN）
使用者要求重新調整首版 Agent 驗收，合併離線 APP 真人驗收及線上使用驗收、降低人工負擔，維持原訓練目標和安全，先提出方案不提前部署。此為提案，非已核准依賴變更、取消 gate 或 M3/C3/M4 授權；原已確認方案、現行 NEXT_ACTION 和原決策在使用者另外確認之前仍有效。基準 d2ac32105ca93c12abebc253cc402ea84694791a tree 916a02cf3037c973f4bd2427d3554f1ebde512e7；CI 44006773485 completed/success（metadata；本輪沒有讀 raw 或重跑）；原主檔 c91bd899b8ef5525646215137124b31dbec617f2、決策 41ce49d312be409d4ab764df9b30d0a0d3a7367f、本方案原 blob 2b9edc0f1cb2a914ad41661b410c9559286b9f5f、原 APP 規格 7dad2a37313ba8da79480b19565894ba01559f20、START_HERE/AGENTS、C0–C6 442fa4a363b8b65935651e78ad07197970624618、新手 B10 d4727f11e4345f59ed1e6a70d63be953d54d13b6、release checklist 38e3b22b843e5ed8c64b177413a62a8cddaca771。main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57。
 
### R1 不變目標與變更理由
真正產品是教師/研究團隊使用之 Agent，不是示範 APP。維持 TD-005 原八組 MUST、八角色十五技能、六工作包、一合成案例、一零新增成本路線（NT$0）、11/22 管理檢查點及 11/29 候選目標（不保證）、TD-004 長期學習延後、真人倫理與技術風險守門。無新增網站、角色、技能、框架、科學功能、雲 DB、登入或外部專案操作。原 M1/M2-1 已驗證，原 517 tests/真 Chromium 375/1280/CSV、同三 APP blob/離線 ZIP 歷史證據重用；不重跑完成項。獨立性及 B10 的限制不可消失。
變更僅限驗收環境、真人證據共用及工作包依賴：不再把 file:// 真人相容性作首版必要（以線上使用為首版交付面向，須使用者確認不必離線承諾）；原離線包保留，file:// NOT_TESTED / NOT_PROMISED，不得標 PASS 或用 HTTPS 代替證明。若另有離線交付需求、發現獨特本機風險，另議適用測試，不重造 APP。真使用者 UAT 移至 C6 一次完成，不取消 R1–R5 適用工程/安全檢查。原驗收目標保留，明說本機專屬環境覆蓋減少，不稱完全等價。
 
### R1 工作包及依賴（待確認）
| 包 | 目前 | 建議依賴/完成證據 |
|---|---|---|
| M0 | 已確認 | 不重做 |
| 1 M1 | READY_STOP | 原工程證據保留 |
| 2 M2-1 | READY_STOP | 原 APP 及 CI 保留 |
| 3 M2-2 | PARTIAL | A07 實質內容已核、source-only 未證；將真人可用性及適用 B10 部分證據放 C6/必要設定，交付指南先沿用；以實際共用證據回填，A07 必須補足，B10 如原規則明示限制經使用者決定。不得在遞延後即 READY_STOP |
| 4 M3-1 | NOT_AUTHORIZED | 修訂方案核准且另明示 M3-1 後可先進 C0–C2，不要求 M2-2 完成；真目標、免費條款/配額/權限/成本、白名單 artifact、對應 SHA/CI/security、復原方案，以及可編輯 C3 具體授權稿；有未知/危險即停，不外部寫入、部署 |
| 5 M3-2 | NOT_AUTHORIZED | C0–C2 真證據合格，C3 明示准許精確範圍後方可受控部署。若 A07 還 PARTIAL，須在 C3 決策中明確承認此未驗限制且只作同一公開合成案例的受控驗收；A07 殘缺非自動阻止已核 scope/來源/安全都通過的受控試部署，但若涉及錯版、無法讀來源、越權、資料安全或未知寫入一律阻擋。C4/C5 HTTPS/真遠端功能/負測/安全/成本/版本與回退，C6 一次整合真 UAT，啟用另明示核准；不自動升級正式產品或寫入其他專案 |
| 6 M4 | NOT_AUTHORIZED | M2-2 及 M3 必要證據全部滿足、原獨立人審與治理守門、回退/版本證據、Owner 核准，另授權；A07 仍 PARTIAL 則不能把第一版完整驗收/正式發布標完成，最多明示受限候選，不放寬原正式發布條件 |
M2-2 可跨步等待共享證據，不是取消或假完成；總進度 2/6，若 M3-1 實際完成可計該包但不冒稱 M2-2 完成。M3-2 遠端 C6 取證後，逐包獨立審核，任何未滿即保留 BLOCKED/PARTIAL。原先「完成即停」仍適用每次明確授權，M3-1 完成停在 C3，M3-2 停在人審/啟用或 M4 之前，無自動階段授權。A07 來源獨立性未證是證據環境問題，非已證實模型能力缺陷；不以本輪討論或 CI 作補證，不要求重開已關閉暫時聊天/反覆相同測試。可採不同、真可取得來源及隔離佐證的途徑，先確認可用性再要求必要人工；驗收方法不能把同一 Agent 自述當獨立證明。原 11-17 暫時聊天官方說明引用之原始來源內容本輪無可核證原文，不能用其當該次環境獨立性證據；保留實際使用者回報與先前 GitHub corroboration，不主張絕對隔離或已驗政策內容。
 
### R1 唯一一次整合真人使用（預計 C6）
Agent 先以授權工具核 C4/C5：同一 HTTPS URL＋已固定 artifact digest/SHA，真匿名與非部署者、兩個 viewport、完整 R1–R5 正負例及 CSV 內容/版本、白名單/秘密資料檢查、無額外外連或收集、成本與 quota；v1→可辨識且不改學術規則的 v2→已知良好 v1 回退，各自真實 provider/readback/瀏覽器驗證；外部調用不可用則明示 BLOCKED，不把先前 localhost CI 當遠端。完成且回退後穩定在預定可驗收版本，再給使用者一次連結＋當前必要操作；不要求在 v1、v2、回退每階段重做人工矩陣。人類僅以常用瀏覽器開真 HTTPS URL、40/seed1 生成並查看兩組各20、下載 CSV，回報能否使用及是否理解指引/遇到阻礙；可提供合成 CSV 或遮蔽畫面，技術檢查由 Agent 完成。此為一次驗收會話內的核心流程，一步一步引導，非已完成結果。若 Agent 已取得可查遠端正負例與重播/seed/非法輸入/恢復、鍵盤/版面、六欄內容之證據，不令使用者重複矩陣；只有必需項無法代驗才請人補特定操作，缺證不 PASS，不忽略使用者真遇錯誤；只修受影響最小範圍後重驗。合併共享證據指向同一版本/URL/時間/結果，M2-2 交付可用性和 C6 真人 UAT 可引用同一紀錄；B10 另看是否真正新手及真適用帳號/設定/錯誤支線，不捏造新手、付費或錯帳號。若不具適用獨立新手，以原程序記 PARTIAL/NOT_TESTED 限制、使用者明確決定候選揭露及後續補驗，不自動 PASS。C6 之正式啟用核准與一次 UAT 分開，不預設啟用。無正式研究/真人資料/測量精度或動態資料安全全驗 claim。
 
### R1 人力與安全
最少化使用者人工：方案/獨立階段授權與 C3 具體範圍確認、必要本人登入/平台設定（僅實際需要）、一次組合真人 UAT、另需合格非作者審查與 Owner 啟用/正式發布核准。另 A07 缺口如有確實不同驗證途徑，才請必要的人機操作。Agent 負責所有可代辦工程、版本、測試、成本與回讀，不能把使用者當測試工程師，不要求 CLI、付費/新帳號、提交 secrets 或多人權限重配。未知費用/權限/競寫/不明 POST 停下唯讀對帳；不得因改次序擴大權限、減少安全檢查、先 merge main、改 release/付款/建真資源。適用項 N/A 有理由，通過標準仍逐項證據，不以平均成績或測試數當產品驗收。若出現必要缺陷，按已確認範圍最小修復，重大 scope/time/cost/authorization 另議。原日期不保證。
 
### R1 決策及下一步
建議確認以上 R1（包括取消離線相容性首版承諾、A07 未證狀態下只允許另准安全準備/受控部署而非完整通過、共享 UAT 與逐包關閉）。另明示 M3-1 才執行 C0–C2，完成即停；若不同意改依賴，原 006 仍有效。此次只提供修訂方案，不執行實際驗收、APP 重包、平台/帳號設定、C0–C2 實作/成本調查、C3、部署、正式發布或其他專案；不改 source/runtime/workflows/main/release。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK。原主檔只索引待確認提案，原 NEXT_ACTION 保持，寫後回讀與例行 CI 分開。


## 2026-11-17｜證據來源補正
證據更正（2026-11-17，EVIDENCE-PROVENANCE-CORRECTION-007）：此前外部來源閱讀/官方佐證標記缺少可核讀正文，原列 URL 僅參考連結（REFERENCE_LINKS_UNVERIFIED）；相關實讀/官方佐證肯定宣稱撤回。保留一般工程原則及原實際實驗結果，實際採用前另查當前產品規則。詳細見原決策紀錄及能力證據重整覆盤。 暫時聊天原官方閱讀宣稱撤回，不影響原真新對話回報與 source-only PARTIAL。原 R1 仍待確認，不影響既定授權。


## 2026-11-17｜後續明示確認及實際 M3-1 查核
使用者已確認 R1 並授權 C0–C2；前述未確認為形成時狀態，不再有效。C1 BLOCKED/C2 PARTIAL、2/6，M3-1 已授權續補，完成停 C3；A07 source-only 及其他原安全門檻維持。詳[實際查核](2026-11-17-m3-predeployment.md)。長期真任務學習提案仍 PROPOSED，不接管外部專案。


## 2026-11-17｜M3-1 完成固定版本準備，待 C3
原 R1 仍有效。C0-C2 prepared at pinned 6cdd6fe1042505143234623d95eef028a4866e00，C1 本人 Pages UI 證明 disabled/None，C2 同版 CI 44010391221 真 raw 517/517 及原 archive identity；三包完成，M2-2 PARTIAL。C3 具體方案及當前 head/CI/費用/設定再核硬門檻詳[原 M3-1 查核](2026-11-17-m3-predeployment.md)；未授權/未部署、不取消 A07、B10、C6 或 M4，長期提案待確認。
