"use client"

import React, { useState, useEffect, useRef } from "react"
import { Send, Mic, MessageSquare } from "lucide-react"
import SiriMic from "../components/SiriMic"

const Input = ({ placeholder, className, value, onChange, onKeyDown }) => (
  <input
    placeholder={placeholder}
    className={`p-3 border rounded-lg flex-1 ${className}`}
    value={value}
    onChange={onChange}
    onKeyDown={onKeyDown}
  />
)

const Button = ({ onClick, children, variant, className }) => (
  <button
    onClick={onClick}
    className={`p-3 rounded-lg transition-colors ${
      variant === "default"
        ? "bg-purple-600 hover:bg-purple-700 text-white"
        : "bg-zinc-700 hover:bg-zinc-600 text-white border border-zinc-600"
    } ${className}`}
  >
    {children}
  </button>
)

const Card = ({ children, className }) => (
  <div className={`p-3 rounded-xl shadow-lg ${className}`}>{children}</div>
)

function TypingDots() {
  return (
    <div className="typing-dots flex items-center gap-1">
      <span className="dot w-2 h-2 rounded-full animate-bounce-slow" />
      <span className="dot w-2 h-2 rounded-full animate-bounce-slow delay-150" />
      <span className="dot w-2 h-2 rounded-full animate-bounce-slow delay-300" />

      <style jsx>{`
        .dot {
          background-color: currentColor;
          opacity: 0.6;
        }
        .animate-bounce-slow {
          animation: bounce 1s infinite ease-in-out;
        }
        .delay-150 {
          animation-delay: 0.15s;
        }
        .delay-300 {
          animation-delay: 0.3s;
        }

        @keyframes bounce {
          0%,
          80%,
          100% {
            transform: translateY(0);
            opacity: 0.6;
          }
          40% {
            transform: translateY(-6px);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  )
}

export default function ChatSectionDemo() {
  const[wakeWord,setWakeword]=useState('Eva')
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState("")
  const [isListening, setIsListening] = useState(false)
  const [isEvaTyping, setIsEvaTyping] = useState(false)
  const chatEndRef = useRef(null)
  const recognitionRef = useRef(null)
  const lastTranscriptRef = useRef("")
  const wakeRecognitionRef = useRef(null)
  const wakePausedRef = useRef(false)
  const activeSessionRef = useRef({ fromWake: false, restartAttempts: 0 })

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isEvaTyping])

  const sleep = (ms) => new Promise((res) => setTimeout(res, ms))

  const handleQuestion = async (questionText) => {
    if (!questionText || !String(questionText).trim()) return

    // show user message
    const userMessage = { sender: "user", text: questionText }
    setMessages((prev) => [...prev, userMessage])
    setQuestion("")
    setIsEvaTyping(true)

    try {
      const res = await fetch("http://127.0.0.1:8000/recieve_response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer: questionText }),
      })

      const data = await res.json()
      const evaText = data?.data || "Sorry, I couldn’t get a response."

      await sleep(500 + Math.random() * 500)

      const evaMessage = { sender: "eva", text: evaText }
      setMessages((prev) => [...prev, evaMessage])
    } catch (err) {
      console.error("Error:", err)
      setMessages((prev) => [
        ...prev,
        { sender: "eva", text: "Error: Could not connect to EVA." },
      ])
    } finally {
      setIsEvaTyping(false)
    }
  }

  const handleMicClick = () => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Voice recognition not supported")
      return
    }
    // Ensure the active (user) recognition exists and toggle it.
    ensureActiveRecognition()

    // Toggle start/stop
    if (isListening) {
      try {
        recognitionRef.current.stop()
      } catch (e) {
        console.warn("Error stopping recognition:", e)
      }
    } else {
      try {
        lastTranscriptRef.current = ""
        recognitionRef.current.start()
      } catch (e) {
        console.warn("Error starting recognition:", e)
      }
    }
}

  // cleanup on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.onresult = null
          recognitionRef.current.onend = null
          recognitionRef.current.onstart = null
          recognitionRef.current.stop()
        } catch (e) {
          // ignore
        }
        recognitionRef.current = null
      }
    }
  }, [])

  const ensureActiveRecognition = () => {
    if (!("webkitSpeechRecognition" in window)) return

    if (!recognitionRef.current) {
      const recognition = new window.webkitSpeechRecognition()
      recognition.lang = ""
      recognition.interimResults = true
      recognition.continuous = true

      recognition.onstart = () => setIsListening(true)

      recognition.onresult = (event) => {
        let interimTranscript = ""
        let finalTranscript = ""

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript + " "
          } else {
            interimTranscript += transcript
          }
        }

        const combined = (finalTranscript + interimTranscript).trim()
        lastTranscriptRef.current = (lastTranscriptRef.current + " " + finalTranscript).trim()
        setQuestion(combined)
      }

      recognition.onend = () => {
        const final = lastTranscriptRef.current?.trim() || ""

        if (activeSessionRef.current.fromWake && final === "" && activeSessionRef.current.restartAttempts < 4) {
          activeSessionRef.current.restartAttempts += 1
          // small delay and try to restart the active recognizer
          setTimeout(() => {
            try {
              recognitionRef.current && recognitionRef.current.start()
            } catch (e) {
              // ignore
            }
          }, 300)
          return
        }

        // Normal end-of-recognition handling: update UI and send final transcript
        setIsListening(false)

        if (final !== "") {
          // clear ref before sending to avoid duplicate sends
          lastTranscriptRef.current = ""
          handleQuestion(final)
        }

  // no modal dialog to hide; transcript is shown in the input field

        // If wake-word listener exists, restart it so background listening resumes.
        // Also clear any wake-paused flag so it may restart.
        try {
          wakePausedRef.current = false
          if (wakeRecognitionRef.current) {
            setTimeout(() => {
              try {
                wakeRecognitionRef.current.start()
              } catch (e) {
              }
            }, 300)
          }
        } catch (e) {
        }
        activeSessionRef.current = { fromWake: false, restartAttempts: 0 }
      }

      recognitionRef.current = recognition
    }
  }
  useEffect(() => {
    if (!("webkitSpeechRecognition" in window)) return
    if (wakeRecognitionRef.current) return

    try {
      const wakeRec = new window.webkitSpeechRecognition()
      wakeRec.lang = "en-US"
      wakeRec.interimResults = true
      wakeRec.continuous = true

      let buffer = ""

      wakeRec.onresult = (event) => {
        let interim = ""
        let final = ""
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const t = event.results[i][0].transcript
          if (event.results[i].isFinal) final += t + " "
          else interim += t
        }

        buffer = (buffer + " " + final + interim).trim().toLowerCase()

        // check for wake word (word boundary)
        const wake = (wakeWord || "eva").toLowerCase()
        const regex = new RegExp("\\b" + wake.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&") + "\\b", "i")

        if (regex.test(buffer)) {
          // trigger visible mic and active recognition
          try {
            // stop wake recognizer briefly to avoid double triggers
            try {
              wakePausedRef.current = true
              wakeRec.stop()
            } catch (e) {}

            ensureActiveRecognition()
            // give active recognizer a moment and then start
            setTimeout(() => {
              try {
                lastTranscriptRef.current = ""
                // mark this session as originating from wake-word
                activeSessionRef.current = { fromWake: true, restartAttempts: 0 }
                recognitionRef.current.start()
              } catch (e) {
                console.warn("Failed to start active recognition after wake:", e)
              }
            }, 120)
          } catch (e) {
            console.warn("Wake trigger error:", e)
          }

          // clear buffer after detection
          buffer = ""
        }
      }

      wakeRec.onend = () => {
        // Only auto-restart the wake recognizer if we haven't been asked to pause it
        try {
          if (wakePausedRef.current) return
          setTimeout(() => {
            try {
              wakeRec.start()
            } catch (e) {
            }
          }, 500)
        } catch (e) {

        }
      }

      wakeRecognitionRef.current = wakeRec

      try {
        wakeRec.start()
      } catch (e) {
   

        console.warn("Unable to start wake-word recognition automatically:", e)
      }
    } catch (e) {
      console.warn("Wake-word setup failed:", e)
    }

    return () => {
      if (wakeRecognitionRef.current) {
        try {
          wakeRecognitionRef.current.onresult = null
          wakeRecognitionRef.current.onend = null
          wakeRecognitionRef.current.stop()
        } catch (e) {
        }
        wakeRecognitionRef.current = null
      }
    }
  }, [wakeWord])

  // Dialog handlers removed: transcript is shown in the chat input and recognition controls are on the mic button


const renderMessage = (msg, i) => {
  const isUser = msg.sender === "user"

  return (
    <div
      key={i}
      className={`flex ${isUser ? "justify-end" : "justify-start"} px-2`}
    >
      <div
        className={`max-w-[75%] px-4 py-3 rounded-2xl leading-relaxed shadow-sm
          ${isUser
            ? "bg-zinc-700 text-gray-100 rounded-br-none"
            : "bg-zinc-800 text-gray-100 rounded-bl-none border border-zinc-700"
          }`}
      >
        {msg.text}
      </div>
    </div>
  )
}


  return (
    <div className="flex flex-col h-screen p-4">
      <div className="flex-1 overflow-y-auto flex flex-col gap-3 pb-4">
        {messages.length === 0 && !isEvaTyping && (
          <div className="text-gray-500 text-center my-auto flex flex-col items-center">
            <MessageSquare className="h-8 w-8 mb-2" />
            Start a conversation with EVA
          </div>
        )}

        {messages.map((msg, i) => renderMessage(msg, i))}

        {isEvaTyping && (
          <Card className="self-start p-3 bg-zinc-800 text-gray-100 mr-auto">
            <TypingDots /> <span className="ml-2">EVA is thinking...</span>
          </Card>
        )}

        <div ref={chatEndRef} />
      </div>

      <div className="flex items-center gap-3 relative pt-4 border-t border-zinc-800">
        <Input
          placeholder="Ask EVA something..."
          className="border-zinc-800"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleQuestion(question)}
        />
        <Button
          onClick={() => handleQuestion(question)}
          variant="default"
          className="flex-shrink-0"
        >
          <Send className="h-4 w-4" />
        </Button>

        <div className="relative flex-shrink-0">
          <Button onClick={handleMicClick} variant="outline" className="p-3">
            <Mic
              className={`h-4 w-4 ${isListening ? "text-purple-400" : ""}`}
            />
          </Button>
          {isListening && <SiriMic active={isListening} />}
        </div>
      </div>

      {/* No microphone dialog — live transcript appears in the input field */}
    </div>
  )
}
