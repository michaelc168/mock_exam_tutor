"use client"

import { CheckCircle2, Sparkles } from "lucide-react"
import type { ReactNode } from "react"

export interface PlanCardProps {
  title: string
  description: string
  features: string[]
  icon: ReactNode
  featured?: boolean
  badge?: string
  buttonLabel: string
  onClick?: () => void
}

export function PlanCard({
  title,
  description,
  features,
  icon,
  featured = false,
  badge,
  buttonLabel,
  onClick,
}: PlanCardProps) {
  return (
    <div
      className={`
        group relative flex flex-col rounded-xl p-6 transition-all duration-300
        hover:-translate-y-2 hover:shadow-xl
        ${
          featured
            ? "bg-gradient-to-br from-blue-600 to-indigo-700 text-white shadow-lg shadow-blue-500/25"
            : "bg-card text-card-foreground shadow-md border border-border"
        }
      `}
    >
      {badge && (
        <span className="absolute -top-3 right-4 inline-flex items-center gap-1 rounded-full bg-amber-400 px-3 py-1 text-xs font-semibold text-amber-950">
          <Sparkles className="h-3 w-3" />
          {badge}
        </span>
      )}

      <div
        className={`mb-4 flex h-12 w-12 items-center justify-center rounded-lg ${
          featured ? "bg-white/20" : "bg-primary/10"
        }`}
      >
        <span className={featured ? "text-white" : "text-primary"}>{icon}</span>
      </div>

      <h3 className="mb-2 text-xl font-bold">{title}</h3>

      <p
        className={`mb-5 text-sm leading-relaxed ${
          featured ? "text-blue-100" : "text-muted-foreground"
        }`}
      >
        {description}
      </p>

      <ul className="mb-6 flex flex-col gap-3">
        {features.map((feature) => (
          <li key={feature} className="flex items-start gap-2 text-sm">
            <CheckCircle2
              className={`mt-0.5 h-4 w-4 shrink-0 ${
                featured ? "text-emerald-300" : "text-emerald-500"
              }`}
            />
            <span className={featured ? "text-blue-50" : "text-card-foreground"}>{feature}</span>
          </li>
        ))}
      </ul>

      <div className="mt-auto">
        <button
          type="button"
          onClick={onClick}
          className={`
            w-full rounded-lg px-4 py-3 text-sm font-semibold transition-all duration-200
            ${
              featured
                ? "bg-white text-blue-700 hover:bg-blue-50 shadow-md"
                : "bg-primary text-primary-foreground hover:opacity-90"
            }
          `}
        >
          {buttonLabel}
        </button>
      </div>
    </div>
  )
}


