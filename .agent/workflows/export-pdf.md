---
description: 將指定的 Markdown 檔案轉換為高品質 PDF 報告
---

# PDF 轉換工作流

此流程將指定的 Markdown 檔案（如分析 Session 或個股報告）轉換為具備高品質樣式的 PDF 檔案，並儲存在 `exports/` 資料夾中。

## 執行步驟

1. **環境檢查**
   // turbo
   確認必要的轉換工具已就緒。
   `node -e "require('md-to-pdf')"`

2. **檔案轉換**
   // turbo
   執行轉換腳本對目標檔案進行處理。
   `node convert.js {{target}}`

3. **產出確認**
   轉換完成後，請查閱 `exports/` 資料夾獲取 PDF 檔案。

## 使用方式
在聊天視窗輸入：
`/export-pdf [檔案路徑]`

**範例**:
- `/export-pdf sessions/session_2026-01-21.md`
- `/export-pdf stock/2330.TW-分析.md`
