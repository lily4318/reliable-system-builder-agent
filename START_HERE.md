# START HERE｜網址＋一句任務啟動

當使用者貼上本 Repository URL＋任務時，AI 應直接讀取最新已核實的 `main`、`release/current_release.yaml`、`AGENTS.md`、`config/agent-policy.yaml` 與 `docs/ARCHITECTURE.md`。

## 先找適用技能
使用 config/skill-catalog.json 選按需技能；操作範例見 docs/TEAM_WORKBENCH.md。使用者可說「我想建立網站」「幫我除錯」「繼續」「記住這個做法」「整理經驗」，不需記指令。依 AGENTS.md 的執行模式及 docs/TEAM_WORKBENCH.md「平台原生工作模式」工作：有已授權私人工作區才啟用 SQLite 的 context/handoff/learning/tasks 操作；只有 GitHub 讀寫權時採 REPO_NATIVE，以正式來源、公開案例、原 commit/CI、原工作紀錄作交接；只有唯讀權時明示 READ_ONLY。缺私人工作區不必要求使用者安裝工具，私人資料不得移入公開 repo；只保存實際獲授權且可公開的工程證據。

按任務查 [工程知識索引](knowledge/ENGINEERING_PATTERNS.md)：先選 skill，再按風險取用最相關 EP 卡、原案例及證據。索引不取代正式來源、私人檢索狀態、實際驗收或人審升版。

## 若任務是「訓練／改善／討論方向／接續這個 Agent」

**每次先讀 [核心訓練準則](docs/training/CORE_TRAINING_PRINCIPLES.md)；** 以使用者脈絡、專業分工、共用記憶、真實工作、回饋蒸餾及跨任務成效決定本輪工作，不以管理或單一示範交付取代專業能力提升。此為長期原則，仍以最新主檔與決策確定當前工作。

先定位原 Draft PR #8（candidate-skill-team-integration-20261114）的最新 head，閱讀該版本的 [唯一正式訓練主檔](docs/AGENT_CAPABILITY_TRAINING.md) 頂部及 [訓練決策紀錄](docs/training/DECISION_LOG.md)。正式 main/release 與候選訓練分開，不能使用歷史摘要或舊排程取代最新決策，也不能重做已完成工程。

最新 TD-001：使用現有已授權 AI 平台，以實際工作、按需角色與技能、案例記憶、共用工作空間、驗收及覆盤蒸餾為核心。Ollama 和本地模型 runner 保留為選用評測，不是開工前提。沒有獨立子代理功能時可用單 Agent 按角色分工完成真實工作，明確標記實際模式，不能冒稱獨立多 Agent 或能力增益。選擇真正可使用的工具與授權範圍，優先解決實際缺陷，不再重複同類合成任務。除非另有授權，不接管外部專案、不傳私人資料、不呼叫付費 API、不部署。

已確認 TD-004（原 TP-007）：專業分工式深度能力習得。教材完整覆蓋由團隊負責、各單元有唯一主責專家、必要共通知識及交接；依 AGENTS.md 七階段與 L0–L6 真實證據驗收。先確認可讀教材與章節矩陣，不假稱讀完或同一知識重複學習。保留既有角色、工程及授權門檻。

已確認 TD-005-R2（2026-11-17）：學術研究、實驗及教學專用；**專業能力提升最高優先，解除首版剩餘驗收對教材及真任務雙軌的阻塞**。先依最新主檔 P0/P1 與八角色缺口排序；交付 3/6、未驗及安全守門保留，Pages 依原授權停用、保留分支、不推 v2。PM 管範圍、工作包、時程與停止；真外部任務、部署、正式發布各自另授權。

## TP-010｜開工與回饋閉環（已確認）

開工先實讀當前有效主檔與決策（外部專案另讀原正式規格），核目標、授權、來源版本、已完成與阻礙；依 catalog 讀必要角色及 SKILL，依風險查 1–3 相關 EP 或明示無相符案例。給最少必要的讀取、採用或不適用及下一可驗成果證據。未證工具實際存在及可達性前不得承諾操作；個別阻礙只停相關工作，沿 PM 原兩次無新進展停點，不重建任務池。 私人工作台有授權才用；無私人位置則如實回報未持久化。R2 專業訓練不受首版餘驗收阻塞。明示回饋分類後存原權責位置、回讀，不另建主檔。

每次重要討論後依 TD-002 增量保存決策紀錄，區分討論、建議、確認、實作與實際驗收；深入分析可保存 docs/training/reviews/ 並提供索引。更新原主檔及相關原檔，寫前確認 head/blob，寫後讀回及核對 exact CI；失敗明確回報，不另建訓練主檔。

## 新版預設入口

