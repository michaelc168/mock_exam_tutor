# 題目變型實作說明

## 問題背景

用戶要求：**出題時要做「變型」，而不是 1:1 複製題庫**

原因：同樣的題目看了 2 次，學生就會背起來，失去考試意義。

---

## 錯誤理解 vs. 正確理解

### ❌ 錯誤理解（我之前的實作）

「變型」= 打亂選項順序

```python
# 錯誤做法
def _apply_variation(question):
    # 只是把 A/B/C/D 選項重新排列
    shuffle(question["options"])
    return question
```

**問題**：題目內容完全相同，學生看過就記住了。

---

### ✅ 正確理解（現在的實作）

「變型」= **AI 改寫題目**

- 保持：題型、難度、考點
- 改變：數字、情境、措辭

```python
# 正確做法
def _rewrite_question_with_llm(question, subject):
    # 用 OpenAI API 改寫題目
    # 輸入：原題
    # 輸出：全新的題目文字、選項、正確答案
    response = openai_client.chat.completions.create(...)
    return new_question
```

**效果**：每次出題都是全新的題目內容。

---

## 技術實作

### 1. 後端整合 OpenAI API

**檔案**：`backend/main.py`

```python
# 匯入 OpenAI
from openai import OpenAI

# 初始化 client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None

# 改寫函式
def _rewrite_question_with_llm(q: dict, subject: str) -> dict:
    """用 LLM 改寫題目：同概念、同難度，但新措辭、新數字、新情境。"""
    if not openai_client:
        return _shuffle_options_fallback(q)  # 無 API key 時降級
    
    # 建立 prompt
    prompt = f"""你是私立國中入學考題的出題專家。請將以下題目「改寫/變型」：

**原題**（{subject}科）：
{q["question"]}

(A) {q["options"][0]}
(B) {q["options"][1]}
(C) {q["options"][2]}
(D) {q["options"][3]}

**要求**：
1. 保持相同的**題型**與**難度**（小六升國一程度）
2. 改變**題目文字、情境、數字**，使其成為全新但類似的題目
3. 產生 4 個新選項（A/B/C/D），其中一個為正確答案
4. 如果是數學題，數字要合理且答案可計算；如果是語文題，改寫措辭但考點不變

**輸出格式（只輸出以下 JSON，不要其他說明）**：
{{
  "question": "改寫後的題目文字",
  "options": ["新選項A", "新選項B", "新選項C", "新選項D"],
  "correct_answer": "A或B或C或D"
}}
"""
    
    # 調用 OpenAI
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=1000,
    )
    
    # 解析回應
    content = response.choices[0].message.content.strip()
    result = json.loads(content)
    
    return {
        "question": result["question"],
        "options": result["options"],
        "correct_answer": result["correct_answer"],
    }
```

### 2. 出題流程

```python
def _sample_from_bank(bank_file, num_questions, subject):
    # 1. 解析題庫
    questions = _parse_bank_questions(bank_file)
    
    # 2. 隨機抽題
    selected = random.sample(questions, num_questions)
    
    # 3. 對每一題做變型（AI 改寫）
    varied = [_apply_variation(q, subject) for q in selected]
    
    return varied

def _apply_variation(q, subject):
    # 優先用 LLM 改寫
    # 無 API key 時降級為選項打亂
    return _rewrite_question_with_llm(q, subject)
```

### 3. 寫入考卷

```python
def _write_exam_file(output_file, questions, subject, exam_id):
    # 寫入題目與選項
    for i, q in enumerate(questions):
        md_content += f"### {i+1}. {q['question']}\n\n"
        for j, opt in enumerate(q['options']):
            md_content += f"({chr(65+j)}) {opt}  \n"
    
    # 寫入答案表（使用 AI 改寫後的正確答案）
    for i, q in enumerate(questions):
        md_content += f"| {i+1} | {q['correct_answer']} |\n"
```

---

## 降級機制

### 情況 A：有 API Key

後端對每一題調用 OpenAI `gpt-4o-mini`，改寫題目。

