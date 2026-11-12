# START HERE｜網址＋一句任務啟動

當使用者貼上本 Repository URL＋任務時，AI 應直接讀取最新已核實的 `main`、`release/current_release.yaml`、`AGENTS.md`、`config/agent-policy.yaml` 與 `docs/ARCHITECTURE.md`。

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
