# 系統架構文檔

## 整體架構

```
┌─────────────┐
│   Browser   │
│ (用戶介面)   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   Next.js   │
│  Frontend   │  Port 3000
└──────┬──────┘
       │ REST API
       ▼
┌─────────────┐
│   FastAPI   │
│   Backend   │  Port 8000
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│   Exams     │◄────►│   Scripts    │
│   Files     │      │ (PDF Convert)│
└─────────────┘      └──────────────┘
```

## 技術棧

### 前端
- **框架**: Next.js 16 (React 19)
- **語言**: TypeScript
- **UI 庫**: 
  - Radix UI (無障礙組件)
  - Tailwind CSS (樣式)
  - Lucide React (圖標)
- **狀態管理**: React Hooks (useState, useEffect)
- **HTTP 客戶端**: Fetch API

### 後端
- **框架**: FastAPI 0.115.6
- **語言**: Python 3.13
- **ASGI 伺服器**: Uvicorn
- **資料驗證**: Pydantic 2.10.5
- **跨域處理**: CORS Middleware

### 資料存儲
- **題庫**: Markdown 檔案 (`.md`)
- **生成的考卷**: Markdown + PDF
- **無需資料庫**: 檔案系統即存儲

### 工具
- **PDF 轉換**: Node.js + Puppeteer + MathJax
- **數學公式**: LaTeX → SVG
- **開發工具**: 
  - pnpm/npm (前端依賴)
  - pip + venv (後端依賴)

---

## 資料流

### 1. 出題流程

```
用戶點擊「開始出題」
    ↓
前端發送 POST /api/exams/generate
    ↓
後端接收請求 {subject, num_questions, difficulty}
    ↓
讀取題庫 (exams/bank/*.md)
    ↓
AI 生成考卷 (TODO: 整合 AI API)
    ↓
儲存 Markdown (exams/generated/*.md)
    ↓
返回考卷資訊 {exam_id, filename, ...}
    ↓
前端顯示成功訊息
    ↓
跳轉到考卷列表
```

### 2. PDF 生成流程

```
前端請求 POST /api/exams/{exam_id}/generate-pdf
    ↓
後端接收請求
    ↓
讀取 Markdown 檔案
    ↓
呼叫 Node.js 腳本: scripts/convert-to-pdf.js
    ↓
    ┌──────────────────────┐
    │ convert-to-pdf.js    │
    │ 1. 解析 Markdown      │
    │ 2. LaTeX → SVG       │
    │ 3. HTML → PDF        │
    └──────────────────────┘
    ↓
生成 PDF 檔案 (exams/generated/*.pdf)
    ↓
返回成功訊息
```

### 3. 下載流程

```
用戶點擊「下載」
    ↓
前端跳轉到 /api/exams/{exam_id}/download
    ↓
後端檢查檔案存在性
    ↓
    ├─ 有 PDF？ → 返回 PDF (Content-Type: application/pdf)
    └─ 無 PDF？ → 返回 Markdown (Content-Type: text/markdown)
    ↓
瀏覽器自動下載
```

---

## API 設計

### RESTful 原則

| HTTP 方法 | 用途 | 範例 |
|-----------|------|------|
| GET | 讀取資源 | `/api/exams` 列出考卷 |
| POST | 建立資源 | `/api/exams/generate` 生成考卷 |
| DELETE | 刪除資源 | (未實作) |
| PUT/PATCH | 更新資源 | (未實作) |

### 錯誤處理

| 狀態碼 | 說明 | 範例 |
|--------|------|------|
| 200 | 成功 | 考卷生成成功 |
| 400 | 錯誤請求 | 科目參數錯誤 |
| 404 | 找不到 | 考卷 ID 不存在 |
| 500 | 伺服器錯誤 | PDF 轉換失敗 |

### 回應格式

**成功回應**：
```json
{
  "exam_id": "exam-chinese-20260205-143022",
  "filename": "exam-chinese-20260205-143022.md",
  "total_questions": 20,
  "created_at": "2026-02-05T14:30:22",
  "download_url": "/api/exams/exam-chinese-20260205-143022/download"
}
```

**錯誤回應**：
```json
{
  "detail": "不支援的科目"
}
```

---

## 前端架構

### 頁面結構

```
app/
├── layout.tsx          # 根布局
├── page.tsx            # 首頁（選擇科目）
└── exams/
    └── page.tsx        # 考卷列表
```

### 元件樹

```
Page (首頁)
├── Header
│   ├── Logo
│   └── Link to /exams
├── Hero Section
└── Plans Grid
    └── PlanCard × 4
        ├── Icon
        ├── Title
        ├── Description
        ├── Features List
        └── Button (onClick → API 呼叫)

ExamsPage (考卷列表)
├── Header
│   ├── Logo
│   └── Reload Button
└── Exam List
    └── ExamCard × N
        ├── Icon
        ├── Metadata
        └── Download Button
```