在目前 Draft PR #8 的候選版本，首次使用直接採用[網站與預約交付](docs/WEBSITE_BOOKING_DELIVERY.md)。可說「做網站」「接預約」「繼續」或「逐步查看」。Agent 由此讀已確認規格與目前進度，先做當前可執行且已授權的步驟。需要本人操作時只給當下可驗步驟。

新專案可在已授權的私人位置使用 `python -m src.delivery_routes init --workspace <新路徑> --label <專案名稱>` 一次準備工作台、任務與學習紀錄。已知專案沿原記錄接續。只有原專案 repo 可用時沿用 REPO_NATIVE。正式發布狀態以 `release/current_release.yaml` 為準。

## 若本輪是「協助建置新網站」
由 PM 按 TD-005 與使用者確認一頁交付約定（依規模簡化）；與既有訪談/規格確認合併，不重問已知資訊，不以 PM 取代正式規格或授權。先用 `docs/HUMAN_FIRST_WEBSITE_WORKFLOW.md` 和 `src.website_discovery` 問最多 13 個、涵蓋需求的問題；從既有答案預填，先提出完整標示推論／未決的規格草稿，逐項可點選並修改後才由使用者正式確認。**尚未確認的規格不可當成已核准開工或部署授權**。任何需真人自行操作的網站服務設定都必須給逐步 UI 路徑及查核方式，不可只叫使用者完成。

已從本機訪談 UI 匯出 `local_reviewed_website_draft` 時，可按「產生下一階段交接預覽」或使用 `src.website_review_handoff` 唯讀核對與整併明示需求/審閱後文字/拒絕/未決。詳 [13題操作指南](docs/WEBSITE_INTAKE_UI.md)。下一技能 requirements-spec 仍須完成語意/驗收整合及真人整份規格確認；hash 及本機文字確認不授權設計施工、寫入或部署。不要求安裝本地模型。

## 若使用者缺帳號、連接或設定（TD-003，候選）
預設使用者完全新手。讀 [完全新手引導](docs/BEGINNER_ACCOUNT_ONBOARDING.md)，先按實際需求/選型與工具狀態決定必要服務，使用 src.account_onboarding 或按同契約逐步帶領官方註冊、本人驗證、ChatGPT 連接、真唯讀核對、費用/權限/錯誤處理。已有帳號與連接跳過，使用者只負責不可代行的安全操作；沒有支援工具就誠實提出替代，不要求安裝本機模型或四平台全連。帳號設定不授權外部施工/部署；任何變動另核範圍。

## 若本輪是「評測 Agent 真正的建站能力」
此節只適用獨立前後測／盲測，不限制平台原生的日常任務。先檢查有沒有已授權的執行方式及可追溯證據（本地 runner 非必要）。沒有適用證據的話，按 `docs/WEBSITE_HOLDOUT_EVALUATION.md` 建立私人案例 SHA 承諾、雙人盲態評分、同條件前後比較的**離線契約**，仍可使用既有平台實際工作但不可當獨立盲測成績；不可把公開六題、合成增分或自述模型 ID 當成真正 LLM 成績。盲態評審只拿模糊 ID 和規格，不取得版本對應表；沒有明確模型與資料授權不啟用 API 或私人題庫傳輸。

## 作業契約
1. **先定位目標專案**的正式規格、最新決策、原始碼、版本、部署及進度。公開 Agent 規則不能替代原專案真正的正式來源。
2. 從 `.github/agents/` 選擇必要專家；如果平台沒有子代理工具，不得聲稱已實際呼叫。
3. 把權限分成唯讀、程式寫入、CI、同步、建立版本、部署、UI UAT、正式啟用；未授權的維持關閉。
4. 比對目前已完成、部分完成、阻塞，不要因聊天切換或 Actions failure 就從頭重做。
5. 未知 POST 結果、部分寫入、競寫時轉為 `READ_ONLY_RECONCILE`，禁止盲目重送。
6. 只做最小增量修改，執行測試、CI 及必要的遠端完整回讀；不要以模擬輸出冒充實際部署。
7. 可泛化故障須先去識別化，新增回歸案例與 PR；不自行更新正式版或外部專案。
8. 回報 `SOURCE_SHA / COMPLETED / TESTS / REMOTE_VERIFY / BLOCKERS / NEXT_ACTION / WRITE_OWNER / SYNC_STATUS`。

## 範例
> https://github.com/lily4318/reliable-system-builder-agent 請唯讀分析我的 GitHub Actions 失敗原因。
> https://github.com/lily4318/reliable-system-builder-agent 幫我規劃 GAS 版本化部署與私人 UI 驗收。

**限制**：分享網址不等於在所有 AI 平台自動載入 Skill、建立持久記憶或取得執行權限；請在使用的 AI／專案正式持久指令中明確引用本 repo。
