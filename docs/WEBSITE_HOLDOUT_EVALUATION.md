# Agent 陌生網站需求：私人未見題與雙人盲態前後比較（Draft PR #7）

> 此文件是 **Agent 能力驗證工具與執行程序**，不是已觀察到的模型訓練成效。所有公開 CI 測試資料都是合成。尚未有已核准、可驗證的模型 runner，未建置真正獨立的私人 holdout，也未收集真正的人工語意評分。**不得把公開 W101–W106 當成未見案例。**

## 目標與五個人工評分構面

針對**同一批真正未見的網站需求**，在相同模型、runner 和資源預算下，對改善前後的 Agent 產出進行逐題配對。每個輸出由兩位**互不看到對方分數、也不知道哪個版本**的獨立審查者評 0–4 分。

| 構面（JSON 欄位） | 評閱重點 | 0 分／2 分／4 分示意 |
|---|---|---|
| `explicit_requirements` | 使用者 13 題答覆、優先序、否定句與跨輪更正有無正確保留 | 0：明顯錯誤／逆向；2：主要流程有但有缺漏；4：完整保留且標記來源 |
| `reasonable_inferences` | 有無提出合理遺漏需求，亦不加入使用者明確不需要的功能 | 0：過度推導或漏掉關鍵；2：部分合理；4：必要推導皆合理且個別標待核 |
| `architecture_design` | 權責、資料流、權限、資料保存、例外與部署／測試界線是否可行 | 0：不可行或危險；2：能描述元件但關鍵選擇未交代；4：有合理權衡、介面與驗證 |
| `specification_completeness` | 頁面、功能與非功能、資料欄位、角色、測試、MVP、運維是否足夠 | 0：只是摘要；2：章節有但多處空泛；4：具體、可驗收且缺漏有清楚待核 |
| `editable_confirmation` | 每項推導可接受／修改／不採用、可編輯文字，選擇不自動送出或核准 | 0：選完即送或不能修改；2：只部分能編輯；4：所有項目可選可改可取消再確認 |

1 與 3 分介於相鄰錨點之間。每個構面必須填寫至少 12 字的**具體證據／判斷理由**，不可只填「好」或「通過」。若兩人同一構面分數差距 **≥2**，需由第三位、不是原兩位審查者的人提供仲裁及理由，否則比較器拒絕輸出完成報告。

## 分工與資料隔離：不能讓 Agent 接觸測驗解答

- **案例作者（獨立於 Agent Prompt／評分器作者）**：設計至少五個與 W101–W106 不同、模型前後版本均未見過的新網站需求；至少包含真實世界常見的規格矛盾、否定句、模糊授權、跨對話更正、資料及管理權限、可編輯確認。避免使用真人個資或保密來源。作者只在受限的私人位置保存案例正文、13 題回答、人工預期與版本。公開 Repo 不能保存案例文字或標準答案。
- **執行者**：只有在另行確認模型服務、runner、執行目的、工具權限與費用授權後，才可把**同一案例**交給改善前後兩個不同 Agent 版本。在隔離環境保存完整原始輸出及執行紀錄；不要在 GitHub Actions 加 API Key、也不要使用公開 CI 執行真正模型。
- **兩位評閱者**：獲取只含模糊代碼與規格全文的私人評分包，看不到 before／after、Agent 版本、模型設定及其他評閱者分數。不可將合成測試文字誤認為模型真實輸出。
- **仲裁者**：只處理兩人差距 ≥2 的特定構面，須不同於原兩位審查者。
- **對帳者**：在所有盲態評分完成並鎖定之後，才回讀私人版本對照表、內容 SHA-256、病例承諾 SHA-256 與版本配對，計算差異。不宣稱 SHA 可單獨證明供應商真正執行模型。

## 人工作業 Step by Step（不用建立 GitHub Secret）

1. 確認私人工作目錄，例如個人電腦的 `/secure/research-agent-eval/`（僅**示意路徑**；請選有適當存取控制的位置）。**不要**在本 Agent Repo 或公開 Actions artifact 中建立這個資料夾。確認沒有被 Git、同步或公開分享。
2. 請未參與 Agent Prompt 開發的案例作者，把 5 項以上新案例輸入 `cases.json`，結構如下。所有 13 題欄位必須出現；尚無答案填 `null`，不得推定：
   ```json
   {"schema_version":1,"kind":"independent_private_website_cases","cases":[
     {"id":"H001","brief":"這裡填未公開的完整陌生網站需求，至少 25 個字",
      "answers":{"purpose":"...","audience":"...","journey":"...","pages":"...",
       "identity":"...","forms":"...","slots":"...","notice":"...",
       "admin":"...","privacy":"...","integrations":"...",
       "experience":"...","release":"..."}}
   ]}
   ```
   上例只顯示**格式**，不是實際 holdout 題目；需要至少五題 H001…H005。
