# TD004-OFFICIAL-02 / NATIVE-PG-022｜PostgreSQL RLS、交易與 migration 架構原生驗收

日期 2026-11-15；Architect / architecture-design 主責，Security 權限、Developer SQL、QA 原生查詢與故障驗收。REPO_NATIVE / SINGLE_AGENT_ROLE_WORK。非 HackMD 教材、非獨立子代理、非正式上線。使用者授權新獨立單元，不得建立付費資源或外部部署。

## 官方來源與學習範圍
- PostgreSQL 16 [RLS](https://www.postgresql.org/docs/16/ddl-rowsecurity.html)、17 [CREATE POLICY](https://www.postgresql.org/docs/17/sql-createpolicy.html)、16 [CREATE VIEW](https://www.postgresql.org/docs/16/sql-createview.html)：GRANT / policy、USING / WITH CHECK、FORCE、owner/superuser/BYPASSRLS、view invoker semantics。
- PostgreSQL 16 [transaction isolation](https://www.postgresql.org/docs/16/transaction-iso.html)、17 [transaction isolation](https://www.postgresql.org/docs/17/transaction-iso.html)：Read Committed 每 statement snapshot，等待競寫後重查條件；row lock 連結同一 owner 的決策，全庫不等於 Serializable；較嚴隔離或 deadlock 可能要求重跑完整 transaction，未知 commit 仍先 read-only reconcile EP-03。
- PostgreSQL 16 [ALTER TABLE](https://www.postgresql.org/docs/16/sql-altertable.html)：NOT VALID 可先限制新資料，但既有資料須 VALIDATE；強鎖/掃描與維護窗取捨。這個小型例刻意在同一 transaction 內 ADD/VALIDATE，不宣稱大型資料表線上無鎖。
- Supabase [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security)、[Securing API](https://supabase.com/docs/guides/api/securing-your-api)、[Migrations](https://supabase.com/docs/guides/deployment/database-migrations)。明確 GRANT + RLS、auth.uid() 需可信 JWT，auth.role 不取代 TO；user_metadata 可由使用者修改，不作業務授權；service role/secret 不進瀏覽器；SECURITY DEFINER 引入權限升級面，Function execute 額外核對。Supabase skill 已讀；changelog.md fetch 回 400 unsupported markdown，改讀[官方 HTML changelog](https://supabase.com/changelog)及[Data API 曝露 breaking change](https://supabase.com/changelog/45329-breaking-change-tables-not-exposed-to-data-and-graphql-api-automatically)：2026-04-28 公告、2026-10-30 全專案新 table opt-in 時程，以實際 project grants/settings 為準；不假設既有物件權限已撤回。另見 self-hosted PG15→17 公告，不把本 lab PG16/17 文件與任意 Supabase 版本混為一談。
- [GitHub Ubuntu runner image](https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md) 顯示 PG16 預裝。實際版本以 CI 的 PG-ARCH-ENGINE marker 為準；本工作容器無 postgres/psql/initdb，採原候選 CI 自帶 engine；不新增雲服務/付費 API、未使用 Supabase MCP 對真實 account 作 SQL，也沒有 supabase CLI migration 或 advisors，因為這不是 Supabase 專案。

## 需求與真缺口
基準 bba46fedcb7733b2f090c694123f5cb5c0fa4916 / CI 43719636689 success run metadata；原 487 tests 已驗收。原 tree 沒有 SQL 檔或 native Postgres tests，CLOUD-D 規格有 RLS/grants/transaction/migration 但沒有引擎實作。不是聲稱實際 Supabase production 漏洞。選擇一個新合成案例：兩個獨立 owner 的 drafts/stock/receipts；每 owner 10 個名額（不是兩 owner 共用庫存）；會員可讀自己的資料及新增/編輯自己的草稿，不可改 owner/id、庫存及 receipt；匿名無表權限；trusted writer 獨立角色執行 reserve。操作 token 以 owner 為 namespace，same owner/token/qty 重播原決策、payload conflict 拒絕。

## ADR 與取捨
A 只在應用層加 WHERE：便捷但漏 filter 或新入口可能跨租戶，不能取代引擎防護。B 採 GRANT + RLS / security_invoker view / trusted writer transaction：本輪採用，會員直接草稿權限最小化，ledger 不讓會員填造。C 開放 SECURITY DEFINER RPC 給會員：可減少 backend 功能，但需要嚴格 auth.uid()、EXECUTE ACL、固定 search_path、不可任意 owner 參數、role owner 和繞過 RLS 審視；本輪不採。writer 是信任角色，能直接 DML，故不能當一般 client 憑據；production 如需所有寫入均依 invariant，須限制 writer 存取路徑或重新設計，未以 SQL function 證明可防可信角色任意 DML。拒絕用 Supabase service role 偽裝一般使用者驗收。Lab session_user 來自真正分離 DB login，私有 Unix socket 的 trust 只是 disposable CI 測試設置，並非 Supabase JWT authentication，不能複製 production。未開 TCP，忽略繼承 PG* 環境參數，CI 若無可用 engine 則 fail 而非 skip；其他本機缺 PG 可明示 skip。

## 實作及驗收
- `examples/postgres-architecture/01-baseline.sql` 先建舊 schema（預設會員不可存取）；`02-rls-transaction.sql` 同交易增加 stock cap/驗既有資料、label default、RLS/GRANT/受限 view/函式 ACL。原生 PostgreSQL 練習檔放 examples，不是假裝 supabase/migrations 或可直接推雲端。
- 交易：鎖定 owner 的 stock，再查 prior receipt，成功扣減與 receipt insert 同一交易，失敗決策也持久保存。獨立 psql session 模擬 7+7 與剩餘 10，預期一成功一不足、remaining 3，兩筆 receipt、重播不扣庫存。失敗中斷後 stock/receipt 一起回復；未知 commit 不因 SQL 拒絕而盲目重送。此處只驗每 owner 的固定單列名額，未做共享多資源、分散式或全域序列化。
- Migration：增加 label 欄仍支援明示舊欄 INSERT，不代表 SELECT *、所有舊程式或 post-commit downgrade 相容。非法 legacy remaining=11 時 validation 拒絕且沒有殘留 constraint/label/RLS；修正為合法值後才重試。正式大型在線 migration 須另驗 expand/backfill/validate/contract、舊新 writer 同時運行/lock、備份 restore、版本降級或 forward-fix；不自行修正式資料、不在新寫入後盲退快照。
- 7 引擎 test methods：①隔離 schema 內故意給 legacy broad grant 的反例觀測兩列，migration 後兩帳號只看自己一列，view 相同，anon 拒絕；②合法新增編輯、跨 owner insert/update/ownership transfer 拒絕或 0 row；③會員與 anon 不可 writer DML/呼叫函式，receipt 隔離；④兩獨立連線競寫/冪等/衝突；⑤交易故障全回復；⑥舊明示欄位與新約束；⑦不合法歷史資料 migration abort。真引擎負對照不是既有真實產品漏洞。正負測試原始碼 `tests/test_postgres_architecture.py`，不以 mock 或 SQLite 代替。
- SQL 與測試 exact b5e61035272a8687b2f24a05030fda9d2eddfd44 / [CI 43720063088](https://github.com/lily4318/reliable-system-builder-agent/actions/runs/43720063088) job 132829900213；completed/success。全部 7 項真 PostgreSQL 測試及既有 487 項回歸已確認。
raw 247045 chars; 2026-11-15T13:39:45.3821442Z PG-ARCH-ENGINE: 18.6 (Ubuntu 18.6-1.pgdg26.04+2) private Unix socket; TCP disabled
2026-11-15T13:39:45.4638462Z test_backend_only_mutation_and_receipt_isolation (test_postgres_architecture.PostgresArchitectureTests.test_backend_only_mutation_and_receipt_isolation) ... ok
2026-11-15T13:39:45.5276568Z test_insert_update_and_owner_transfer (test_postgres_architecture.PostgresArchitectureTests.test_insert_update_and_owner_transfer) ... ok
2026-11-15T13:39:45.6047016Z test_invalid_legacy_data_aborts_migration_without_partial_schema (test_postgres_architecture.PostgresArchitectureTests.test_invalid_legacy_data_aborts_migration_without_partial_schema) ... ok
2026-11-15T13:39:45.6596651Z test_migration_preserves_rows_and_old_column_contract (test_postgres_architecture.PostgresArchitectureTests.test_migration_preserves_rows_and_old_column_contract) ... ok
2026-11-15T13:39:46.1322077Z test_real_concurrent_stock_and_idempotent_decisions (test_postgres_architecture.PostgresArchitectureTests.test_real_concurrent_stock_and_idempotent_decisions) ... ok
2026-11-15T13:39:46.1825241Z test_transaction_failure_rolls_back_stock_and_receipt (test_postgres_architecture.PostgresArchitectureTests.test_transaction_failure_rolls_back_stock_and_receipt) ... ok
2026-11-15T13:39:46.2683717Z test_unprotected_grant_negative_control_and_rls_isolation (test_postgres_architecture.PostgresArchitectureTests.test_unprotected_grant_negative_control_and_rls_isolation) ... ok
2026-11-15T13:39:54.6274516Z Ran 494 tests in 70.531s
2026-11-15T13:39:54.6274790Z OK

## 蒸餾與接續
原 architecture-design/security-review 及 EP-13 候選索引增量整合；L1/L2 有實際來源分析，L3 有受控真引擎實作驗收；L4 不以刻意 negative fixture 當既有產品故障，L5/L6 尚待新情境與獨立交接。 下階段優先 migration late-failure/lock contention、重複 token 同時提交與不同 owner namespace、現有編碼/連線權限剩餘缺口；另經授權才能做真正 Supabase Auth/JWT、anon/authenticated、直接 REST/RPC、Storage、advisors、migration history / restore，不能以 session_user lab 假裝已通過。原 HackMD matrix blob 25d164664d834953beea0a1c2cd41f71a017be56 不變、main/release 未改，不建立付費或免費外部資源、不部署。
