# Mock Exam Tutor - UI 系統

這是為私中考題系統架設的完整 UI 介面。

## 系統架構

```
mock_exam_tutor/
├── frontend/              # Next.js 前端
│   ├── app/              # 頁面
│   │   ├── page.tsx      # 首頁（選擇科目）
│   │   └── exams/        # 考卷列表
│   ├── components/       # UI 元件
│   └── lib/              # API 客戶端
├── backend/              # FastAPI 後端
│   ├── main.py          # API 伺服器
│   └── requirements.txt  # Python 依賴
└── exams/               # 考題資料
    ├── bank/            # 題庫
    └── generated/       # 生成的考卷
```

## 功能特色

✅ **4 種出題模式**
- 國語科（20 題）
- 英語科（20 題）
- 數學科（40 題）
- 綜合考卷（國 20 + 英 20 + 數 40）

✅ **完整功能**
- AI 智能出題
- 考卷列表管理
- PDF 下載
- 漂亮的 UI 介面

## 快速開始

### 1. 安裝後端依賴

```bash
cd backend
pip install -r requirements.txt
```

### 2. 安裝前端依賴

```bash
cd frontend
npm install
# 或使用 pnpm
pnpm install
```

### 3. 啟動系統

**方法 1：使用啟動腳本（推薦）**

```bash
# 在專案根目錄執行
chmod +x start-dev.sh
./start-dev.sh
```

**方法 2：手動啟動**

終端 1 - 啟動後端：
```bash
cd backend
uvicorn main:app --reload --port 8000
```

終端 2 - 啟動前端：
```bash
cd frontend
npm run dev
# 或
pnpm dev
```

### 4. 開啟瀏覽器

- 前端：http://localhost:3000
- 後端 API：http://localhost:8000
- API 文檔：http://localhost:8000/docs

## API 端點

### 考卷相關

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/exams` | 列出所有考卷 |
| GET | `/api/exams/{exam_id}` | 取得特定考卷 |
| POST | `/api/exams/generate` | 生成單科考卷 |
| POST | `/api/exams/generate-mixed` | 生成綜合考卷 |
| GET | `/api/exams/{exam_id}/download` | 下載考卷 |
| POST | `/api/exams/{exam_id}/generate-pdf` | 生成 PDF |

### 其他

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/subjects` | 取得科目資訊 |
| GET | `/api/stats` | 統計資訊 |

## 使用範例

### 1. 首頁選擇科目

點擊任一卡片開始出題：
- 國語科 → 自動生成 20 題國語考卷
- 英語科 → 自動生成 20 題英語考卷
- 數學科 → 自動生成 40 題數學考卷
- 錯題變型 → 生成綜合考卷（20+20+40）

### 2. 查看考卷列表

點擊右上角「我的考卷」查看所有已生成的考卷

### 3. 下載考卷

在考卷列表中點擊「下載」按鈕

## 開發指南

### 前端開發

```bash
cd frontend
npm run dev     # 開發模式
npm run build   # 建置
npm run start   # 生產模式
npm run lint    # 檢查代碼
```

### 後端開發

```bash
cd backend
uvicorn main:app --reload --port 8000  # 開發模式（自動重載）
uvicorn main:app --port 8000           # 生產模式
```

### 環境變數

**前端** (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**後端**：
- 預設使用專案內的 `exams/` 資料夾
- 無需額外設定

## 整合現有系統

目前後端 API 已經可以：
- ✅ 讀取現有題庫
- ✅ 列出已生成的考卷
- ✅ 提供考卷下載
- ✅ 呼叫 PDF 轉換腳本

**TODO：整合 AI 生成**

現在的 `generateExam()` 只是返回模擬資料。要整合實際的 AI 生成，你可以：

**選項 1：在 Python 中呼叫 Cursor AI API**
```python
# 在 backend/main.py 中
# TODO: 整合 OpenAI API 或 Anthropic API
```

**選項 2：使用現有的 Cursor 規則**
```python
# 可以透過 subprocess 執行 Cursor CLI（如果有）
```

**選項 3：直接在前端呼叫 AI（需要 API key）**
```typescript
// 在 frontend/lib/ai.ts 中
// 使用 OpenAI SDK 或 Anthropic SDK
```

## 疑難排解

### 前端無法連接後端

檢查：
1. 後端是否正在運行（`http://localhost:8000`）
2. CORS 設定是否正確（已在 `backend/main.py` 設定）
3. `.env.local` 中的 API URL 是否正確

### PDF 生成失敗

確保：
1. Node.js 已安裝
2. 已執行 `npm install`（在專案根目錄）
3. `scripts/convert-to-pdf.js` 可執行

### 考卷列表為空

確認：
1. `exams/generated/` 資料夾存在
2. 資料夾中有 `.md` 檔案

## 授權

MIT License
