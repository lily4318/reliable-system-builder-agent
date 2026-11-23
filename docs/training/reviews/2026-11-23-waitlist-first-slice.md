# 候補遞補第一段

使用者確認五項專業與交付目標後，授權以合成資料完成第一段跨層實作及正反測，暫不部署。實驗設定為每場一席，依排入序遞補資格合格者，同序以預約 ID 排定，資格是已給定的測試值。

| 原教材 | 本次實讀及採用 |
| --- | --- |
| [C# 5.3.15 介面](https://hackmd.io/@johnsonnote/csharp_vsc_oop_interface) | 從介面與實作分離及紙箱範例，蒸餾出 Controller 依賴取消與遞補結果契約。用型別區分查無、狀態衝突與完成。 |
| [MVC 4.3.5 完整專案範本](https://hackmd.io/@johnsonnote/vscode_template_full) | 讀 CLI 建立、Models、Program 依賴注入和 Controller 設定。用可直接建置的 Web SDK 專案重現入口、注入及持久化分工。 |
| [SQL 3.4.6 Transaction](https://hackmd.io/@johnsonnote/sqlds_sql_transaction) | 明確交易、提交、回滾與隔離。用 SQLite 寫入交易先取得寫權，再把取消、遞補、回執作為同一工作單元。SQL Server 的巢狀交易及鎖語義需另驗。 |

實際讀到授權備份的 Markdown 文字與程式片段約 7,230、42,332、26,020 字元。附圖、引用與來源版本尚待獨立核對。原教材矩陣成熟度待正式驗收。

ASP.NET Core MVC POST `/bookings/{id}/cancel` 進入型別化介面，資料層用有條件的參數化 SQL、交易和每場唯一確認席次索引。取消回執讓重送回傳當時遞補結果，即使無人遞補也可辨識重送。[專案與測試](../../../examples/dotnet-waitlist/)

驗證方法為先建置 `dotnet build examples/dotnet-waitlist/Waitlist.csproj`，再執行 `python examples/dotnet-waitlist/verify_waitlist.py`。合成案例涵蓋按序、同序取 ID、跳過不合格、無合格者、無效或非確認預約、同筆取消併發與在回執寫入處觸發回滾。Windows SDK 9.0.200 實際編譯零警告零錯誤，限制環境回送 HTTP 回報 WinError 10013，HTTP 以候選 CI 驗證。範圍是合成資料庫和本機 MVC 入口，正式資格覆核、後台登入、外部通知、部署及獨立能力驗收皆待各自驗證。

[CI 45204122916](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/45204122916) job 137795101306 原始日誌核對：實作提交 `ffdb3d18d3f18ea22b3af4f46d0280f031f30a01` 與 PR merge checkout 的檔案差異為零。.NET 10 建置後真 HTTP／SQLite 五項全過，既有 602 項測試及品質守門通過。Windows .NET 9 直接呼叫控制器與 SQLite 的補充測試通過，HTTP 連線在該環境受限。三節教材正文的文字指紋增量記入原矩陣，合計 26 項文字可讀、137 未讀、13 缺件，三節維持 L0，附圖、原 SQL Server 及獨立能力驗收待驗。
