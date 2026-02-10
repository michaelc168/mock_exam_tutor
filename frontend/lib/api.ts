/**
 * API Client for Mock Exam Tutor Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface Subject {
  id: string
  name: string
  question_count: number
  available: boolean
}

export interface Exam {
  exam_id: string
  filename: string
  created_at: string
  file_size: number
  has_pdf: boolean
}

export interface ExamRequest {
  subject: string
  num_questions: number
  difficulty?: string
}

export interface MixedExamRequest {
  chinese_count: number
  english_count: number
  math_count: number
}

export interface ExamResponse {
  exam_id: string
  filename: string
  total_questions: number
  created_at: string
  download_url?: string
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || `HTTP ${response.status}`)
      }

      return response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // ==================== API Methods ====================

  async healthCheck() {
    return this.request<{ status: string; message: string; version: string }>('/')
  }

  async getSubjects() {
    return this.request<{ subjects: Subject[] }>('/api/subjects')
  }

  async listExams() {
    return this.request<{ exams: Exam[] }>('/api/exams')
  }

  async getExam(examId: string) {
    return this.request<{ exam_id: string; content: string; has_pdf: boolean; created_at: string }>(
      `/api/exams/${examId}`
    )
  }

  async generateExam(request: ExamRequest) {
    return this.request<ExamResponse>('/api/exams/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async generateMixedExam(request: MixedExamRequest) {
    return this.request<ExamResponse>('/api/exams/generate-mixed', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async generatePdf(examId: string) {
    return this.request<{ success: boolean; exam_id: string; pdf_path: string; message: string }>(
      `/api/exams/${examId}/generate-pdf`,
      { method: 'POST' }
    )
  }

  getDownloadUrl(examId: string) {
    return `${this.baseUrl}/api/exams/${examId}/download`
  }

  async getStats() {
    return this.request<{
      total_exams: number
      total_pdfs: number
      subjects: Record<string, { name: string; question_count: number }>
    }>('/api/stats')
  }
}

export const apiClient = new ApiClient()