3. 使用 `python -m src.website_holdout_compare seal --cases /secure/research-agent-eval/cases.json --output /secure/research-agent-eval/manifest.json`，只產生私人案例 ID 與 SHA-256 承諾，**不將題目與回答放入 manifest**。檢查輸出 `case_count>=5`；若已有同名檔，會停止而非覆寫。
4. 真正取得**已授權 Agent runner** 後，固定相同模型、runner 與資源預算。先記改善前 Agent 原始碼 SHA、Prompt SHA，再記改善後 Agent 原始碼 SHA、Prompt SHA；兩個 Agent 版本必須不同。對同一批 H 題逐項實跑，讓每個版本分別提交 JSON 完整規格書。保留私人原始輸出與平台授權／執行紀錄。若這一步未取得授權，**停止於第 3 步**，不得人工填假輸出冒稱模型成功。
5. 將每份規格寫成 `specifications/<不含版本資訊的模糊 ID>.json`，建立私人 `bundle.json`：
   ```json
   {"schema_version":1,"kind":"externally_supplied_website_outputs_unverified",
    "official_model_execution_verified":false,
    "profiles":{
      "before":{"agent_sha":"40位 Git commit SHA","prompt_sha":"64位 Prompt SHA256",
                "model_id":"實際模型 ID（目前僅自述）",
                "runner_id":"實際 runner 版本（目前僅自述）",
                "resource_budget":"相同資源上限"},
      "after":{"agent_sha":"另個40位 SHA","prompt_sha":"64位 SHA256",
               "model_id":"與 before 相同","runner_id":"與 before 相同",
               "resource_budget":"與 before 相同"}},
    "outputs":[
      {"id":"OPAQUEID001X98765","case_id":"H001","phase":"before",
       "case_sha256":"manifest 中該題 SHA256",
       "path":"specifications/OPAQUEID001X98765.json",
       "sha256":"實際完整規格 JSON 檔 SHA256"}
    ]}
   ```
   每題**兩個**版本、各一份輸出，輸出 ID 必須不含 before/after 等暗示。JSON 中完整內容不能包含「已核准部署」等錯誤聲稱。只會比較規格書，不執行任何規格附帶的程式。
6. 先由對帳者在私人環境產出不含 before／after、模型版本和 runner 的**盲態評分包**，只交給審查者模糊 ID 和規格全文：
   ```bash
   python -m src.website_holdout_compare blind \\
     --manifest /secure/research-agent-eval/manifest.json \\
     --bundle /secure/research-agent-eval/bundle.json \\
     --workspace /secure/research-agent-eval/ \\
     --output /secure/research-agent-eval/blind-review-packet.json
   ```
   對帳者應另外核查規格全文未自行透露版本，並防止評閱者接觸私人版本對照表。請兩位審查者獨立閱讀隱藏版本的規格書，以 `ratings` 填入五構面 0–4 分和每項判斷理由；兩人不可彼此看見分數。私人 `reviews.json` 範例：
   ```json
   {"schema_version":1,"kind":"independent_blinded_human_website_reviews",
    "model_or_agent_run_verified":false,"adjudications":[],
    "ratings":[
      {"output_id":"OPAQUEID001X98765","reviewer_id":"REVIEWERONE000001",
       "scores":{"explicit_requirements":2,"reasonable_inferences":2,
         "architecture_design":2,"specification_completeness":2,
         "editable_confirmation":2},
       "evidence":{"explicit_requirements":"逐項保留回答的實際理由（至少12字）",
         "reasonable_inferences":"推導是否符合明示範圍的具體理由（至少12字）",
         "architecture_design":"資料流和權限是否合理的具體理由（至少12字）",
         "specification_completeness":"缺漏欄位與測試範圍的具體理由（至少12字）",
         "editable_confirmation":"選擇後修改及確認流程的具體理由（至少12字）"}}
    ]}
   ```
   每一份輸出需要兩位不同審查者。遇分歧過大時，以 `adjudications` 加入第三位審查者的 `output_id`、`dimension`、`adjudicator_id`、`score`、`reason`；**沒有仲裁時工具拒絕完成比較**。
7. 在所有評分完成後，再由對帳者執行離線配對比較：
   ```bash
   python -m src.website_holdout_compare compare \
     --manifest /secure/research-agent-eval/manifest.json \
     --bundle /secure/research-agent-eval/bundle.json \
     --reviews /secure/research-agent-eval/reviews.json \
     --workspace /secure/research-agent-eval/ \
     --output /secure/research-agent-eval/comparison.json
   ```
   檢查是否對齊每題、SHA、模型／runner／資源預算、評審數、仲裁結果，最後才讀每題配對差與五構面平均差。輸出不覆寫、無實際網路請求、也不會送出任何網站規格的確認按鈕。
8. **人工判定是否真的提升**：比較器即使印出正向數字也只能是「依輸入的人工評分計算差異」，不能自動證明真實模型、案例獨立或能力提升。獨立審查者需另外核對 runner 的真實執行證據、盲態是否維持、案例是否未污染、評分一致性、實際規格與編輯／送出 UI UAT，才可作具體能力結論。

## 自動檢查與負測

```bash
python -m src.website_holdout_compare protocol
python -m unittest discover -s tests -v
python -m src.quality_gate check
```

公開 CI 只會執行**合成資料**：包括 5 個生成的私人案例格式假資料、兩組「模型不存在」的假輸出、假人工分數與期望 +1 的算術結果，測試缺一個版本、版本相同、模型/runner/資源不一致、雜湊破壞、非法路徑、雙評審不足、重複 ID、分數不合法、虛構模型認證、第三人仲裁缺漏、不可編輯或點選即送出等拒絕情境。合成比較中的任何「提升」數字 **不是** 實際 Agent 成績。

## 本輪授權與效力

目前 `main` 及 PR #7 的檔案中沒有可證實可用的 Agent runner；GitHub 的環境／變數列表也無法透過此連線核實。因此本輪**不呼叫 API、不使用 API Key、不啟動付費模型、不提供任何實際未見案例或真實分數**。在取得獨立授權與可信執行紀錄前，報告固定為：

- `actual_model_or_agent_execution_verified=false`
- `sealed_holdout_independence_verified=false`
- `model_capability_improvement_verified=false`
- `human_semantic_truth_independently_verified_by_software=false`
- `releases_or_live_websites_authorized=false`

人類選項確認是編輯後文字確認，不代表取得 GitHub 寫入、網站部署、個資收件、第三方倫理或營運核准。
