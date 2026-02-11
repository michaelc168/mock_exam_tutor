# 🚀 Gemini 變型功能 - 快速開始

## ✅ 已完成

- ✅ 後端已整合 Gemini API（`gemini-1.5-flash`）
- ✅ 同時支援 OpenAI（可選）
- ✅ 服務已重啟運行中

## 📝 下一步：設定 API Key

### 取得 Gemini API Key（免費）

1. 到 https://aistudio.google.com/app/apikey
2. 用 Google 帳號登入
3. 點「Create API Key」
4. 複製 API key（`AIza...` 開頭）

### 設定環境變數

建立 `backend/.env` 檔案：

```bash
# backend/.env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza你的完整API金鑰
```

### 重啟服務

```bash
./stop-dev.sh
./start-dev.sh
```

## 🎯 測試變型功能

1. 設定好 API key 並重啟
2. 在 UI (`http://localhost:3000`) 點「開始出題」
3. 選擇科目與題數
4. 系統會自動用 Gemini 改寫每一題
5. 檢查生成的考卷（`exams/generated/` 資料夾）

## 💡 變型效果

### 數學題範例

**題庫原題**：
```
計算：10 × 11 × 12 × 13 × 14 = 240240，
則 (－11) × (－12) × (－13) × (－14) × (－15) = ？
```

**Gemini 改寫後**（每次不同）：
```
已知 7 × 8 × 9 × 10 × 11 = 55440，
則 (－8) × (－9) × (－10) × (－11) × (－12) = ？
```

### 國語題範例

**題庫原題**：
```
「職業無貴賤，只要用心經營...」缺空處依序宜填入？
```

**Gemini 改寫後**：
```
「工作不分高低，只要認真投入...」缺空處依序宜填入？
```

## 💰 費用

### Gemini（預設）
- ✅ **完全免費**
- 每分鐘 15 次請求
- 生成 20 題考卷：**$0**

### OpenAI（備用）
如果你想用 OpenAI：

```bash
# backend/.env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-你的key
```

費用：生成 20 題約 $0.05 美元

## 📖 詳細文件

- 📄 `SETUP-GEMINI.md` - Gemini 詳細設定教學
- 📄 `SETUP-API-KEY.md` - 兩種 API 的比較
- 📄 `docs/llm-variation-setup.md` - 技術實作細節
- 📄 `docs/variation-implementation.md` - 完整技術文件

## 🔍 問題排查

### 後端啟動失敗

```bash
# 檢查 logs
cat logs/backend.log

# 確認環境變數
source backend/venv/bin/activate
python -c "import os; print('GEMINI_API_KEY:', os.getenv('GEMINI_API_KEY'))"
```

### API 錯誤

- `API key not valid`: 檢查 API key 是否正確
- `Resource exhausted`: 免費額度用完，等一分鐘
- 無 API key: 系統會降級為「選項打亂」

## 📌 重要提醒

⚠️ **不要把 `.env` 檔案上傳到 GitHub**

`.env` 已經在 `.gitignore` 中，不會被 commit。

## 🎉 開始使用

```bash
# 1. 取得 API key
open https://aistudio.google.com/app/apikey

# 2. 設定環境變數
echo "LLM_PROVIDER=gemini" > backend/.env
echo "GEMINI_API_KEY=AIza你的key" >> backend/.env

# 3. 重啟
./stop-dev.sh && ./start-dev.sh

# 4. 開始出題
open http://localhost:3000
```

完全免費，無需綁卡！
