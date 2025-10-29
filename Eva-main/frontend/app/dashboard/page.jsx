"use client"

import ChatSection from '@/components/Chat'
import React, { useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'

export default function Page() {
  const router = useRouter()
  const timerRef = useRef(null)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const INACTIVITY_MS = 30000
    const events = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll', 'click']

    const clearTimer = () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
        timerRef.current = null
      }
    }

    const startTimer = () => {
      clearTimer()
      timerRef.current = setTimeout(() => {
        router.push('/')
      }, INACTIVITY_MS)
    }
    const reset = () => startTimer()
    events.forEach((ev) => window.addEventListener(ev, reset, { passive: true }))
    startTimer()
    const handleVisibility = () => {
      if (!document.hidden) startTimer()
    }
    document.addEventListener('visibilitychange', handleVisibility)

    return () => {
      clearTimer()
      events.forEach((ev) => window.removeEventListener(ev, reset))
      document.removeEventListener('visibilitychange', handleVisibility)
    }
  }, [router])

  return (
    <div className='m-10'>
      <ChatSection />
    </div>
  )
}
