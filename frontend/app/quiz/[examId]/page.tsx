"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { BrainCircuit, Clock, ChevronLeft, ChevronRight } from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api"
import { LatexRenderer } from "@/components/latex-renderer"

interface Question {
  id: number
  subject: string
  question: string
  options: {
    label: string
    text: string
  }[]
  correctAnswer: string
}

interface ExamData {
  exam_id: string
  title: string
  subject: string
  questions: Question[]
  total_questions: number
}

export default function QuizPage() {
  const params = useParams()
  const router = useRouter()
  const examId = params.examId as string

  const [examData, setExamData] = useState<ExamData | null>(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadExam()
  }, [examId])

  const loadExam = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getExamForQuiz(examId)
      
      setExamData({
        exam_id: response.exam_id,
        title: response.title,
        subject: response.subject,
        total_questions: response.total_questions,
        questions: response.questions
      })
      setLoading(false)
    } catch (error) {
      console.error('載入考卷失敗:', error)
      alert('載入考卷失敗，請稍後再試')
      setLoading(false)
    }
  }

  const currentQuestion = examData?.questions[currentIndex]

  const handleSelectOption = (optionLabel: string) => {
    setAnswers({
      ...answers,
      [currentIndex]: optionLabel,
    })
  }

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
    }
  }

  const handleNext = () => {
    if (examData && currentIndex < examData.questions.length - 1) {
      setCurrentIndex(currentIndex + 1)
    } else {
      // 最後一題，提交答案
      handleSubmit()
    }
  }

  const handleSubmit = async () => {
    try {
      // 將答案轉換為 API 格式
      const answersList = Object.entries(answers).map(([index, answer]) => ({
        question_id: examData!.questions[parseInt(index)].id,
        user_answer: answer
      }))
      
      // 提交答案
      const result = await apiClient.submitQuiz(examId, answersList)
      
      // 將結果存入 localStorage，供結果頁面讀取
      localStorage.setItem(`quiz_result_${examId}`, JSON.stringify(result))
      
      // 跳轉到結果頁面
      router.push(`/quiz/${examId}/result`)
    } catch (error) {
      console.error('提交答案失敗:', error)
      alert('提交答案失敗，請稍後再試')
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="mt-4 text-muted-foreground">載入中...</p>
        </div>
      </div>
    )
  }

  if (!examData || !currentQuestion) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">找不到考卷</p>
      </div>
    )
  }

  const progress = ((currentIndex + 1) / examData.total_questions) * 100

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80">
            <BrainCircuit className="h-7 w-7 text-primary" />
            <span className="text-lg font-bold text-foreground">AI 智能出題平台</span>
          </Link>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>{currentIndex + 1} / {examData.total_questions}</span>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="h-1 bg-gray-200">
          <div 
            className="h-full bg-primary transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </header>

      {/* Quiz Content */}
      <div className="mx-auto max-w-4xl px-6 py-12">
        {/* Back Button and Subject */}
        <div className="mb-8 flex items-center justify-between">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-muted-foreground hover:text-foreground"
          >
            <ChevronLeft className="h-5 w-5" />
            返回
          </button>
          <h2 className="text-xl font-bold text-foreground">{examData.subject}</h2>
          <div className="w-20"></div> {/* Spacer for centering */}
        </div>

        {/* Question Card */}
        <div className="rounded-xl bg-card p-8 shadow-lg">
          {/* Question Number */}
          <div className="mb-6">
            <span className="inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm font-semibold text-primary">
              第 {currentIndex + 1} 題
            </span>
          </div>

          {/* Question Text */}
          <h3 className="mb-8 text-xl font-medium leading-relaxed text-foreground">
            <LatexRenderer content={currentQuestion.question} />
          </h3>

          {/* Options */}
          <div className="space-y-4">
            {currentQuestion.options.map((option) => {
              const isSelected = answers[currentIndex] === option.label
              
              return (
                <button
                  key={option.label}
                  onClick={() => handleSelectOption(option.label)}
                  className={`
                    w-full rounded-lg border-2 p-4 text-left transition-all duration-200
                    ${
                      isSelected
                        ? "border-primary bg-primary/5"
                        : "border-border bg-background hover:border-primary/50 hover:bg-gray-50"
                    }
                  `}
                >
                  <div className="flex items-start gap-3">
                    <span
                      className={`
                        flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 font-semibold
                        ${
                          isSelected
                            ? "border-primary bg-primary text-white"
                            : "border-gray-300 bg-white text-gray-600"
                        }
                      `}
                    >
                      {option.label}
                    </span>
                    <span className="pt-1 text-base text-foreground">
                      <LatexRenderer content={option.text} />
                    </span>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-8 flex items-center justify-between gap-4">
          {/* Previous Button */}
          <button
            onClick={handlePrevious}
            disabled={currentIndex === 0}
            className={`
              flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition-all whitespace-nowrap flex-shrink-0
              ${
                currentIndex === 0
                  ? "cursor-not-allowed text-muted-foreground"
                  : "text-foreground hover:bg-gray-100"
              }
            `}
          >
            <ChevronLeft className="h-4 w-4" />
            上一題
          </button>

          {/* Progress Dots */}
          <div className="flex items-center justify-center gap-1 overflow-x-auto flex-1 max-w-xl mx-4">
            {examData.questions.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`
                  h-2 rounded-full transition-all duration-300 flex-shrink-0
                  ${
                    index === currentIndex
                      ? "w-8 bg-primary"
                      : answers[index]
                      ? "w-2 bg-primary/60"
                      : "w-2 bg-gray-300"
                  }
                `}
              />
            ))}
          </div>

          {/* Next Button */}
          <button
            onClick={handleNext}
            className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white hover:opacity-90 whitespace-nowrap flex-shrink-0"
          >
            {currentIndex === examData.questions.length - 1 ? "提交答案" : "下一題"}
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </main>
  )
}