### 狀態管理

- **loading**: 是否正在請求 API
- **message**: 成功/錯誤訊息
- **exams**: 考卷列表資料

### API 客戶端

`lib/api.ts` 封裝所有 API 請求：

```typescript
class ApiClient {
  async generateExam(request)    // 生成單科考卷
  async generateMixedExam(...)   // 生成綜合考卷
  async listExams()              // 列出考卷
  async getExam(examId)          // 取得考卷內容
  async generatePdf(examId)      // 生成 PDF
  getDownloadUrl(examId)         // 取得下載 URL
}
```

---

## 後端架構

### 模組結構

```
backend/
├── main.py              # 主程式
├── requirements.txt     # 依賴
└── venv/               # 虛擬環境
```

### 未來可擴展為：

```
backend/
├── main.py
├── api/
│   ├── exams.py        # 考卷 API
│   ├── subjects.py     # 科目 API
│   └── auth.py         # 認證 (未來)
├── services/
│   ├── exam_generator.py   # AI 生成邏輯
│   ├── pdf_converter.py    # PDF 轉換
│   └── question_bank.py    # 題庫管理
├── models/
│   └── schemas.py      # Pydantic 模型
└── utils/
    └── helpers.py      # 工具函數
```

### 關鍵類別

```python
# 資料模型
class ExamRequest(BaseModel):
    subject: str
    num_questions: int
    difficulty: Optional[str]

class ExamResponse(BaseModel):
    exam_id: str
    filename: str
    total_questions: int
    created_at: str
```

---

## 安全性考量

### 目前狀態

✅ **已實作**：
- CORS 限制（僅允許 localhost:3000）
- 路徑遍歷防護（使用 pathlib）
- 基本輸入驗證（Pydantic）

❌ **未實作**：
- 使用者認證
- API Rate Limiting
- 檔案上傳限制
- SQL/NoSQL 注入防護（無資料庫）

### 建議改進

1. **認證系統**：JWT Token
2. **限流**：每分鐘最多 10 次出題
3. **檔案大小限制**：單個考卷最大 10MB
4. **HTTPS**：生產環境必須使用
5. **環境變數**：API Key 不寫死在程式碼中

---

## 效能優化

### 目前效能

| 操作 | 時間 |
|------|------|
| 生成考卷 (模擬) | ~100ms |
| 列出考卷 | ~50ms |
| PDF 轉換 | ~2-5s |

### 優化方向

1. **快取**：
   - Redis 快取常用題庫
   - 瀏覽器快取靜態資源

2. **背景任務**：
   - PDF 生成改為背景任務
   - 使用 Celery + RabbitMQ

3. **CDN**：
   - 靜態資源上傳 CDN
   - 圖片壓縮

4. **資料庫**：
   - 題庫改用 PostgreSQL
   - 全文搜索優化

---

## 部署建議

### 開發環境

✅ 已實作：
- `start-dev.sh` 一鍵啟動
- Hot Reload（前後端）
- 日誌檔案

### 生產環境

**前端**：
```bash
cd frontend
npm run build
npm run start
```

**後端**：
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker 化（建議）

```dockerfile
# Dockerfile.frontend
FROM node:20-alpine
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build
CMD ["npm", "start"]

# Dockerfile.backend
FROM python:3.13-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY backend/ ./
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose**：
```yaml
version: '3.8'
services:
  frontend:
    build: 
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
  
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./exams:/app/exams
```

---

## 未來擴展

### Phase 1: 基礎功能
- ✅ 出題介面
- ✅ 考卷列表
- ✅ PDF 下載
- ⏳ AI 生成整合（TODO）

### Phase 2: 使用者功能
- ⏳ 使用者註冊/登入
- ⏳ 答題功能（線上作答）
- ⏳ 自動評分
- ⏳ 錯題本

### Phase 3: 進階功能
- ⏳ 學習分析（答題報告）
- ⏳ 錯題變型（智能推薦）
- ⏳ 多人協作（老師/學生）
- ⏳ 手機 App（React Native）

### Phase 4: 企業功能
- ⏳ 多租戶（SaaS）
- ⏳ 付費訂閱
- ⏳ 數據分析儀表板
- ⏳ API 開放平台

---

## 總結

這個架構設計的核心理念：

1. **簡單優先**: 檔案系統 > 資料庫
2. **逐步演進**: 模組化設計，易於擴展
3. **使用者體驗**: 快速回應，清楚反饋
4. **開發效率**: 一鍵啟動，自動化工具

**目前狀態**: MVP (最小可行產品)
**下一步**: 整合 AI API 實現真實出題功能
