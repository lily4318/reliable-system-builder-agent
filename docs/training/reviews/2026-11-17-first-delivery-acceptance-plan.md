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
