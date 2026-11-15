# Developer / QA｜動態研究資料及一致快照（2026-11-16）

本單元是獨立官方技術原理與自寫合成 lab，不是指定教材閱讀完成或原產品修改。主責 Developer，QA 設計明確預期，Architect/ Security 提供既有交易/權限限制；同一 Agent 角色分工，非獨立子代理或盲評。

## 閱讀、原理與取捨
- Python sqlite3 官方交易控制：https://docs.python.org/3/library/sqlite3.html ；確認明示 BEGIN 與提交/回退的邊界；WAL 讀交易依同一快照，不能以兩個獨立自動提交 SELECT 當一致性保證。實際以 Python 3.13.5 SQLite 3.46.1 測試，而非聲稱已驗新版文件所有行為。
- Python csv 官方 writer/reader：https://docs.python.org/3/library/csv.html ；None 預設轉空字串不可逆，需欄位語意；以固定欄名、明示 missing、UTF-8、標準 quoting 及獨立於 writer 的 reader 對照，不能從行數推論資料正確。
- OWASP CSV Injection：https://community.owasp.org/attacks/CSV_Injection 及 https://wstg.owasp.org/latest/4-Web_Application_Security_Testing/07-Injection/21-CSV_Injection/ ；正常 CSV quoting 不等同阻止公式解讀，客戶端行為不同。本 lab 選機器交換格式 note_encoded = 固定 text: 前綴 + JSON 字串，無損可逆、不靜默改原資料；非通用試算表安全保證，未測真 Excel。不選直接輸出 free text 或以 0 填缺失。真正研究者須確認字典、缺失值及統計用途。

## 原證據與不同缺口
靜態研究方法 APP 已測 browser CSV；scope lab 已測 study/actor 越權和撤銷；EP-06/11/13 有資料交易、負向 oracle 與 DB 證據。此輪不重做，訓練「合法動態更新→交易及事件→版本化 CSV」；R1 固定字典 v1、revision CAS；R2 Pddd ID、0–100 整數或 null、字串 note、批次 1–100；R3 同批唯一 ID、失敗原三表不變；R4 CSV 固定欄位順序、ID 排序、missing/observed 與可逆文字；R5 同 revision 重複匯出 bytes 一致，交錯寫入不混合版本。上述規格為合成 lab 自行選定，不代表使用者研究規格。

## 實作與實測
[獨立可重現程式](test_research_data.py) SHA256 2b544ec46ede697c395a1ec3a85331cdc18d96fa60e58235c72e482130e993c4，Git blob 59d95f775a05913b8e6f1632be45189eef7cfdd6。
- Python 3.13.5 / SQLite 3.46.1；LAB_MODE=unsafe python docs/training/reviews/test_research_data.py exit 1，10 methods、8 failures、0.112s：interleaved snapshot, late failure, duplicate batch, bool True/False, formula prefix, missing/zero, schema/revision。
- python docs/training/reviews/test_research_data.py exit 0，10/10，0.113s。其餘正反測含實際更新、固定排序、資料版本、UTF-8/引號/換行、batch bounds、unknown fields；負例比 meta/records/events 三表。真正 WAL 兩連線交錯：讀 revision 1 後第二連線提交 revision 2/score 20；舊對照讀到 revision 1/score 20，strict 固定 revision 1/score 10，下一次 export revision 2/score 20。對照為刻意不安全自行編寫，并非正式程式漏洞。

## 蒸餾、交接、限制
增量至原 implement-feature、test-and-acceptance；交接需求須明示字典/版本、missing、更新語意、交換格式、測試 oracle 與風險。L3 受控實作證據；自寫對照 red/green 不證明獨立模型進步、L4 真產品修復或 L5/L6。未執行完整指定教材七階段；未證固定 v1 之外 schema 變更、空資料版本 manifest、歷史快照保存、大資料與跨程序競寫、HTTP/身分、真試算表及正式資料。原學術 APP 不變。後續依必要能力與交接訓練，不提前真人驗收、部署或發布。
