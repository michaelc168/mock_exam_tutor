"use client"

import { useState } from "react"
import { PlanCard } from "@/components/plan-card"
import type { PlanCardProps } from "@/components/plan-card"
import { BrainCircuit, BookOpen, Languages, Calculator, RotateCcw, Loader2, CheckCircle } from "lucide-react"
import { apiClient } from "@/lib/api"
import Link from "next/link"

export default function Page() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const handleGenerateExam = async (subject: string, numQuestions: number) => {
    try {
      setLoading(true)
      setMessage(null)

      const response = await apiClient.generateExam({
        subject,
        num_questions: numQuestions,
        difficulty: 'medium',
      })

      setMessage({
        type: 'success',
        text: `考卷生成成功！檔名：${response.filename}`,
      })

      // 3 秒後跳轉到考卷列表
      setTimeout(() => {
        window.location.href = '/exams'
      }, 2000)
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : '生成失敗，請稍後再試',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateMixedExam = async () => {
    try {
      setLoading(true)
      setMessage(null)

      const response = await apiClient.generateMixedExam({
        chinese_count: 20,
        english_count: 20,
        math_count: 40,
      })

      setMessage({
        type: 'success',
        text: `綜合考卷生成成功！共 ${response.total_questions} 題`,
      })

      setTimeout(() => {
        window.location.href = '/exams'
      }, 2000)
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : '生成失敗，請稍後再試',
      })
    } finally {
      setLoading(false)
    }
  }

  const plans: PlanCardProps[] = [
    {
      title: "國語科",
      description: "AI 智能改寫國語題庫，產出全新變型題目，鞏固閱讀理解與語文能力。",
      features: ["從題庫智能出題", "AI 改寫內容，非直接複製", "涵蓋字詞、閱讀、寫作"],
      icon: <BookOpen className="h-6 w-6" />,
      buttonLabel: "開始出題",
      onClick: () => handleGenerateExam('chinese', 20),
    },
    {
      title: "英語科",
      description: "AI 智能改寫英語題庫，針對文法、單字與閱讀產出新題，提升英語實力。",
      features: ["從題庫智能出題", "AI 改寫內容，非直接複製", "涵蓋文法、單字、閱讀"],
      icon: <Languages className="h-6 w-6" />,
      buttonLabel: "開始出題",
      onClick: () => handleGenerateExam('english', 20),
    },
    {
      title: "數學科",
      description: "AI 智能改寫數學題庫，生成同類型但不同數據的練習題，強化運算與邏輯。",
      features: ["從題庫智能出題", "AI 改寫內容，非直接複製", "涵蓋計算、應用、幾何"],
      icon: <Calculator className="h-6 w-6" />,
      buttonLabel: "開始出題",
      onClick: () => handleGenerateExam('math', 40),
    },
    {
      title: "錯題變型加強版",
      description: "從你的錯題出發，AI 自動生成變型題，確認你真正搞懂而非死背答案。",
      features: ["從你的錯題中出變型題", "確保真的搞懂，不是死背答案", "跨科目錯題智能追蹤"],
      icon: <RotateCcw className="h-6 w-6" />,
      featured: true,
      badge: "最受歡迎",
      buttonLabel: "立即體驗",
      onClick: handleGenerateMixedExam,
    },
  ]

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <BrainCircuit className="h-7 w-7 text-primary" />
            <span className="text-lg font-bold text-foreground">AI 智能出題平台</span>
          </div>
          <Link
            href="/exams"
            className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90"
          >
            我的考卷
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="mx-auto max-w-7xl px-6 py-16 text-center">
        <span className="mb-4 inline-block rounded-full bg-primary/10 px-4 py-1.5 text-xs font-semibold text-primary">
          {"選擇適合你的學習方案"}
        </span>
        <h1 className="mb-4 text-3xl font-bold text-foreground md:text-4xl lg:text-5xl text-balance">
          {"AI 幫你出題，學習更高效"}
        </h1>
        <p className="mx-auto max-w-2xl text-base leading-relaxed text-muted-foreground md:text-lg">
          {"不再死背答案。智能出題系統根據題庫 AI 改寫全新題目，讓每次練習都有新挑戰。"}
        </p>
      </section>

      {/* Loading/Success Message */}
      {loading && (
        <div className="mx-auto mb-6 flex max-w-2xl items-center justify-center gap-3 rounded-lg bg-blue-50 px-6 py-4 text-blue-700">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span className="font-semibold">正在生成考卷...</span>
        </div>
      )}

      {message && (
        <div
          className={`mx-auto mb-6 flex max-w-2xl items-center justify-center gap-3 rounded-lg px-6 py-4 ${
            message.type === 'success'
              ? 'bg-green-50 text-green-700'
              : 'bg-red-50 text-red-700'
          }`}
        >
          {message.type === 'success' && <CheckCircle className="h-5 w-5" />}
          <span className="font-semibold">{message.text}</span>
        </div>
      )}

      {/* Plans Grid */}
      <section className="mx-auto max-w-7xl px-6 pb-20">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {plans.map((plan) => (
            <PlanCard key={plan.title} {...plan} />
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-card py-8 text-center text-sm text-muted-foreground">
        <p>{"© 2026 AI 智能出題平台. All rights reserved."}</p>
      </footer>
    </main>
  )
}
