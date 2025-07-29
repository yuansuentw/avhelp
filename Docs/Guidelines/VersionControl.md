# 版本管理規範

v0.0.1, last update：2025/7/27

---

# 版本管理

## 版本號規則

使用 x.y.z（Semantic Versioning）三段版本號格式。

- **z 版本號**：由你決定是否增加，一般而言如果是新增測試案例、編排格式調整、小規模性能優化、文件內容增刪等不影響主要邏輯，則無須更新版號。但若涉及使用者明確告知 issue 編號或重大 bug 修復，或新實現了功能，則應推進版號。
- **x 和 y 版本號**：由使用者決定，並將明確指示推進。

## Commit Message 規範

- 內容及格式符合 Conventional Commits 規範。
- body 中應包含當次 Work 的 Goal、Tasks，簡述即可。
- 自定義 type：temp，用以表示進行到一半尚未完成的工作，此類型 commit 僅限本機儲存，避免 push 到 remote，並且下次 commit 應該使用 amend 模式進行覆蓋。

## Git 工作流程

1. 允許直接代替使用者 commit，不需提交 PR。
2. 持續在相同的 branch 上，若需切換分支，使用者將會自行手動處理。

## .gitignore 設定

應使用.gitignore排除版本控制項目：

- 密碼、API端點、access token 等敏感數據之設定文件，如.env。
- 編譯、打包後的中間代碼或二進制文件，如 build\、dist\、\_\_pycache\_\_\\等。
- IDE/linter 等輔助軟體設定檔、非直接相關的shell script等個人化資料，如 `.vscode`。
- log 檔案。