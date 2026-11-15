# TD004-OFFICIAL-01｜HTTP 訊息完整性及持久化寫入的因果邊界

2026-11-15；獨立官方技術單元，非 HackMD 課程章節。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK，主責 Security/security-review；Developer 實作；QA 真實 HTTP 測試。不冒稱獨立子代理或模型權重訓練。

## 1. 閱讀與能力缺口
- IETF [RFC 9110 §8.6](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.6)：長度為 ASCII 十進位數字表示的 octets；合法數字長度可能很大，需防轉型或精度問題。
- IETF [RFC 9112 §6.3](https://www.rfc-editor.org/rfc/rfc9112.html#section-6.3)、[§8](https://www.rfc-editor.org/rfc/rfc9112.html#section-8)、[§9.6](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.6)：訊息邊界、不完整訊息與連線關閉要求；同值重複長度可以拒絕，不能將提前 EOF 當作完整 request。
- Python 3.12 [http.server](https://docs.python.org/3.12/library/http.server.html) 及 [socket.settimeout](https://docs.python.org/3.12/library/socket.html#socket.socket.settimeout)：標準函式庫教學 server 不推薦 production；socket idle I/O timeout 並非整體時限。閱讀上述相關原文段落，不宣稱已讀完整 RFC 所有章節。
- 前置原 478 規格回歸 [CI 43717413326](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43717413326) exact e829d7bd77673fec41fc08535730d9d17ed812b7 job 132822033470 原始 log 243959 chars, 478 tests in 50.079s OK，12 curriculum tests 全 ok，EDITORIAL_BROWSER_PASS。這不是本次 HTTP 缺陷測試。
- 原 editorial_site.py blob e0c553e2e83668e797f5cbc557c3b6a8b7621f34：已有 Host/Origin/CSRF、角色、body cap、duplicate key、receipt/transaction 防護，但 read(size) 取得提前 EOF 的 bytes 直接解析 JSON，將協定完整性誤當內容正確性；int 接受超出協定 grammar 的字串；TE 欄位的 truthiness 不能辨識空值欄位存在。真正有權使用的 authenticated client 仍不可送出不完整請求。

## 2. 深度反思與設計取捨
安全是串聯多個前置條件，不是任一層通過可替代另一層。合法身份/CSRF 只證明通過相應身份關卡，合法 JSON 只證明語法；只有明確 framing 完成才可交業務驗證及 transaction。資料量 cap 不等於完整性；idle timeout 不等於絕對 request deadline 或速率限制。既有未知 POST recovery/receipt 仍必須保留：服務端這次可確定未進入 mutation，不代表任意網路失敗都可重送。
比較 A 只檢 JSON（原缺陷）；B 本機 API 固定長度、strict ASCII digits、限制顯著位數，拒絕任何 TE、先驗完整 bytes、EOF 400/idle 408、關閉連線（採最小相容修復）；C 正式產品採成熟 HTTP server/framework 及可信反向代理（需要另外選型、上線及同層實測）。B 不支援 chunked 等一般完整 HTTP/1.1 所有能力，不將本機拒絕策略冒充通用協定伺服器。沒有外部 proxy chain，未宣稱防禦所有 request smuggling、Slowloris/DoS、TLS、HTTP/2/3 或正式 production 安全。五秒是本地候選預設，由本次 agent 決定、不是使用者正式 SLA。

## 3. 蒸餾與專屬任務
Security owner：先定 framing/ACL/size/timeout 邊界、拒絕與無副作用 oracle；Developer：修原路徑，在解析及 mutation 前拒絕；QA：用已授權本機合成帳號、真 TCP/HTTP、原 actor 唯讀 receipt + workspace 對照。對待未知 POST 依 EP-03；驗收分層依 EP-06。規則寫回原 security-review，知識索引 EP-12 候選，無新角色/技能或 runtime seed。

## 4. 實作、故障及回歸
- 紅測 exact ea58562ad69bdf2435eee1b32dc3810d6d70dbfe [CI 43718703256](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43718703256) job 132825743234 completed/failure，raw log 112483 chars，481 tests in 52.496s，3 failures。實際 incomplete valid JSON、signed CL、empty TE 均 200、receipt observed True、workspace 新寫入，應為 400/False/原 workspace。合法 UTF-8/leading zero 控制組通過；duplicate/combined/非空 TE 原已拒絕，保留測試，不冒稱新修復。
- 以原 src/editorial_site.py 修正、tests/test_editorial_site.py 新四個 test methods，含 5 subcases；完整字節驗證、ASCII decimal 及 significant digits cap、拒絕 TE 欄位存在差異、5s socket idle、close，新增 idle timeout 真連線負例（未半關閉）。程式與測試 blob 4ea0df0425426456cfaca9af380465c9f3f73dfd / 0883fb747f574e0280c1a5a13b4870c03287a366 已遠端逐檔一致回讀。
- 修復 exact 10be998cb877cec8911f83edf61736463f735c9d / [CI 43718746128](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43718746128) job 132826026062，run completed/success；Offline unit tests success。完整 CI 通過；以原始測試日誌為細項證據。
實際日誌摘要：
2026-11-15T13:24:07.5670972Z test_http_framing_complete_utf8_and_leading_zero_length (test_editorial_site.EditorialHTTPTests.test_http_framing_complete_utf8_and_leading_zero_length) ... ok
2026-11-15T13:24:13.4066050Z test_http_framing_idle_timeout_has_no_mutation (test_editorial_site.EditorialHTTPTests.test_http_framing_idle_timeout_has_no_mutation) ... ok
2026-11-15T13:24:14.2403599Z test_http_framing_incomplete_valid_json_has_no_mutation (test_editorial_site.EditorialHTTPTests.test_http_framing_incomplete_valid_json_has_no_mutation) ... ok
2026-11-15T13:24:15.0990357Z test_http_framing_invalid_length_or_transfer_encoding_has_no_mutation (test_editorial_site.EditorialHTTPTests.test_http_framing_invalid_length_or_transfer_encoding_has_no_mutation) ... ok
2026-11-15T13:25:01.4676006Z Ran 482 tests in 58.668s
2026-11-15T13:25:01.4676297Z OK
2026-11-15T13:25:24.1616746Z EDITORIAL-BROWSER: {"status": "EDITORIAL_BROWSER_PASS", "views": [{"status": "PASS", "width": 375, "checks": {"exact_viewport": true, "page_one": true, "page_two": true, "initial_empty": true, "keyboard_focus": true, "real_tab_navigation": true, "wrong_login": true, "lost_ack_pending": true, "reconcile_owner_guard": true, "reconcile_after_relogin": true, "read_only_reconcile": true, "author_create": true, "author_keyboard_field": true, "workspace_no_overflow": true, 
- 成熟度：L2 有來源原理解釋及具體限制分析；L3/L4 受控工程實作及失敗修復有實測支持，候選作業證據，不是獨立模型分數。 L5/L6 未做陌生任務與獨立跨角色完整驗收，仍 pending。

## 5. 遷移與接續
原 src/p21_equipment_site.py blob 723cbd45c6d11792e38aa35732b791679950f7a0 L310–317 仍見 get('Transfer-Encoding') 與 read(n) 後直接 parse_qs；同屬 framing 但編碼為 form-urlencoded。已唯讀定位，尚未實際重現/修復；下一步同一原理在不同 parser 和業務流程真測後才判斷是否應共用守門（避免未證據重構）。正式部署另行核准。
HackMD 章節矩陣 blob 25d164664d834953beea0a1c2cd41f71a017be56 完全未改，BLOCKED_SOURCE，未知分母、無教材單元成熟度。main c8be8c80a326bebd1d9a6abc9ad52e18cc9f7e57 未變、未出正式 release 或外部部署/付費/真個資。本次只增量原 PR #8。

## 6. 第二情境 form-urlencoded 遷移實際證據（NATIVE-HTTP-021）
- 使用者確認接續原 HTTP 單元、設備預約表單，先實際重現再最小修復及無副作用回歸。基準 exact 8ead5fd50edc4e4ec9d02b0a0fa185de558c501f / CI 43718959810 completed/success（run metadata），保留原 482 全綠。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK；Security 主責，Developer 修復，QA 以實際 loopback HTTP + SQLite 資料驗收。補讀 RFC 9112 §6.3 https://www.rfc-editor.org/rfc/rfc9112.html#section-6.3 、Python 3.12 parse_qs https://docs.python.org/3.12/library/urllib.parse.html#urllib.parse.parse_qs；沿原官方單元來源及 EP-03/12。
- 新情境不同於 JSON 文章：合法 URL 編碼前綴在短讀時仍可解析，且業務拒絕本身可持久化 action_attempts。原 p21_equipment_site.py blob 723cbd45c6d11792e38aa35732b791679950f7a0 L310–317。先提交 red-only 測試 exact c682d19fa6e7ece58dbbb20fede872b46f60282b，CI 43719342135/job 132827726515 completed/failure，raw 117759 chars，486 tests in 60.986s，6 failures：reserve/cancel/return 提前 EOF、signed CL、empty TE 各為 (200, False, False)，不完整負向決策為 (409, False, False)，oracle tuple 是 (status, all four tables unchanged, SQLite file bytes unchanged)，預期 (400,True,True)。完整 URL 編碼及重播控制組成功；原已拒絕 duplicate/combined/非空 TE/zero/oversize 不冒稱新修復。red 測試已在獨立 commit 先啟動；其 CI 執行中提交 fix、red 日誌之後回讀，沒有以修改後的測試冒充原版結果。
- 最小修復原 src/p21_equipment_site.py：保留 4096 bytes 上限及原 8 fields、Host/Origin/CSRF、原表單解析/角色/交易/ledger/replay；ASCII decimal grammar、拒絕任何 TE 欄位、顯著位數 cap、讀足宣告 byte count 才解析、5秒 idle timeout（沿原 timeout、範圍移至 Handler）回 408、close connection。原 schema 不變、不做未必要共用模組重構；408 是本次 Agent 的相容性取捨、不是使用者 SLA。5 個新測試方法（原 red 四項 + idle），實際 4 table snapshot 與檔案 bytes 等值，合法 percent encoding/leading zeros/replay/歸還正例。原 src/tests blob 94231c8f5b0f8cff5ec93319a4b3ce362f0c2892 / 63b67a600d486fc719bd003f26966da6bcc27274，fix exact readback 兩份一致。
- 修復 exact a1cf40d0fa5bdca908c057e92f73436ce4c4a50e / [CI 43719406375](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43719406375) job 132828041718，in_progress/none；offline unit tests success。完整原始日誌尚待取得。 不先宣稱完整 CI 成功。
- 角色成熟度：L4 原 JSON 單元保留；本次 form 遷移已實作且真 red，修復驗收尚待 exact CI，不升 L5。 不等於獨立陌生 holdout、模型權重訓練或 L6；設備專屬真人 UAT、正式部署或完整資安審查未做。local HTTP server、idle timeout 非整體 deadline、proxy/HTTP2/3/DoS 未驗。原 [覆盤](reviews/2026-11-15-http-framing.md) 追加此單元，原 EP-12、security-review、test-and-acceptance 增量深化。HackMD 矩陣 blob 25d164664d834953beea0a1c2cd41f71a017be56 不變；main/release/外部專案不修改、不付費或部署。NEXT：先查 exact CI，若失敗先 reconcile，通過再補 L5 證據。

### 6.1 實際綠測回讀（VERIFIED）
NATIVE-HTTP-021 修復後 exact a1cf40d0fa5bdca908c057e92f73436ce4c4a50e / [CI 43719406375](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43719406375) job 132828041718 completed/success，所有列示步驟通過；raw log 245557 chars，487 tests in 63.561s OK，5 新 form framing methods 全 ok（含 6 原 red 情境、idle 408、正例及 replay）；P21-EQUIPMENT-BROWSER PASS actual_browser_dom_events=true, roles=3, stock=10, reserved=0, manual_uat=false；EDITORIAL_BROWSER_PASS 375/1280。四表與 SQLite bytes 無副作用負測通過；保留原正常業務拒絕持久化。L5 受控工程知識遷移證據成立（不同 parser/業務流程，非獨立未見 holdout、L6 或模型能力證明）；原 pending 記錄由本補記接續，不改歷史。
