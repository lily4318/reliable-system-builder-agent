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
