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
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState("")
  const [isEvaTyping, setIsEvaTyping] = useState(false)
  const [isListening, setIsListening] = useState(true)
  const chatEndRef = useRef(null)

  // Smooth scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isEvaTyping])

  const sleep = (ms) => new Promise((res) => setTimeout(res, ms))

  // 🧠 Poll backend for live transcript every 300ms
  useEffect(() => {
    let interval
    const pollTranscript = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/get_live_text")
        const data = await res.json()
        if (data?.text) {
          setQuestion(data.text)
        }
      } catch (err) {
        console.error("Error fetching live transcript:", err)
      }
    }

    interval = setInterval(pollTranscript, 300)
    return () => clearInterval(interval)
  }, [])

  const handleQuestion = async (questionText) => {
    if (!questionText.trim()) return
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

      await sleep(400 + Math.random() * 400)
      setMessages((prev) => [...prev, { sender: "eva", text: evaText }])
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

  const renderMessage = (msg, i) => {
    const isUser = msg.sender === "user"
    return (
      <div key={i} className={`flex ${isUser ? "justify-end" : "justify-start"} px-2`}>
        <div
          className={`max-w-[75%] px-4 py-3 rounded-2xl leading-relaxed shadow-sm ${
            isUser
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

      {/* ---- Input + Send ---- */}
      <div className="flex items-center gap-3 relative pt-4 border-t border-zinc-800">
        <Input
          placeholder="Ask EVA something..."
          className="border-zinc-800"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleQuestion(question)}
        />
        <Button onClick={() => handleQuestion(question)} variant="default">
          <Send className="h-4 w-4" />
        </Button>

        {/* Just for design continuity */}
        <div className="relative flex-shrink-0">
          <Button variant="outline" className="p-3">
            <Mic className={`h-4 w-4 ${isListening ? "text-purple-400" : ""}`} />
          </Button>
          {isListening && <SiriMic active={true} />}
        </div>
      </div>
    </div>
  )
}
