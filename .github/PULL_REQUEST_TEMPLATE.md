## 變更與證據
- TASK_DOMAIN：
- Base SHA：
- 去識別化 incident／正式來源：
- 測試與實際結果：

## 安全和品質
- [ ] 無任何憑證、真人個資、原專案私人資料及內部部署 URL
- [ ] 新回歸案例可重現原故障，保有相關反例
- [ ] CI 和 critical safety case 全部通過
- [ ] 不自動更改其他專案、不在本 repo 部署或開放真人收件
- [ ] 人類評審且未將 CI 冒充實際 UI UAT

## 版本與回讀
- main SHA：
- Actions Run：
- BLOCKERS：
- NEXT_ACTION：

## 恢復安全與升版審查
- [ ] 新增或確認版本建立成功但清單延遲的反例，未知 POST 只做 GET
- [ ] `python -m src.independent_acceptance evaluate` 通過，0 個危險操作
- [ ] `python -m src.quality_gate check` 通過，與上版可信基準相比無退步
- [ ] 當前候選版本仍未被自動升為正式版
- [ ] 有可查證的回退基準 SHA 與人類 PR 審核
- [ ] 若需要正式發布，另由人類依 `release/REVIEW_CHECKLIST.md` 審查和核准

## Evidence-based continual improvement review
- [ ] Base main SHA 與候選 PR SHA 經實際回讀，不直接 push main。
- [ ] 標註採人類 reviewer、原專案有效證據和去識別化摘要；公共附件僅 synthetic。
- [ ] 保留測試不在公開 repo / Actions artifacts；holdout SHA、候選 commit、人類審核分離已確認（如有真實保留測試）。
- [ ] Baseline/candidate 用相同 label SHA；沒有真實樣本不宣稱 real-world improvement。
- [ ] `verify` CI、22 policy、21 recovery、feedback synthetic 評測皆通過。
- [ ] false-completion、unsafe-mutation 都為 0；有任何未知就標為 BLOCKED。
- [ ] 與正式 release 隔離，不做自動合併、發 Tag、部署或修改其他專案。

## Outcome-label contract review（PR #1 候選修正）
- [ ] `label_success_fraction_known` 是標註資料分布，非 Agent 實際成功率。
- [ ] 無實際版本綁定執行軌跡時 `agent_verified_task_success_rate` 必須為 `null`。
- [ ] 真實 unknown `verified=false`、reviewer 仍必要，且不能 `REPORT_VERIFIED_COMPLETE`。
- [ ] 實際 success 須遠端／UI 原始證據；不因 CI Success 自動核准。
