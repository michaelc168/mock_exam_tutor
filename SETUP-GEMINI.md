# 🚀 快速設定：Gemini API（推薦）

## 為什麼選 Gemini？

✅ **完全免費**：每分鐘 15 次請求  
✅ **速度快**：`gemini-1.5-flash` 比 GPT-4o-mini 更快  
✅ **品質好**：改寫題目效果很棒  
✅ **無需綁卡**：不用輸入信用卡

---

## 設定步驟（3 分鐘搞定）

### 1. 取得 API Key

1. 到 https://aistudio.google.com/app/apikey
2. 用 Google 帳號登入
3. 點「Create API Key」
4. 複製 API Key（`AIza...` 開頭）

### 2. 設定環境變數

建立 `backend/.env`：

```bash
# backend/.env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza你的API金鑰
```

### 3. 安裝依賴並重啟

```bash
# 安裝 Gemini SDK
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# 重啟服務
./stop-dev.sh
./start-dev.sh
```

---

## 測試

在 UI 點「開始出題」，後端會用 Gemini 改寫題目。

檢查 `logs/backend.log` 確認沒有錯誤。

---

## 費用

### Gemini 免費額度

| 模型 | 免費額度 | 速度 |
|------|---------|------|
| gemini-1.5-flash | **15 RPM** | 極快 |
| gemini-1.5-pro | 2 RPM | 較慢但更聰明 |

**RPM** = Requests Per Minute（每分鐘請求數）

生成 20 題考卷約需 20 次請求（每題一次），完全在免費額度內。

### 對比 OpenAI

| 項目 | Gemini | OpenAI |
|------|--------|--------|
| 免費額度 | ✅ 15 RPM | ❌ 需付費 |
| 速度 | 🚀 極快 | 🐢 較慢 |
| 品質 | 😊 很好 | 😊 很好 |
| 綁卡 | ❌ 不用 | ✅ 需要 |

---

## 備用：OpenAI

如果你已有 OpenAI API Key，也可以用：

```bash
# backend/.env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-你的key
```

---

## 範例：backend/.env

```bash
# 使用 Gemini（推薦）
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyC...你的完整key

# 或使用 OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-...
```

---

## 問題排查

### 錯誤：`API key not valid`

- 檢查 `backend/.env` 的 API key 是否正確
- 確認沒有多餘空格

### 錯誤：`Resource has been exhausted`

- Gemini 免費額度用完（每分鐘 15 次）
- 等一分鐘再試，或升級到付費版

### 後端啟動失敗

```bash
# 檢查 logs
cat logs/backend.log

# 確認環境變數
source backend/venv/bin/activate
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
```

---

## 總結

1. 到 https://aistudio.google.com/app/apikey 取得 API key
2. 建立 `backend/.env`，填入 `GEMINI_API_KEY`
3. 安裝依賴：`pip install -r backend/requirements.txt`
4. 重啟：`./stop-dev.sh && ./start-dev.sh`
5. 在 UI 出題測試

完全免費，不用綁卡！
