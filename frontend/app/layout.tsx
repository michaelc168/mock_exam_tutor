import React from "react"
import type { Metadata, Viewport } from 'next'
import { Noto_Sans_TC } from 'next/font/google'

import './globals.css'

const notoSansTC = Noto_Sans_TC({ subsets: ['latin'], weight: ['400', '500', '600', '700'] })

export const metadata: Metadata = {
  title: 'AI 智能出題平台 | 選擇你的學習方案',
  description: 'AI 智能出題平台，從題庫智能出題、錯題變型練習，幫助你高效學習。',
}

export const viewport: Viewport = {
  themeColor: '#3b82f6',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-TW">
      <body className={`${notoSansTC.className} antialiased`}>{children}</body>
    </html>
  )
}
