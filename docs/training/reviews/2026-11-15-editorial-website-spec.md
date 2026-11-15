# WEB-EDITORIAL-01/v0.1｜線上編輯與文章發布管理平台

狀態 PROPOSED / DRAFT_REQUIRES_USER_REVIEW。2026-11-15。紀錄 NATIVE-MATURITY-013-EDITORIAL-SPEC。此文件只是公開合成委託，不是外部真實客戶或已核准施工規格。使用者明示：完整網站工程實戰、不同於設備/報名/報表、提出具體需求/資料/權限/驗收供編輯確認、確認後實作。以下 R01–R13 全為 Agent 預填提案，請使用者逐項接受或修改；不冒稱使用者已回答。任何修改需更新版本與重新確認，確認規格和候選程式寫入授權分開。尚未執行 src.website_review_handoff：未取得本機 export 或使用者實際逐項決策。以原 Git 版本和後續真實審閱作 REPO_NATIVE 接續，不造 local flags。

## 13 題預填規格（依原 intake IDs）
| ID / source question | Agent 提案（待核） | 可觀察驗收 |
|---|---|---|
| R01 purpose | 小型線上刊物；從作者撰稿到審稿、發布、公開閱覽、修訂與下架均可完整操作。 | 同一篇合成文章實際走完 R03，重啟後結果仍在。 |
| R02 audience | 三角色：匿名讀者、作者、編輯。編輯不兼任作者，不另做管理帳號 UI；至少兩個合成作者、一位編輯。 | 匿名僅讀公開版本，A 作者看不到 B 私稿，編輯可審全部已送審稿；服務端負測。 |
| R03 journey | 作者新建草稿→編輯→送審；編輯退回（必填理由）或核准；核准後另行點發布。已發布文可由原作者新建修訂稿，舊公開版本保留直到新版發布。編輯可下架；下架後可由原作者新建修訂重走審核再發布。不設自動核准/定時發布。 | 實際 UI 完成含退回的全流程；核准但尚未發布不可見，新版未發布不改舊內容；下架立即退出公開頁。 |
| R04 pages | 首頁/文章清單、文章閱讀（只有公開版）、登入、作者文章清單/編輯、編輯審稿清單/詳情/發布及下架。公開清單標題/分類搜尋與分頁，每頁20筆；最多固定三個分類（生活、文化、科技）。 | 不登入可搜尋公開文章；找不到、無結果、超頁碼有清楚狀態；匿名網址猜測不泄露草稿。 |
| R05 identity | 合成本機帳號密碼登入、登出，伺服器端 session；密碼加鹽雜湊，session 到期 30 分鐘，HttpOnly/SameSite cookie，POST CSRF、session rotation；只允許 localhost，正式 HTTPS/Secure cookie 另行驗收。帳號由本機 CLI 初始化，無註冊/忘記密碼/第三方登入。 | 錯密碼拒絕、登出舊 session 不可用、過期/無 CSRF/跨來源 POST 拒絕，前端隱藏不能取代伺服器權限。 |
| R06 forms | 文章：標題 1–120 字、分類固定枚舉、內文 1–10000 字（純文字安全呈現，換行保留）；拒絕理由 1–500 字。必填空白、長度與枚舉皆伺服器檢查。不接受附件/任意 HTML/富文本。 | 空白、超長、錯分類拒絕且狀態不變；script 標籤僅文字，不執行。合法繁中保存、重讀一致。 |
| R07 slots | 不需要報名、預約、名額、候補、付款。文章單一未完成修訂，送審後鎖編；退回才可再編輯；同版 optimistic revision guard、重送以 action token 去重，未知結果先唯讀查詢。 | 同版兩個提交只一個有效；過期內容/審核拒絕；相同 token+payload 回原決定，異 payload 拒絕，不重複發布或事件。 |
| R08 notice | 僅站內狀態及退回理由，沒有 Email、簡訊、外部通知、排程。 | 作者登入可見自己最新審稿狀態/退回理由，無任何外部發送。 |
| R09 admin | 編輯後台只能查看已送審及自己可依法管理的文章狀態、核准/退回/發布/下架；不得直接改作者內文、不得刪歷史。作者僅改自己草稿，編輯可讀為審稿所需的 submitted/approved/returned 版本與已發布歷史，不能讀從未送審的新草稿；退回後的新草稿亦不對編輯開放。 | 每個變更均有 actor/時間/文章及版本/前後狀態紀錄；使用直接 HTTP 與 UI 驗證每種拒絕、歷史可回讀。 |
| R10 privacy | 只用合成帳號/文章；不收真實個資、不用追蹤器、不保存密碼明文或 session token 原值在日誌；本機測試資料保留於指定資料夾，測試暫存可清除，普通使用者無硬刪。 | Git diff、log、公開回應無私稿/密碼/憑證，隔離測試備份與還原，清除僅對測試資料且明示。 |
| R11 integrations | 無既有網域或外部系統；提案 Python 3.12 標準庫 HTTP + SQLite + HTML/CSS/JS，與既有 CI 相容；對照 Flask/Django 等後再定 ADR。目標僅原 PR #8 內隔離新範例（例如 src/editorial_site.py、examples/editorial-site/、專屬 tests），不改既有核心除非另有缺陷證據，不另建外部 repo。 | 依 README 於 localhost 啟動，無需 API Key、模型、網路服務；資料重啟持久化、同 SHA CI 與 Git 回讀。 |
| R12 experience | 繁中、簡潔雜誌風、手機優先、鍵盤可操作、可見 focus、label/錯誤狀態；驗收視窗 375 與 1280 px。 | 實際 Chromium DOM 操作，兩尺寸無頁面水平溢出、表單可鍵盤操作、錯誤可見，未宣稱完整 WCAG 認證。 |
| R13 release | MVP 涵蓋以上13項；零額外付費服務、候選本機完整運作，不設定虛構工期；交付源碼、資料初始化/啟動/備份還原/驗收手冊、權限矩陣、架構及回退方案。核准者為本輪使用者，正式外部部署不在範圍。 | 新的隔離 checkout 按指南可啟動；全部必測正反向/真 DOM、同 SHA CI、新對話續作證據；另行真人驗收及上線授權。 |

