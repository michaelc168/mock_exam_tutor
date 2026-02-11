"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { BrainCircuit, CheckCircle, XCircle, Trophy } from "lucide-react"
import Link from "next/link"
import { LatexRenderer } from "@/components/latex-renderer"

interface ResultData {
  exam_id: string
  subject: string
  total_questions: number
  correct_count: number
  score: number
  answers: Array<{
    question_id: number
    question: string
    user_answer: string
    correct_answer: string
    is_correct: boolean
  }>
}

export default function ResultPage() {
  const params = useParams()
  const examId = params.examId as string

  const [result, setResult] = useState<ResultData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadResult()
  }, [examId])

  const loadResult = async () => {
    try {
      setLoading(true)
      
      // 從 localStorage 讀取結果（由答題頁面存入）
      const storedResult = localStorage.getItem(`quiz_result_${examId}`)
      if (storedResult) {
        const parsedResult = JSON.parse(storedResult)
        setResult(parsedResult)
      } else {
        alert('找不到測驗結果')
      }
      
      setLoading(false)
    } catch (error) {
      console.error('載入結果失敗:', error)
      alert('載入結果失敗')
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="mt-4 text-muted-foreground">計算成績中...</p>
        </div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">找不到結果</p>
      </div>
    )
  }

  const percentage = (result.correct_count / result.total_questions) * 100

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex max-w-7xl items-center gap-2 px-6 py-4">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80">
            <BrainCircuit className="h-7 w-7 text-primary" />
            <span className="text-lg font-bold text-foreground">AI 智能出題平台</span>
          </Link>
        </div>
      </header>

      <div className="mx-auto max-w-4xl px-6 py-12">
        {/* Score Card */}
        <div className="mb-8 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 p-8 text-center text-white shadow-xl">
          <Trophy className="mx-auto mb-4 h-16 w-16" />
          <h1 className="mb-2 text-3xl font-bold">測驗完成！</h1>
          <p className="mb-6 text-blue-100">{result.subject}</p>
          
          <div className="mb-4 text-6xl font-bold">{result.score} 分</div>
          
          <div className="flex items-center justify-center gap-8 text-sm">
            <div>
              <div className="text-2xl font-bold">{result.correct_count}</div>
              <div className="text-blue-200">答對</div>
            </div>
            <div className="h-8 w-px bg-white/30"></div>
            <div>
              <div className="text-2xl font-bold">{result.total_questions - result.correct_count}</div>
              <div className="text-blue-200">答錯</div>
            </div>
            <div className="h-8 w-px bg-white/30"></div>
            <div>
              <div className="text-2xl font-bold">{percentage.toFixed(0)}%</div>
              <div className="text-blue-200">正確率</div>
            </div>
          </div>
        </div>

        {/* Answer Review */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-foreground">答案檢討</h2>
          
          {result.answers.map((answer, index) => (
            <div
              key={answer.question_id}
              className={`
                rounded-lg border-2 p-6
                ${
                  answer.is_correct
                    ? "border-green-200 bg-green-50"
                    : "border-red-200 bg-red-50"
                }
              `}
            >
              <div className="mb-4 flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-foreground">第 {index + 1} 題</span>
                  {answer.is_correct ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                </div>
                <span
                  className={`
                    rounded-full px-3 py-1 text-xs font-semibold
                    ${
                      answer.is_correct
                        ? "bg-green-600 text-white"
                        : "bg-red-600 text-white"
                    }
                  `}
                >
                  {answer.is_correct ? "答對" : "答錯"}
                </span>
              </div>

              <p className="mb-4 text-foreground">
                <LatexRenderer content={answer.question} />
              </p>

              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-muted-foreground">你的答案：</span>
                  <span
                    className={answer.is_correct ? "text-green-700" : "text-red-700"}
                  >
                    ({answer.user_answer})
                  </span>
                </div>
                {!answer.is_correct && (
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-muted-foreground">正確答案：</span>
                    <span className="text-green-700">({answer.correct_answer})</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="mt-8 flex gap-4">
          <Link
            href="/"
            className="flex-1 rounded-lg border-2 border-primary bg-white px-6 py-3 text-center font-semibold text-primary hover:bg-primary/5"
          >
            返回首頁
          </Link>
          <Link
            href={`/exams`}
            className="flex-1 rounded-lg bg-primary px-6 py-3 text-center font-semibold text-white hover:opacity-90"
          >
            查看所有考卷
          </Link>
        </div>
      </div>
    </main>
  )
}
