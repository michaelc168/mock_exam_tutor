"""
FastAPI Backend for Mock Exam Tutor
整合現有的考題系統，提供 API 給前端使用
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import re
import json
import random
from datetime import datetime
import subprocess
import pathlib
from exam_parser import parse_exam_file
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# LLM API for question variation (支援 Gemini 或 OpenAI)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()  # 預設用 Gemini

# Gemini (Google)
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        # 使用最新的 Gemini 2.5 Flash 模型
        gemini_model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        gemini_model = None
except ImportError:
    gemini_model = None
except Exception as e:
    print(f"Gemini 初始化錯誤: {e}")
    gemini_model = None

# OpenAI
try:
    from openai import OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    if OPENAI_API_KEY:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    else:
        openai_client = None
except ImportError:
    openai_client = None

app = FastAPI(title="Mock Exam Tutor API", version="1.0.0")

# 允許前端跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js 預設端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路徑設定
BASE_DIR = pathlib.Path(__file__).parent.parent
EXAMS_DIR = BASE_DIR / "exams"
BANK_DIR = EXAMS_DIR / "bank"
GENERATED_DIR = EXAMS_DIR / "generated"
TEMPLATES_DIR = EXAMS_DIR / "templates"
IMAGES_DIR = EXAMS_DIR / "images"

# ==================== 資料模型 ====================

class ExamRequest(BaseModel):
    """出題請求"""
    subject: str  # "chinese", "english", "math", "mixed"
    num_questions: int
    difficulty: Optional[str] = "medium"  # "easy", "medium", "hard"
    
class MixedExamRequest(BaseModel):
    """綜合考題請求"""
    chinese_count: int = 0
    english_count: int = 0
    math_count: int = 0
    
class ExamResponse(BaseModel):
    """出題回應"""
    exam_id: str
    filename: str
    total_questions: int
    created_at: str
    download_url: Optional[str] = None
    
class ExamListItem(BaseModel):
    """考卷清單項目"""
    exam_id: str
    filename: str
    created_at: str
    file_size: int
    has_pdf: bool

class QuestionOption(BaseModel):
    """選項"""
    label: str
    text: str

class Question(BaseModel):
    """題目"""
    id: int
    subject: str
    question: str
    options: List[QuestionOption]
    correct_answer: Optional[str] = None

class ExamForQuiz(BaseModel):
    """答題用考卷"""
    exam_id: str
    title: str
    subject: str
    questions: List[Question]
    total_questions: int

class QuizAnswer(BaseModel):
    """答題記錄"""
    question_id: int
    user_answer: str

class SubmitQuizRequest(BaseModel):
    """提交答案請求"""
    exam_id: str
    answers: List[QuizAnswer]

class QuizResult(BaseModel):
    """答題結果"""
    exam_id: str
    subject: str
    total_questions: int
    correct_count: int
    score: int
    answers: List[dict]

# ==================== 輔助函數 ====================

def get_subject_bank_path(subject: str) -> pathlib.Path:
    """取得科目題庫路徑"""
    mapping = {
        "chinese": "chinese-gr6-bank.md",
        "english": "english-gr6-bank.md",
        "math": "math-gr6-bank.md",
    }
    return BANK_DIR / mapping.get(subject, "")

def count_questions_in_bank(subject: str) -> int:
    """計算題庫中的題目數量（### 題號 格式）"""
    bank_path = get_subject_bank_path(subject)
    if not bank_path.exists():
        return 0
    with open(bank_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return len(re.findall(r'\n### \d+\.', content))


def _parse_bank_questions(bank_path: pathlib.Path) -> List[dict]:
    """從題庫檔解析出題目列表，每題為 {question: str, options: [A,B,C,D]}"""
    if not bank_path.exists():
        return []
    with open(bank_path, 'r', encoding='utf-8') as f:
        content = f.read()
    questions = []
    blocks = re.split(r'\n### \d+\.\s*\n', content)
    for block in blocks[1:]:
        block = block.strip()
        if not block:
            continue
        opt_match = re.search(
            r'\n\s*\(A\)\s*(.*?)\n\s*\(B\)\s*(.*?)\n\s*\(C\)\s*(.*?)\n\s*\(D\)\s*(.*)',
            block, re.DOTALL
        )
        if not opt_match:
            continue
        q_text = block[:opt_match.start()].strip()
        opts = [opt_match.group(i).strip() for i in range(1, 5)]
        if q_text and len(opts) == 4:
            questions.append({"question": q_text, "options": opts})
    return questions


def _sample_from_bank(subject: str, num_questions: int) -> List[dict]:
    """從題庫隨機抽題。若題庫不足則重複使用。"""
    bank_path = get_subject_bank_path(subject)
    all_q = _parse_bank_questions(bank_path)
    if not all_q:
        return []
    if num_questions <= len(all_q):
        chosen = random.sample(all_q, num_questions)
    else:
        result = list(all_q)
        while len(result) < num_questions:
            result.append(random.choice(all_q))
        chosen = result[:num_questions]
    # 每題做變型：選項重排 + 數學可做數字變換
    return [_apply_variation(q, subject) for q in chosen]


def _rewrite_question_with_llm(q: dict, subject: str) -> dict:
    """用 LLM 改寫題目：同概念、同難度，但新措辭、新數字、新情境。"""
    subject_label = {"chinese": "國語", "english": "英語", "math": "數學"}[subject]
    q_text = q.get("question", "")
    opts = q.get("options", [])
    
    prompt = f"""你是私立國中入學考題的出題專家。請將以下題目「改寫/變型」：

**原題**（{subject_label}科）：
{q_text}

(A) {opts[0] if len(opts) > 0 else ""}
(B) {opts[1] if len(opts) > 1 else ""}
(C) {opts[2] if len(opts) > 2 else ""}
(D) {opts[3] if len(opts) > 3 else ""}

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
    
    try:
        content = ""
        
        # 優先使用 Gemini（免費額度更高）
        if LLM_PROVIDER == "gemini" and gemini_model:
            # 設定較寬鬆的安全設定（避免內容被過濾）
            safety_settings = {
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            }
            
            response = gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
                    # 不設置 max_output_tokens，避免 deprecated SDK 的 bug
                ),
                safety_settings=safety_settings
            )
            
            # 檢查回應狀態
            if response.prompt_feedback.block_reason:
                print(f"[WARNING] Gemini 回應被阻擋: {response.prompt_feedback.block_reason}")
                return _shuffle_options_fallback(q)
            
            content = response.text.strip()
        
        # 備用 OpenAI
        elif LLM_PROVIDER == "openai" and openai_client:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=1000,
            )
            content = response.choices[0].message.content.strip()
        
        # 無任何 API key
        else:
            print(f"無可用的 LLM API (provider={LLM_PROVIDER})，降級為選項打亂")
            return _shuffle_options_fallback(q)
        
        # 去除可能的 markdown code block 標記
        content = content.strip()
        if content.startswith("```"):
            # 移除開頭的 ```json 或 ```
            content = re.sub(r'^```(?:json)?\s*\n', '', content)
            # 移除結尾的 ```
            content = re.sub(r'\n```\s*$', '', content)
        content = content.strip()
        
        # Debug: 可選的調試輸出
        # print(f"[DEBUG] 內容長度: {len(content)}")
        
        result = json.loads(content)
        
        # 清理選項中可能的 (A)、(B) 等前綴
        cleaned_options = []
        for opt in result.get("options", opts):
            # 移除開頭的 (A)、(B)、(C)、(D) 和空格
            cleaned = re.sub(r'^\([A-D]\)\s*', '', str(opt)).strip()
            cleaned_options.append(cleaned)
        
        return {
            "question": result.get("question", q_text),
            "options": cleaned_options if cleaned_options else opts,
            "correct_answer": result.get("correct_answer", "A"),
        }
    
    except Exception as e:
        print(f"LLM 改寫失敗: {e}，使用原題並打亂選項")
        return _shuffle_options_fallback(q)


def _shuffle_options_fallback(q: dict) -> dict:
    """備案：打亂選項順序（假設第一項為正確）。"""
    opts = list(q.get("options", []))
    if len(opts) != 4:
        return {**q, "correct_answer": "A"}
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


def _apply_variation(q: dict, subject: str) -> dict:
    """對單題做變型：優先用 LLM 改寫，無 API key 時改為選項打亂。"""
    return _rewrite_question_with_llm(q, subject)

def _write_exam_file(
    filepath: pathlib.Path,
    title: str,
    subject_label: str,
    questions: List[dict],
) -> None:
    """將考卷寫入 exams/generated/，題目來自題庫或佔位"""
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    subject_map = {"國語科": "一、國語科", "英語科": "二、英語科", "數學科": "三、數學科"}
    section = subject_map.get(subject_label, "題目區")
    lines = [
        f"# {title}",
        "",
        "- 年級：小六升國一",
        f"- 科目：{subject_label}",
        "- 測驗時間：50 分鐘",
        "- 滿分：100 分",
        "",
        "---",
        "",
        f"## {section}",
        "",
        "### 題目區",
        "",
    ]
    for i, q in enumerate(questions, 1):
        lines.append(f"{i}. {q.get('question', '（題目待補充）')}<br>")
        lines.append("")
        opts = q.get("options", ["選項 A", "選項 B", "選項 C", "選項 D"])
        for label, text in zip(["A", "B", "C", "D"], opts):
            lines.append(f"   ({label}) {text}")
        lines.append("")
    lines.extend([
        "---",
        "",
        "## 參考答案",
        "",
        "| 題號 | 答案 | 配分 | 考點 |",
        "|------|------|------|------|",
    ])
    for i, q in enumerate(questions, 1):
        ans = q.get("correct_answer", "A")
        lines.append(f"| {i} | ({ans}) | 2 | 題庫出題 |")
    content = "\n".join(lines)
    filepath.write_text(content, encoding="utf-8")


def generate_exam_with_ai(request: ExamRequest) -> str:
    """從題庫抽題生成考卷，並寫入檔案"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"exam-{request.subject}-{timestamp}.md"
    filepath = GENERATED_DIR / filename
    subject_label = {"chinese": "國語科", "english": "英語科", "math": "數學科"}[request.subject]
    title = f"私立國中入學模擬考 - {subject_label}"
    questions = _sample_from_bank(request.subject, request.num_questions)
    if not questions:
        # 題庫無題目時寫入佔位
        questions = [
            {"question": "（題目內容請由題庫或 AI 工作流程補充）", "options": ["選項 A", "選項 B", "選項 C", "選項 D"]}
            for _ in range(min(request.num_questions, 50))
        ]
    _write_exam_file(filepath, title, subject_label, questions)
    return filename


def generate_mixed_exam_with_ai(request: MixedExamRequest) -> str:
    """從題庫抽題生成綜合考卷（國語+英語+數學）"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"mock-exam-{timestamp}-comprehensive.md"
    filepath = GENERATED_DIR / filename
    title = "私立國中入學模擬考 - 綜合版"
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    chinese_q = _sample_from_bank("chinese", request.chinese_count)
    english_q = _sample_from_bank("english", request.english_count)
    math_q = _sample_from_bank("math", request.math_count)

    def placeholder_list(n: int) -> List[dict]:
        return [
            {"question": "（題目待補充）", "options": ["選項 A", "選項 B", "選項 C", "選項 D"]}
            for _ in range(n)
        ]
    if not chinese_q and request.chinese_count:
        chinese_q = placeholder_list(request.chinese_count)
    if not english_q and request.english_count:
        english_q = placeholder_list(request.english_count)
    if not math_q and request.math_count:
        math_q = placeholder_list(request.math_count)

    n_ch, n_en, n_math = len(chinese_q), len(english_q), len(math_q)
    total = n_ch + n_en + n_math
    lines = [
        f"# {title}",
        "",
        "- 年級：小六升國一",
        "- 科目：國語、英語、數學",
        "- 測驗時間：80 分鐘",
        "- 滿分：100 分",
        "",
        "---",
        "",
        "## 一、國語科",
        "",
        "### 題目區",
        "",
    ]
    for i, q in enumerate(chinese_q, 1):
        lines.append(f"{i}. {q.get('question', '（題目待補充）')}<br>")
        lines.append("")
        for label, text in zip(["A", "B", "C", "D"], q.get("options", ["選項 A", "選項 B", "選項 C", "選項 D"])):
            lines.append(f"   ({label}) {text}")
        lines.append("")
    lines.extend(["---", "", "## 二、英語科", "", "### 題目區", ""])
    for i, q in enumerate(english_q, n_ch + 1):
        lines.append(f"{i}. {q.get('question', '（題目待補充）')}<br>")
        lines.append("")
        for label, text in zip(["A", "B", "C", "D"], q.get("options", ["選項 A", "選項 B", "選項 C", "選項 D"])):
            lines.append(f"   ({label}) {text}")
        lines.append("")
    lines.extend(["---", "", "## 三、數學科", "", "### 題目區", ""])
    start_math = n_ch + n_en + 1
    for i, q in enumerate(math_q, start_math):
        lines.append(f"{i}. {q.get('question', '（題目待補充）')}<br>")
        lines.append("")
        for label, text in zip(["A", "B", "C", "D"], q.get("options", ["選項 A", "選項 B", "選項 C", "選項 D"])):
            lines.append(f"   ({label}) {text}")
        lines.append("")
    lines.extend([
        "---",
        "",
        "## 參考答案",
        "",
        "### 國語科答案",
        "",
        "| 題號 | 答案 | 配分 | 考點 |",
        "|------|------|------|------|",
    ])
    for i, q in enumerate(chinese_q, 1):
        ans = q.get("correct_answer", "A")
        lines.append(f"| {i} | ({ans}) | 2 | 題庫出題 |")
    lines.extend(["", "### 英語科答案", "", "| 題號 | 答案 | 配分 | 考點 |", "|------|------|------|------|"])
    for i, q in enumerate(english_q, n_ch + 1):
        ans = q.get("correct_answer", "A")
        lines.append(f"| {i} | ({ans}) | 2 | 題庫出題 |")
    lines.extend(["", "### 數學科答案", "", "| 題號 | 答案 | 配分 | 考點 |", "|------|------|------|------|"])
    for i, q in enumerate(math_q, start_math):
        ans = q.get("correct_answer", "A")
        lines.append(f"| {i} | ({ans}) | 2 | 題庫出題 |")
    filepath.write_text("\n".join(lines), encoding="utf-8")
    return filename

# ==================== API 端點 ====================

@app.get("/")
async def root():
    """健康檢查"""
    return {
        "status": "ok",
        "message": "Mock Exam Tutor API is running",
        "version": "1.0.0"
    }

@app.get("/api/subjects")
async def get_subjects():
    """取得所有科目資訊"""
    subjects = []
    
    for subject in ["chinese", "english", "math"]:
        bank_path = get_subject_bank_path(subject)
        question_count = count_questions_in_bank(subject)
        
        subjects.append({
            "id": subject,
            "name": {"chinese": "國語", "english": "英語", "math": "數學"}[subject],
            "question_count": question_count,
            "available": bank_path.exists()
        })
    
    return {"subjects": subjects}

@app.get("/api/exams")
async def list_exams():
    """列出所有已生成的考卷"""
    if not GENERATED_DIR.exists():
        return {"exams": []}
    
    exams = []
    for md_file in GENERATED_DIR.glob("*.md"):
        pdf_file = md_file.with_suffix('.pdf')
        stat = md_file.stat()
        
        exams.append(ExamListItem(
            exam_id=md_file.stem,
            filename=md_file.name,
            created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            file_size=stat.st_size,
            has_pdf=pdf_file.exists()
        ))
    
    # 按時間排序（最新的在前）
    exams.sort(key=lambda x: x.created_at, reverse=True)
    
    return {"exams": exams}

@app.get("/api/exams/{exam_id}")
async def get_exam(exam_id: str):
    """取得特定考卷的內容"""
    md_file = GENERATED_DIR / f"{exam_id}.md"
    
    if not md_file.exists():
        raise HTTPException(status_code=404, detail="考卷不存在")
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pdf_file = md_file.with_suffix('.pdf')
    
    return {
        "exam_id": exam_id,
        "content": content,
        "has_pdf": pdf_file.exists(),
        "created_at": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
    }

@app.post("/api/exams/generate", response_model=ExamResponse)
async def generate_exam(request: ExamRequest):
    """生成單科考卷"""
    # 驗證科目
    if request.subject not in ["chinese", "english", "math"]:
        raise HTTPException(status_code=400, detail="不支援的科目")
    
    # 檢查題庫是否存在
    bank_path = get_subject_bank_path(request.subject)
    if not bank_path.exists():
        raise HTTPException(status_code=404, detail=f"{request.subject} 題庫不存在")
    
    # 生成考卷檔名
    filename = generate_exam_with_ai(request)
    exam_id = pathlib.Path(filename).stem
    
    # 這裡可以呼叫實際的 AI 生成邏輯
    # 暫時返回模擬資料
    
    return ExamResponse(
        exam_id=exam_id,
        filename=filename,
        total_questions=request.num_questions,
        created_at=datetime.now().isoformat(),
        download_url=f"/api/exams/{exam_id}/download"
    )

@app.post("/api/exams/generate-mixed", response_model=ExamResponse)
async def generate_mixed_exam(request: MixedExamRequest):
    """生成綜合考卷（國語 + 英語 + 數學）"""
    total = request.chinese_count + request.english_count + request.math_count
    
    if total == 0:
        raise HTTPException(status_code=400, detail="至少要有一科的題目")
    
    # 生成檔名
    filename = generate_mixed_exam_with_ai(request)
    exam_id = pathlib.Path(filename).stem
    
    # TODO: 整合實際的 AI 生成邏輯
    # 可以透過執行 Node.js 腳本或直接呼叫 AI API
    
    return ExamResponse(
        exam_id=exam_id,
        filename=filename,
        total_questions=total,
        created_at=datetime.now().isoformat(),
        download_url=f"/api/exams/{exam_id}/download"
    )

@app.get("/api/exams/{exam_id}/download")
async def download_exam(exam_id: str):
    """下載考卷（Markdown 或 PDF）"""
    from fastapi.responses import FileResponse
    
    md_file = GENERATED_DIR / f"{exam_id}.md"
    pdf_file = GENERATED_DIR / f"{exam_id}.pdf"
    
    # 優先返回 PDF
    if pdf_file.exists():
        return FileResponse(
            path=pdf_file,
            media_type="application/pdf",
            filename=f"{exam_id}.pdf"
        )
    elif md_file.exists():
        return FileResponse(
            path=md_file,
            media_type="text/markdown",
            filename=f"{exam_id}.md"
        )
    else:
        raise HTTPException(status_code=404, detail="考卷不存在")

@app.post("/api/exams/{exam_id}/generate-pdf")
async def generate_pdf(exam_id: str):
    """為考卷生成 PDF"""
    md_file = GENERATED_DIR / f"{exam_id}.md"
    
    if not md_file.exists():
        raise HTTPException(status_code=404, detail="考卷不存在")
    
    # 執行 PDF 轉換腳本
    script_path = BASE_DIR / "scripts" / "convert-to-pdf.js"
    
    try:
        result = subprocess.run(
            ["node", str(script_path), str(md_file)],
            capture_output=True,
            text=True,
            check=True
        )
        
        pdf_file = md_file.with_suffix('.pdf')
        
        return {
            "success": True,
            "exam_id": exam_id,
            "pdf_path": str(pdf_file),
            "message": "PDF 生成成功"
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF 生成失敗: {e.stderr}"
        )

@app.get("/api/stats")
async def get_stats():
    """取得統計資訊"""
    stats = {
        "total_exams": len(list(GENERATED_DIR.glob("*.md"))) if GENERATED_DIR.exists() else 0,
        "total_pdfs": len(list(GENERATED_DIR.glob("*.pdf"))) if GENERATED_DIR.exists() else 0,
        "subjects": {}
    }
    
    for subject in ["chinese", "english", "math"]:
        stats["subjects"][subject] = {
            "name": {"chinese": "國語", "english": "英語", "math": "數學"}[subject],
            "question_count": count_questions_in_bank(subject)
        }
    
    return stats

@app.get("/api/quiz/{exam_id}", response_model=ExamForQuiz)
async def get_exam_for_quiz(exam_id: str):
    """取得考卷資料供答題使用（不包含答案）"""
    md_file = GENERATED_DIR / f"{exam_id}.md"
    
    if not md_file.exists():
        raise HTTPException(status_code=404, detail="考卷不存在")
    
    # 解析考卷
    exam_data = parse_exam_file(md_file)
    if not exam_data:
        raise HTTPException(status_code=500, detail="考卷解析失敗")
    
    # 移除答案（不要傳給前端）
    questions = []
    for q in exam_data['questions']:
        # 建立不含答案的題目
        questions.append(Question(
            id=q['id'],
            subject=q['subject'],
            question=q['question'],
            options=[
                QuestionOption(label=opt['label'], text=opt['text'])
                for opt in q['options']
            ]
        ))
    
    return ExamForQuiz(
        exam_id=exam_id,
        title=exam_data['title'],
        subject=exam_data['subject'],
        total_questions=exam_data['total_questions'],
        questions=questions
    )

@app.get("/api/images/{filename}")
async def get_image(filename: str):
    """取得考卷圖片"""
    image_path = IMAGES_DIR / filename
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="圖片不存在")
    
    return FileResponse(image_path)

@app.post("/api/quiz/submit", response_model=QuizResult)
async def submit_quiz(request: SubmitQuizRequest):
    """提交答案並評分"""
    md_file = GENERATED_DIR / f"{request.exam_id}.md"
    
    if not md_file.exists():
        raise HTTPException(status_code=404, detail="考卷不存在")
    
    # 解析考卷（含答案）
    exam_data = parse_exam_file(md_file)
    if not exam_data:
        raise HTTPException(status_code=500, detail="考卷解析失敗")
    
    # 建立答案對照表
    user_answers_dict = {ans.question_id: ans.user_answer for ans in request.answers}
    
    # 評分
    correct_count = 0
    answer_details = []
    
    for q in exam_data['questions']:
        q_id = q['id']
        correct_ans = q.get('correct_answer', '')
        user_ans = user_answers_dict.get(q_id, '')
        is_correct = user_ans == correct_ans
        
        if is_correct:
            correct_count += 1
        
        answer_details.append({
            'question_id': q_id,
            'question': q['question'],
            'user_answer': user_ans,
            'correct_answer': correct_ans,
            'is_correct': is_correct
        })
    
    total = exam_data['total_questions']
    score = int((correct_count / total) * 100) if total > 0 else 0
    
    return QuizResult(
        exam_id=request.exam_id,
        subject=exam_data['subject'],
        total_questions=total,
        correct_count=correct_count,
        score=score,
        answers=answer_details
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