## 提案資料模型與狀態規則（設計前候選，須審）
- accounts：id、唯一 username、salt/hash、role、active；sessions：token hash、account_id、expiry；無 email/真實姓名。
- articles：id、owner、published_revision_id nullable、version；公開指標只可指向同一 article 的已核准且發布之 immutable revision，不能直接暴露私稿。下架清空公開指標，保留歷史。
- article_revisions：id、article_id、revision_no、title/category/body、status（DRAFT/SUBMITTED/RETURNED/APPROVED/PUBLISHED/SUPERSEDED/WITHDRAWN）、revision counter、review reason、timestamps。只有 DRAFT/RETURNED 可由作者改文（RETURNED 編輯回 DRAFT）；submitted/approved 等內容鎖定；公開指標切換同一交易把舊公開版標 SUPERSEDED，新版 PUBLISHED；下架版 WITHDRAWN，未完成稿不更改，下架後若已有未完成稿，沿該稿繼續而不另創第二份。核准綁定特定稿及版本；不可發布未核准、退回或過期版本，一次只許一份未完成稿。
- action_receipts/effective audit events：actor/action/token/payload digest/receipt、article/revision/state transition/time；所有變更以交易核對 owner、role、state、expected revision；合法重送只回原結果，拒絕不改業務狀態。審稿理由與歷史只向相關作者/編輯顯示，公開搜尋與詳頁只讀 public pointer。禁止全站硬刪、外部發送、公開未審資料。技術型別/索引/API 詳細設計待下一階段核准後提出。

## 核心驗收套件（規格繫結，未執行）
| Gate | 成功 / 拒絕證據 |
|---|---|
| A01 R01/R03/R04/R08 | 真瀏覽器：作者撰稿→送審→編輯退回→作者改稿→核准→明確發布→匿名讀取；新版草稿/approved 不影響舊公開文；新版發布/下架/重新送審發布。 |
| A02 R02/R05/R09/R10 | 至少兩作者、匿名、編輯四個 session 場景；直接路徑/API 越權、偽造角色/actor、草稿外泄、無 token/錯 origin/過期、logout 舊憑據均拒絕。 |
| A03 R06/R07 | 合法繁中字串/邊界；超限、空白、非法分類、XSS、SQL injection 負測；`<script>` 安全作文字呈現；請求大小 cap 及非預期輸入錯誤須安全回應。 |
| A04 R03/R07/R09 | 兩連線同版競寫只允一成功；同 token 重播非重複寫、異 payload 拒絕；故障前後交易/receipt 回讀，未知結果唯讀對帳。 |
| A05 R01/R10/R11/R13 | 新程序重啟持久化、SQLite 備份/還原到新測試路徑、資料與狀態/公開 pointer 一致；不覆寫既有庫或發布歷史。 |
| A06 R04/R12 | 原 Chromium 驗收入口增加不同完整網站實際 DOM 測試，375/1280 viewport、搜尋/分頁/空狀態/鍵盤/錯誤。 |
| A07 R13 | 需求追溯→架構/ADR→DAG工作包→實際程式→unit/integration/browser/security→同 SHA CI/遠端回讀→操作/回復手冊。使用者真人 UAT、真部署、正式發布分開，不得以 CI 代替。 |

## 待使用者審閱與範圍
D1 題目與首版功能，D2 角色/帳號，D3 送審/發布/修訂政策，D4 資料限制/搜尋/通知，D5 候選技術/介面/驗收，D6 獨立寫入範圍（是否授權在原 PR #8 實作；不含 main、Release、外部 repo/帳號、私人資料、付費 API、部署）。全 R01–R13 與 A01–A07 都可修改，D1–D5 經使用者明確完整確認才成施工規格；D6 是單獨授權。維持 TD-001/002；無外部服務或真個資，正式上線另行核准。

## 選題證據及實戰接續
對照 W101–106（研究報名、館舍資訊、志工排班、運動預約、資源目錄/回饋、內部培訓）與既有設備、報表、B003 排班；沒有完整文章編輯審稿發布工作流的舊實作。P22-CASE-001 文件覆核、EP-02 核准版本原理可遷移，但不是同一完整網站。選擇線上刊物而非購物（涉及付款）或另一預約/目錄（題型太近）；公開可見、非盲測。角色 System Lead/project-intake、Architect/requirements-spec；EP-01/02/07 SOURCE_READ 用於草稿/確認/待核政策。後續依任務再讀 EP-03/04/06/09/10 等；不硬套11卡。此次僅完成提案及 Git 文件交接，不宣稱完成程式、真正使用者審閱、CLI、私庫或驗收。下一步只從使用者真實決策與此文件 exact blob 接續，更新同一規格版本/紀錄後才實作；不得自行將 PROPOSED 改為 CONFIRMED。