### 情況 B：無 API Key

後端降級為「選項打亂」：

```python
def _shuffle_options_fallback(q: dict) -> dict:
    """備案：打亂選項順序（假設第一項為正確）。"""
    opts = list(q["options"])
    labels = ["A", "B", "C", "D"]
    indexed = list(zip(labels, opts))
    random.shuffle(indexed)
    new_opts = [t[1] for t in indexed]
    original_first = opts[0]
    correct_letter = next(l for l, o in indexed if o == original_first)
    return {
        **q,
        "options": new_opts,
        "correct_answer": correct_letter,
    }
```

---

## 變型效果範例

### 數學題

#### 題庫原題
```
計算：10 × 11 × 12 × 13 × 14 = 240240，
則 (－11) × (－12) × (－13) × (－14) × (－15) = ？

(A) 320320
(B) 360360
(C) －320320
(D) －360360
```

#### AI 改寫後（範例 1）
```
已知 8 × 9 × 10 × 11 × 12 = 95040，
則 (－9) × (－10) × (－11) × (－12) × (－13) = ？

(A) －154440
(B) 154440
(C) －175560
(D) 175560
```

#### AI 改寫後（範例 2）
```
若 6 × 7 × 8 × 9 × 10 = 30240，
求 (－7) × (－8) × (－9) × (－10) × (－11) = ？

(A) 55440
(B) －55440
(C) 62370
(D) －62370
```

### 國語題

#### 題庫原題
```
「職業無貴賤，只要用心經營...」缺空處依序宜填入？

(A) 不到黃河心不死...
(B) 薑是老的辣...
(C) 吃得苦中苦...
(D) 行行出狀元...
```

#### AI 改寫後
```
「工作不分高低，只要認真投入...」缺空處依序宜填入？

(A) 水滴石穿非一日...
(B) 三百六十行...
(C) 師父領進門...
(D) 各行各業皆可成...
```

---

## 設定方式

### 1. 取得 API Key

https://platform.openai.com/api-keys

### 2. 設定環境變數

```bash
# backend/.env
OPENAI_API_KEY=sk-你的API金鑰
```

### 3. 重啟服務

```bash
./stop-dev.sh
./start-dev.sh
```

---

## 費用

使用 `gpt-4o-mini`：

| 生成題數 | 估計費用 |
|---------|---------|
| 20 題   | ~$0.05  |
| 100 題  | ~$0.25  |

---

## 測試

```bash
# 1. 設定 API key
echo "OPENAI_API_KEY=sk-你的key" > backend/.env

# 2. 重啟
./stop-dev.sh && ./start-dev.sh

# 3. 在 UI 點「開始出題」

# 4. 檢查生成的考卷
cat exams/generated/latest.md

# 5. 再出一次，比對題目是否不同
```

---

## 技術決策

### 為什麼選擇 `gpt-4o-mini`？

- ✅ 便宜（input $0.15/1M tokens）
- ✅ 快速（生成一題約 1-2 秒）
- ✅ 品質足夠（改寫題目不需要最強模型）

### 為什麼不用規則改寫？

```python
# ❌ 規則改寫（無法自動重算答案）
def _vary_math_numbers(question):
    # 把數字改一改
    new_question = question.replace("10", "8")
    # 但答案怎麼算？ 無法自動重算！
    return new_question
```

**問題**：
- 數學題改數字後，答案會錯
- 語文題改措辭後，可能語意不通
- 需要人工檢查每一題

**解決**：用 LLM 改寫，AI 會自動計算新答案並確保語意通順。

---

## 未來可能的改進

1. **支援其他 LLM**：Claude、本地 Ollama
2. **批次改寫**：一次送 20 題給 API（降低延遲）
3. **快取機制**：相同題目 + 種子 = 相同變型（可重現）
4. **難度調整**：讓 AI 產生簡單版/困難版

---

## 文件

- 快速設定：`SETUP-API-KEY.md`
- 詳細說明：`docs/llm-variation-setup.md`
- 本文件：`docs/variation-implementation.md`
