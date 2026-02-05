"use client"

import ChatSection from "../../components/Chat"
import React, { useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { LanguagesIcon, ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function Page() {
  const router = useRouter()
  const timerRef = useRef(null)
  const calledRef = useRef(false)
  const [language, setLanguage] = useState(null)

  const welcome_string = "Hello welcome to srm"

  // ----------------------
  // Send welcome message ONCE
  // ----------------------
  const welcome = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/welcome_text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: welcome_string }),
      })
      if (!res.ok) {
        console.error("Failed to send welcome text:", res.status)
      }
    } catch (e) {
      console.error("Welcome error:", e)
    }
  }

  // ----------------------
  // Inactivity + cleanup logic
  // ----------------------
  useEffect(() => {
    if (!calledRef.current) {
      calledRef.current = true
      welcome()
    }

    if (typeof window === "undefined") return

    const INACTIVITY_MS = 100000
    const events = ["mousemove", "mousedown", "keydown", "touchstart", "scroll", "click"]

    const clearTimer = () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
        timerRef.current = null
      }
    }

    const handleTimeout = async () => {
      console.log("Inactivity timeout → clearing chat DB")

      try {
        await fetch("http://127.0.0.1:8000/delete_questions", {
          method: "DELETE",
        })
        await fetch("http://127.0.0.1:8000/delete_answers", {
          method: "DELETE",
        })
        await fetch("http://127.0.0.1:8000/delete_images", {
          method: "DELETE",
        })
      } catch (e) {
        console.error("Failed to delete chat DB:", e)
      }

      router.push("/")
    }

    const startTimer = () => {
      clearTimer()
      timerRef.current = setTimeout(handleTimeout, INACTIVITY_MS)
    }

    const reset = () => startTimer()

    events.forEach((ev) =>
      window.addEventListener(ev, reset, { passive: true })
    )

    startTimer()

    const handleVisibility = () => {
      if (!document.hidden) startTimer()
    }

    document.addEventListener("visibilitychange", handleVisibility)

    return () => {
      clearTimer()
      events.forEach((ev) =>
        window.removeEventListener(ev, reset)
      )
      document.removeEventListener("visibilitychange", handleVisibility)
    }
  }, [router])


  if (!language) {
    return (
      <div className="relative flex flex-col items-center justify-center h-screen backdrop-blur-sm">
        <div className="relative z-10 text-center space-y-10">
          <h1 className="text-3xl font-semibold drop-shadow-lg">
            Select Your Language
          </h1>

          <div className="grid grid-cols-3 gap-3 justify-center">
            {["English", "Hindi", "Tamil","Malayalam","Telugu","Kannada"].map((lang) => (
              <div
                key={lang}
                onClick={() => setLanguage(lang)}
                className="cursor-pointer flex flex-col items-center justify-center gap-3 w-28 h-28 rounded-full bg-white/10 backdrop-blur-lg border border-white/20 hover:scale-110 transition-transform duration-300"
              >
                <LanguagesIcon className="w-8 h-8" />
                <span className="text-sm font-medium">{lang}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }
  const deleteAllQuestions = async () => {
  await fetch("http://127.0.0.1:8000/delete_questions", { method: "DELETE" })
}

const deleteAllAnswers = async () => {
  await fetch("http://127.0.0.1:8000/delete_answers", { method: "DELETE" })
}
const deleteAllImages = async () => {
  await fetch("http://127.0.0.1:8000/delete_images", { method: "DELETE" })
}

  return (
    <div className="h-full relative">
      <Link href='/'>
       <button
        onClick={()=>{
          deleteAllAnswers()
          deleteAllQuestions()
          deleteAllImages()
        }}
        aria-label="Go to home"
        className="
          fixed mt-4 left-6 z-50
          w-12 h-12
          rounded-full
   backdrop-blur-md
          border border-white/20
          flex items-center justify-center
 
          hover:bg-white/20 hover:scale-105
          active:scale-95
          transition-all duration-200
          shadow-lg
        "
      >
        <ArrowLeft className="w-5 h-5" />
      </button>

      </Link>
     
      <ChatSection language={language} />
    </div>
  )
}
