# Gemini vs OpenAI 比較

## 快速選擇

| 需求 | 推薦 |
|------|------|
| 完全免費 | ✅ **Gemini** |
| 最快速度 | ✅ **Gemini** (`gemini-1.5-flash`) |
| 已有 OpenAI 帳號 | OpenAI |
| 企業級穩定性 | OpenAI |

---

## 詳細比較

### Gemini（推薦）

| 項目 | 內容 |
|------|------|
| **模型** | `gemini-1.5-flash` |
| **費用** | ✅ **免費**（15 RPM） |
| **速度** | 🚀 極快（~1 秒/題） |
| **品質** | 😊 優秀 |
| **設定** | 簡單（無需綁卡） |
| **API Key** | https://aistudio.google.com/app/apikey |
| **限制** | 每分鐘 15 次請求 |

#### 環境變數
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
```

#### 適合場景
- ✅ 個人使用、學習專案
- ✅ 中小型題庫（每次出 20-30 題）
- ✅ 不想綁信用卡
- ✅ 想要最快速度

---

### OpenAI

| 項目 | 內容 |
|------|------|
| **模型** | `gpt-4o-mini` |
| **費用** | 💰 付費（~$0.05/20 題） |
| **速度** | 🐢 較慢（~2 秒/題） |
| **品質** | 😊 優秀 |
| **設定** | 需要綁信用卡 |
| **API Key** | https://platform.openai.com/api-keys |
| **限制** | 視付費方案而定 |

#### 環境變數
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

#### 適合場景
- ✅ 企業級應用
- ✅ 大量出題（每天 100+ 題）
- ✅ 已有 OpenAI 額度
- ✅ 需要更高穩定性

---

## 變型品質比較

兩者改寫品質**相當**，都能做到：

- ✅ 保持題型與難度
- ✅ 改變數字、情境、措辭
- ✅ 語意通順、答案正確
- ✅ 適合小六升國一程度

### 範例：數學題

**題庫原題**：
```
計算：10 × 11 × 12 × 13 × 14 = 240240，
則 (－11) × (－12) × (－13) × (－14) × (－15) = ？
```

**Gemini 改寫**：
```
已知 8 × 9 × 10 × 11 × 12 = 95040，
則 (－9) × (－10) × (－11) × (－12) × (－13) = ？
```

**OpenAI 改寫**：
```
計算：7 × 8 × 9 × 10 × 11 = 55440，
求 (－8) × (－9) × (－10) × (－11) × (－12) = ？
```

兩者都能產生高品質的變型題目。

---

## 費用試算

### 場景 A：個人使用（每週出 2 次，每次 20 題）

| 服務 | 月費用 |
|------|-------|
| Gemini | **$0** |
| OpenAI | ~$0.40 |

### 場景 B：補習班使用（每天出 5 次，每次 30 題）

| 服務 | 月費用 |
|------|-------|
| Gemini | **$0**（可能偶爾超過免費額度） |
| OpenAI | ~$22.50 |

### 場景 C：大量題庫建立（一次生成 1000 題）

| 服務 | 費用 |
|------|-----|
| Gemini | **$0**（分批生成，每批 15 題） |
| OpenAI | ~$2.50 |

---

## 切換方式

### 從 Gemini 切換到 OpenAI

```bash
# 編輯 backend/.env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-你的key

# 重啟
./stop-dev.sh && ./start-dev.sh
```

### 從 OpenAI 切換到 Gemini

```bash
# 編輯 backend/.env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza你的key

# 重啟
./stop-dev.sh && ./start-dev.sh
```

---

## 降級機制

如果**沒有設定任何 API Key**，系統會：

1. ❌ 不使用 LLM 改寫
2. ✅ 改為「選項打亂」（題目文字不變，選項順序隨機）

這樣至少同一題的選項每次位置不同，但題目內容會重複。

---

## 建議

### 個人或學校使用
→ **Gemini**（免費、夠用）

### 補習班或商業使用
→ 先試 **Gemini**，如果超過免費額度再升級 OpenAI

### 企業級應用
→ **OpenAI**（穩定性更高）

---

## 技術細節

兩者都在 `backend/main.py` 的 `_rewrite_question_with_llm()` 函式中實作。

### Gemini API 調用
```python
response = gemini_model.generate_content(
    prompt,
    generation_config=genai.types.GenerationConfig(
        temperature=0.8,
        max_output_tokens=1000,
    )
)
```

### OpenAI API 調用
```python
response = openai_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.8,
    max_tokens=1000,
)
```

---

## 相關文件

- 📄 `README-GEMINI.md` - Gemini 快速開始
- 📄 `SETUP-API-KEY.md` - 完整設定教學
- 📄 `docs/llm-variation-setup.md` - OpenAI 詳細說明
- 📄 `docs/variation-implementation.md` - 技術實作細節
