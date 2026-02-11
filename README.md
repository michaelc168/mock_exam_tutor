# 私中入學模擬考試出題系統

這個專案旨在建立一個類似私中入學模擬考試出題系統。

## 🎉 最新功能：AI 題目變型

✨ **全新**：用 Gemini API 自動改寫題目！

- 🚀 **完全免費**：使用 Gemini 免費額度
- 🎯 **真正變型**：AI 改寫每一題（不是只打亂選項）
- 📝 **保持難度**：同題型、同考點，但不同數字、情境、措辭
- 🔄 **每次不同**：同一份考卷出兩次，題目內容完全不同

### 快速開始

1. **取得 Gemini API Key**（免費）：https://aistudio.google.com/app/apikey
2. **設定環境變數**：
   ```bash
   echo "LLM_PROVIDER=gemini" > backend/.env
   echo "GEMINI_API_KEY=AIza你的key" >> backend/.env
   ```
3. **重啟服務**：
   ```bash
   ./stop-dev.sh && ./start-dev.sh
   ```
4. **開始出題**：在 UI 點「開始出題」

📖 **詳細教學**：`README-GEMINI.md`

---

## 目錄結構

- **.agent/**: 存放 AI 代理的技能 (skills) 與工作流程 (workflows)，用於自動化出題任務。
- **exams/**: 用於存放題庫。
- **bank/**: 用於存放題庫。
- **generated/**: 用於存放生成的題庫。
- **templates/**: 用於存放題庫。
- **report/**: 用於存放題庫。
- **scripts/**: 用於存放 Python 腳本。
- **pdf-style.css**: PDF 样式設定。
- **requirements.txt**: 放置 Python 腳本或設定檔 (如爬蟲、數據分析工具)。

## 下一步

1. 定義自動化工作流程 (例如：自動抓取題庫)。
2. 建立題庫 (Markdown Template)。
3. 設定 Python 虛擬環境 (requirements.txt) 以執行出題工具。
