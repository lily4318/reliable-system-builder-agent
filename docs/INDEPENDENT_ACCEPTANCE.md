# v0.1.0 候選版｜隔離式故障復原驗收

## 目標與獨立性界線
此驗收採用 `src/recovery_reconciler.py`、`src/independent_acceptance.py` 和獨立的 `evaluations/acceptance/recovery_cases.json`，**不直接重用**原有 `src/agent_eval.py` 政策決策函式。這是第二條獨立程式／案例路徑，但仍是**公開人工設計案例與自動化驗收，不是第三方驗證、模型獨立盲測或真實遠端 GAS 測試**。

## 可重現的故障注入
- 建立版本 API 成功、不可變內容驗證成功、版本清單仍舊：判定 `VERSION_LIST_LAG`，停止 POST、再次 GET。
- 已出現在版本清單但未部署：判定 `ORPHAN_VERSION_CONFIRMED`；不能盲目建立另一個版本。
- 部署 POST 回應不明：`UNKNOWN_POST_RESULT`，不假定成功或失敗。
- 正確私人部署已出現在清單：`PRIVATE_DEPLOYMENT_PRESENT_NEEDS_UAT`，不代表實際 UI／正式資料核准。
- 權限公開、執行身分錯誤、HEAD 漂移、既有部署被更動、未知競寫、原本資源消失：阻擋。
- 遠端清單缺漏：`READBACK_MISSING`，不得把「未知」當成「零個版本」。
- 所有評測案例只允許 `GET_HEAD`、`GET_VERSIONS`、`GET_DEPLOYMENTS`、`GET_VERSION_CONTENT`、`GET_DEPLOYMENT_DETAIL` 或 `HUMAN_REVIEW`。本工具不會呼叫任何 API。

## 單獨執行
```bash
python -m unittest discover -s tests -v
python -m src.agent_eval evaluate --output output/policy.json
python -m src.independent_acceptance evaluate --output output/recovery-acceptance.json
python -m src.quality_gate check --output output/quality-gate.json
```

## 指標與防止誤判
- **歷史基準**：`evaluations/baselines/v0.1.0-initial.json`。來源是確實成功的 GitHub Actions Run 43203963325：10 個單元測試、22/22 公開政策回歸、18/18 關鍵案例。當時尚無獨立恢復驗收，所以在 baseline 記錄 `null`，不捏造歷史成績。
- **本版門檻**：原有政策案例數與關鍵案例不得退步；獨立恢復案例至少 20 筆、關鍵至少 18 筆，失敗或允許危險動作皆為 0。
- **根因推斷**：提供案例事件和回讀資料，不用故障日誌的 Failure 直接推論「POST 未發生」。
- **案例集可被看到**：所以全綠是公開 regression 的結果，不能推論 Agent 在陌生環境的成功率，也不能視為真正 ML/DL 的泛化證據。
- **正式版本核准**：須人工審查，CI 綠燈僅是必要非充分條件。

## 後續真正獨立驗收
由未修改評測規則的第二位審查者建立封存情境集，並要求用全新環境執行唯讀稽核、真實 UI 操作；有核准與授權後才可以在外部專案驗收。不得使用真人個資或其他專案的私有系統當公開測試材料。
