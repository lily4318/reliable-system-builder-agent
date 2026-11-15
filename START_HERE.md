# START HERE｜網址＋一句任務啟動

當使用者貼上本 Repository URL＋任務時，AI 應直接讀取最新已核實的 `main`、`release/current_release.yaml`、`AGENTS.md`、`config/agent-policy.yaml` 與 `docs/ARCHITECTURE.md`。

## 先找適用技能
使用 config/skill-catalog.json 選按需技能；操作範例見 docs/TEAM_WORKBENCH.md。使用者可說「我想建立網站」「幫我除錯」「繼續」「記住這個做法」「整理經驗」，不需記指令。依 AGENTS.md 的執行模式及 docs/TEAM_WORKBENCH.md「平台原生工作模式」工作：有已授權私人工作區才啟用 SQLite 的 context/handoff/learning/tasks 操作；只有 GitHub 讀寫權時採 REPO_NATIVE，以正式來源、公開案例、原 commit/CI、原工作紀錄作交接；只有唯讀權時明示 READ_ONLY。缺私人工作區不必要求使用者安裝工具，私人資料不得移入公開 repo；只保存實際獲授權且可公開的工程證據。

按任務查 [工程知識索引](knowledge/ENGINEERING_PATTERNS.md)：先選 skill，再按風險取用最相關 EP 卡、原案例及證據。索引不取代正式來源、私人檢索狀態、實際驗收或人審升版。

## 若任務是「訓練／改善／討論方向／接續這個 Agent」

先定位原 Draft PR #8（candidate-skill-team-integration-20261114）的最新 head，閱讀該版本的 [唯一正式訓練主檔](docs/AGENT_CAPABILITY_TRAINING.md) 頂部及 [訓練決策紀錄](docs/training/DECISION_LOG.md)。正式 main/release 與候選訓練分開，不能使用歷史摘要或舊排程取代最新決策，也不能重做已完成工程。

最新 TD-001：使用現有已授權 AI 平台，以實際工作、按需角色與技能、案例記憶、共用工作空間、驗收及覆盤蒸餾為核心。Ollama 和本地模型 runner 保留為選用評測，不是開工前提。沒有獨立子代理功能時可用單 Agent 按角色分工完成真實工作，明確標記實際模式，不能冒稱獨立多 Agent 或能力增益。選擇真正可使用的工具與授權範圍，優先解決實際缺陷，不再重複同類合成任務。除非另有授權，不接管外部專案、不傳私人資料、不呼叫付費 API、不部署。

每次重要討論後依 TD-002 增量保存決策紀錄，區分討論、建議、確認、實作與實際驗收；深入分析可保存 docs/training/reviews/ 並提供索引。更新原主檔及相關原檔，寫前確認 head/blob，寫後讀回及核對 exact CI；失敗明確回報，不另建訓練主檔。

## 若本輪是「協助建置新網站」
先用 `docs/HUMAN_FIRST_WEBSITE_WORKFLOW.md` 和 `src.website_discovery` 問最多 13 個、涵蓋需求的問題；從既有答案預填，先提出完整標示推論／未決的規格草稿，逐項可點選並修改後才由使用者正式確認。**尚未確認的規格不可當成已核准開工或部署授權**。任何需真人自行操作的網站服務設定都必須給逐步 UI 路徑及查核方式，不可只叫使用者完成。

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
