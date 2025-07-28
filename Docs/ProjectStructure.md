# 專案結構規範

v0.0.1, last update：2025/7/27

---

# 文件規範及目錄結構

## 組態檔

設計需同時供專案程式及使用者操作，用以儲存如常數、 DAG/flow 流程、parse 規則、及預設組態資訊等資料，優先使用 yaml 格式，前端程式則使用 json 格式，禁止使用 .ini 檔。但若涉及環境相關，例如因部署環境不同（生產、開發、測試）而有所差異的資訊，則應另儲存於.env檔案。

## 文件時間標記

所有文字文件應在開頭或結尾處加上最後更新時間資訊。

## 專案目錄結構

下面為第一層級，除`README.md`外均為可選：

### Docs/
- **Arch/**：放置組件關係圖、資料流程圖、外部資源網路圖等，只儲存當前版本，更新時應該覆蓋舊資料或刪除舊資料。
- **Handbooks/**：技術相關文件，例如API相關文檔，或是部署流程等。
- **Caveats.md**：紀錄血淚教訓（lesson learned），避免後續再次踩坑。
	- 每項總共不超過200字，最多1個子階層。
	- 內容簡潔扼要，僅需紀錄問題核心和解決方案，其他如除錯過程等資訊省略。
- **ClaudeAgents.md**：Agent定義與協作流程。
- **Workflow.md**：工作流程總覽。
- **CodingStandards.md**：編碼規範與品質標準。
- **TechStack.md**：技術棧規範。
- **ProjectStructure.md**：專案結構規範（本文件）。
- **VersionControl.md**：版本管理規範。

### Docs/Missions/
- **YYYYMMDDTHHMM-簡短任務名稱/**
	- **general_info.md**：含row idea, requirement, solution design, adr, closing summary, commit message等
	- **progress_status.md**：紀錄plan中的task執行進度
	- **plan/**
		- **task_name1.md**
			- spec
			- test result
			- review report
			- 錯誤分析報告及改善方案
		- **task_name2.md**
		- ...

### README.md

### Misc/
存放其他不易分類的輔助資料
- **Logs/**
	- 限定開發或測試環境，為了便利提供開發人員檢視 log 檔，統一放在專案目錄中。
	- 正式生產環境中，log 檔案應視作業系統規範及運行權限，放置於系統或使用者目錄下，專門用於儲存 app 資料的路徑。

### Shared/
放置各服務、子專案或模組等共通的資產，如graphql 或資料庫的Schema定義等。

## 特殊規則

1. 不用加 License 文件。
2. 特殊功能性檔案，例如 GraphQL 的 Schema，不受上面規範限制，依慣例處理。
3. 檔名（含副檔名）上限為 40 字元，目錄名上限為 28 字元，最大路徑長度 200 字元，最大目錄深度 6 層。路徑與層級計算皆由專案根目錄起算。