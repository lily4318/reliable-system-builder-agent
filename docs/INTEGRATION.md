# 跨帳號整合與使用

使用者只要把公開網址 `https://github.com/lily4318/reliable-system-builder-agent` 加上一句需求貼到可讀 GitHub 的 AI，即可要求依最新 README／START_HERE／AGENTS 流程提供協助。

## 要持續在另一專案中使用
1. 在**原專案**正式持久指令或 Agent 設定引用此公開網址，並固定採用的 release commit SHA。
2. 每次先讀原專案的最新正式程式、規格、部署、資料表、授權與接續點。
3. 本公開 Agent 的新版本不能覆寫原專案的更嚴格安全門檻。
4. 若要調用真正 coding agent，須依平台能力安裝／授權 Skills 或 connector；不能靠貼 URL 就讓它在背景執行。
5. 任何外部 repo／GAS／Sheets 寫入須另行核准；本公開 repo 只存放通用規則與去識別化回歸案例。

## 同時供研究室帳號使用
公用 Repository 可直接讀取；有權限的人可 fork 或對此 repo 提交 PR。不要在公開庫放入研究專案的 OAuth、個資或私有原始碼。

範例：`integrations/project-manifest.example.json`。
