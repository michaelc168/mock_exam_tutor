"use client"

import { useEffect, useState } from "react"
import { apiClient, type Exam } from "@/lib/api"
import { BrainCircuit, Download, FileText, Loader2 } from "lucide-react"
import Link from "next/link"

export default function ExamsPage() {
  const [exams, setExams] = useState<Exam[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadExams()
  }, [])

  const loadExams = async () => {
    try {
      setLoading(true)
      const response = await apiClient.listExams()
      setExams(response.exams)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : '載入失敗')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (isoString: string) => {
    return new Date(isoString).toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2">
            <BrainCircuit className="h-7 w-7 text-primary" />
            <span className="text-lg font-bold text-foreground">AI 智能出題平台</span>
          </Link>
          <button
            onClick={loadExams}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90"
          >
            重新載入
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-12">
        <h1 className="mb-8 text-3xl font-bold text-foreground">我的考卷</h1>

        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
            <p className="font-semibold">載入失敗</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {!loading && !error && exams.length === 0 && (
          <div className="rounded-lg border border-border bg-card p-12 text-center">
            <FileText className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
            <p className="text-lg font-semibold text-foreground">還沒有考卷</p>
            <p className="mt-2 text-sm text-muted-foreground">
              回到首頁開始出題吧！
            </p>
            <Link
              href="/"
              className="mt-4 inline-block rounded-lg bg-primary px-6 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90"
            >
              開始出題
            </Link>
          </div>
        )}

        {!loading && !error && exams.length > 0 && (
          <div className="space-y-4">
            {exams.map((exam) => (
              <div
                key={exam.exam_id}
                className="flex items-center justify-between rounded-lg border border-border bg-card p-6 transition-shadow hover:shadow-md"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <FileText className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">{exam.filename}</h3>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(exam.created_at)} · {formatFileSize(exam.file_size)}
                      {exam.has_pdf && " · 含 PDF"}
                    </p>
                  </div>
                </div>

                <a
                  href={apiClient.getDownloadUrl(exam.exam_id)}
                  download
                  className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90"
                >
                  <Download className="h-4 w-4" />
                  下載
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
