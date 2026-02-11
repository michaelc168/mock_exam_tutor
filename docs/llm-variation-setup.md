# LLM 變型功能設定

## 功能說明

當你在 UI 點「開始出題」時，後端會：
1. 從題庫隨機抽題
2. **用 OpenAI API 改寫每一題**（同概念但新措辭、新數字、新情境）
3. 寫入 `exams/generated/` 資料夾
4. 新考卷會出現在「我的考卷」

這樣每次出題都是**全新的題目**，而不是重複的題庫內容。

---

## 設定步驟

### 1. 取得 OpenAI API Key

1. 到 https://platform.openai.com/api-keys
2. 登入/註冊 OpenAI 帳號
3. 點「Create new secret key」
4. 複製 API key（`sk-...` 開頭）

### 2. 設定環境變數

建立 `backend/.env` 檔案：

```bash
OPENAI_API_KEY=sk-你的API金鑰
```

或在啟動時設定：

```bash
export OPENAI_API_KEY=sk-你的API金鑰
./start-dev.sh
```

或用 PM2 的 env：

```javascript
// ecosystem.config.cjs
{
  name: 'mock-exam-backend',
  env: {
    OPENAI_API_KEY: 'sk-你的API金鑰'
  },
  ...
}
```

### 3. 安裝依賴

```bash
source backend/venv/bin/activate
pip install -r backend/requirements.txt  # 會安裝 openai
```

### 4. 重啟服務

```bash
./stop-dev.sh && ./start-dev.sh
# 或
pm2 restart ecosystem.config.cjs
```

---

## 運作方式

### 有 API Key 時

後端會對**每一題**調用 OpenAI `gpt-4o-mini` 模型：

**Prompt 範例**（國語科）：
```
你是私立國中入學考題的出題專家。請將以下題目「改寫/變型」：

原題（國語科）：
世說新語‧德行：「東晉人庾亮坐騎之中有一匹馬的盧...」

(A) 事不三思總有敗...
(B) 千經萬典，孝悌為先
(C) 滿招損，謙受益
(D) 己所不欲，勿施於人

要求：
1. 保持相同的題型與難度
2. 改變題目文字、情境、數字
3. 產生 4 個新選項，其中一個為正確答案
4. 語文題改寫措辭但考點不變，數學題數字要合理且答案可計算

輸出格式（JSON）：
{
  "question": "改寫後的題目文字",
  "options": ["新選項A", "新選項B", "新選項C", "新選項D"],
  "correct_answer": "B"
}
```

LLM 會回傳改寫後的題目、選項、正確答案。

### 無 API Key 時

降級為**選項打亂**：
- 題目文字不變
- 四個選項重新排列
- 記錄正確答案對應到的新位置

---

## 變型效果

### 範例：數學題

**原題**：
```
計算：10 × 11 × 12 × 13 × 14 = 240240，
則 (－11) × (－12) × (－13) × (－14) × (－15) = ？

(A) 320320
(B) 360360
(C) －320320
(D) －360360
```

**變型後**（可能）：
```
已知 8 × 9 × 10 × 11 × 12 = 95040，
則 (－9) × (－10) × (－11) × (－12) × (－13) = ？

(A) －154440
(B) 154440
(C) －175560
(D) 175560
```

### 範例：國語題

**原題**：
```
「職業無貴賤，只要用心經營...」缺空處依序宜填入？
(A) 不到黃河心不死...
(B) 薑是老的辣...
(C) 吃得苦中苦...
(D) 行行出狀元...
```

**變型後**（可能）：
```
「工作不分高低，只要認真投入...」缺空處依序宜填入？
(A) 水滴石穿非一日...
(B) 三百六十行...
(C) 師父領進門...
(D) 各行各業皆可成...
```

---

## 費用

使用 `gpt-4o-mini`：
- Input: ~$0.15 / 1M tokens
- Output: ~$0.6 / 1M tokens

生成 20 題綜合考卷（每題約 200 tokens input + 150 tokens output）：
- 估計費用：~$0.05 美元

---

## 測試

```bash
# 設定 API key
export OPENAI_API_KEY=sk-你的key

# 啟動
./start-dev.sh

# 在 UI 點「開始出題」，後端會自動調用 LLM 改寫
# 檢查 logs/backend.log 可看到改寫過程
```

---

## 備註

- 若無 API key，仍可用（但只是選項打亂，不是真正的變型）
- 可在 `backend/.env` 設定，避免每次 export
- 未來可支援其他 LLM（Claude、本地 Ollama 等）
