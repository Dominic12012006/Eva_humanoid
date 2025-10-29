import React from 'react'
import { Button as ShadcnButton } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export default function GlowingButton({ children, className, ...props }) {
  return (
    <ShadcnButton
      className={cn(
        "relative overflow-hidden group",
        "before:absolute before:inset-0 before:bg-gradient-to-r before:from-primary/50 before:via-primary/80 before:to-primary/50",
        "before:animate-glow before:blur-xl before:opacity-75 before:-z-10",
        "hover:before:opacity-100 transition-all duration-300",
        className
      )}
      {...props}
    >
      Go to dashboard 
    </ShadcnButton>
  )
}
