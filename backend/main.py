"""
FastAPI Backend for Mock Exam Tutor
整合現有的考題系統，提供 API 給前端使用
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from datetime import datetime
import subprocess
import pathlib

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
    """計算題庫中的題目數量"""
    bank_path = get_subject_bank_path(subject)
    if not bank_path.exists():
        return 0
    
    with open(bank_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 簡單計算 ## 題目 的數量
        return content.count('## 題目')

def generate_exam_with_ai(request: ExamRequest) -> str:
    """使用 AI 生成考卷（模擬）"""
    # 這裡可以整合 Cursor 的規則，或直接呼叫 AI API
    # 現在先用簡單的方式生成檔名
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"exam-{request.subject}-{timestamp}.md"
    return filename

def generate_mixed_exam_with_ai(request: MixedExamRequest) -> str:
    """生成綜合考卷"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"mock-exam-{timestamp}-comprehensive.md"
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
