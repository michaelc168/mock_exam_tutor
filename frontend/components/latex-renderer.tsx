"use client"

import { useEffect, useRef } from 'react'

interface LatexRendererProps {
  content: string
  className?: string
}

// 動態載入 KaTeX
let katexLoaded = false
let katexPromise: Promise<any> | null = null

function loadKatex() {
  if (katexLoaded) return Promise.resolve((window as any).katex)
  if (katexPromise) return katexPromise

  katexPromise = new Promise((resolve, reject) => {
    // 載入 CSS
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css'
    document.head.appendChild(link)

    // 載入 JS
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js'
    script.onload = () => {
      katexLoaded = true
      resolve((window as any).katex)
    }
    script.onerror = reject
    document.head.appendChild(script)
  })

  return katexPromise
}

export function LatexRenderer({ content, className = '' }: LatexRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    loadKatex().then((katex) => {
      if (!containerRef.current) return

      // 處理 LaTeX 公式
      // 支援 $...$ (inline) 和 $$...$$ (display)
      let html = content

      // 先處理圖片（避免被 $ 符號影響）
      // ![描述](../images/xxx.png) -> <img src="http://localhost:8000/api/images/xxx.png" alt="描述" />
      html = html.replace(/!\[([^\]]*)\]\(\.\.\/images\/([^)]+)\)/g, (match, alt, filename) => {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        return `<img src="${apiUrl}/api/images/${filename}" alt="${alt}" class="max-w-[50%] h-auto my-4 mx-auto block" />`
      })

      // 處理 display 模式 $$...$$
      html = html.replace(/\$\$(.*?)\$\$/g, (match, latex) => {
        try {
          return katex.renderToString(latex, {
            displayMode: true,
            throwOnError: false,
          })
        } catch (e) {
          console.error('LaTeX render error:', e)
          return match
        }
      })

      // 處理 inline 模式 $...$
      html = html.replace(/\$(.*?)\$/g, (match, latex) => {
        try {
          return katex.renderToString(latex, {
            displayMode: false,
            throwOnError: false,
          })
        } catch (e) {
          console.error('LaTeX render error:', e)
          return match
        }
      })

      containerRef.current.innerHTML = html
    }).catch((error) => {
      console.error('Failed to load KaTeX:', error)
      if (containerRef.current) {
        containerRef.current.textContent = content
      }
    })
  }, [content])

  return (
    <div
      ref={containerRef}
      className={className}
    />
  )
}
