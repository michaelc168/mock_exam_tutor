# 🔑 快速設定：題目變型功能

## 現況

✅ **已完成**：後端已整合 LLM API，可以**自動改寫題目**  
✅ **支援**：Gemini（推薦，免費）或 OpenAI  
⚠️ **需要**：設定你的 API Key

---

## 什麼是「題目變型」？

當你在 UI 點「開始出題」時，系統會：

1. ❌ **不是**：直接從題庫複製貼上
2. ❌ **不是**：只打亂選項順序
3. ✅ **而是**：用 AI 改寫每一題，產生**全新的題目**

### 範例

#### 原題庫的題目
```
計算：10 × 11 × 12 × 13 × 14 = 240240，
則 (－11) × (－12) × (－13) × (－14) × (－15) = ？

(A) 320320
(B) 360360
(C) －320320
(D) －360360
```

#### AI 改寫後（每次不同）
```
已知 8 × 9 × 10 × 11 × 12 = 95040，
則 (－9) × (－10) × (－11) × (－12) × (－13) = ？

(A) －154440
(B) 154440
(C) －175560
(D) 175560
```

**重點**：題型相同、難度相同，但數字、情境完全不同。

---

## 如何設定 API Key

### 方案 A：Gemini（推薦，免費）

**詳細教學**：`SETUP-GEMINI.md`

```bash
# 1. 到 https://aistudio.google.com/app/apikey 取得 key
# 2. 建立 backend/.env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza你的key

# 3. 安裝並重啟
pip install -r backend/requirements.txt
./stop-dev.sh && ./start-dev.sh
```

### 方案 B：OpenAI（需付費）

```bash
# 1. 到 https://platform.openai.com/api-keys 取得 key
# 2. 建立 backend/.env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-你的key

# 3. 重啟
./stop-dev.sh && ./start-dev.sh
```

---

## 費用

### Gemini（推薦）
- ✅ **完全免費**：每分鐘 15 次請求
- 生成 20 題考卷：**$0**

### OpenAI
- 使用 `gpt-4o-mini`：
  - 生成 20 題：約 **$0.05 美元**
  - 生成 100 題：約 **$0.25 美元**

---

## 測試

1. 設定好 API key 並重啟
2. 在 UI 點「開始出題」
3. 檢查生成的考卷（`exams/generated/` 資料夾）
4. 每次出題，題目內容都會不同

---

## 沒有 API Key 會怎樣？

系統會**降級**為：
- ❌ 題目文字不變（直接複製題庫）
- ✅ 選項順序打亂

這樣至少同一題的選項每次位置不同，但題目內容會重複。

---

## 重要提醒

⚠️ API Key 是你的 OpenAI 帳號金鑰，**不要上傳到 GitHub**

我已經建立 `.env.example` 作為範本，你只需要：

```bash
cp backend/.env.example backend/.env
# 然後編輯 backend/.env，填入你的 API key
```

`.env` 檔案已經在 `.gitignore` 中，不會被 commit。

---

## 需要協助？

詳細文件：`docs/llm-variation-setup.md`

問題排查：
1. 檢查 `logs/backend.log` 是否有錯誤
2. 確認 API key 格式正確（`sk-` 開頭）
3. 確認 OpenAI 帳號有額度
