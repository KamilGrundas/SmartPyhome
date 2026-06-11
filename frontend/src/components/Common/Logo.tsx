import { Link } from "@tanstack/react-router"
import { Home } from "lucide-react"

import { cn } from "@/lib/utils"

interface LogoProps {
  variant?: "full" | "icon" | "responsive"
  className?: string
  asLink?: boolean
}

export function Logo({
  variant = "full",
  className,
  asLink = true,
}: LogoProps) {
  const iconEl = (
    <Home className={cn("size-5 shrink-0", variant === "full" && "size-6")} />
  )

  const content =
    variant === "icon" ? (
      <span className={cn("flex items-center", className)}>{iconEl}</span>
    ) : variant === "responsive" ? (
      <>
        <span className="flex items-center gap-2 font-semibold group-data-[collapsible=icon]:hidden">
          {iconEl}
          <span>SmartPyhome</span>
        </span>
        <span className="hidden group-data-[collapsible=icon]:flex items-center">
          {iconEl}
        </span>
      </>
    ) : (
      <span className={cn("flex items-center gap-2 font-semibold text-xl", className)}>
        {iconEl}
        <span>SmartPyhome</span>
      </span>
    )

  if (!asLink) {
    return content
  }

  return <Link to="/">{content}</Link>
}
