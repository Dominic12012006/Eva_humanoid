"use client"

import React, { useState, useEffect, useRef } from "react"
import { Send, Mic, MessageSquare, LanguagesIcon } from "lucide-react"
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
          0%, 80%, 100% { transform: translateY(0); opacity: 0.6; }
          40% { transform: translateY(-6px); opacity: 1; }
        }
      `}</style>
    </div>
  )
}

export default function ChatSectionDemo() {
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState("")
  const [language, setLang] = useState("English")
  const [showLangMenu, setShowLangMenu] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isEvaTyping, setIsEvaTyping] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState(null)
  const chatEndRef = useRef(null)

  const sleep = (ms) => new Promise((res) => setTimeout(res, ms))

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isEvaTyping])

  // 🧠 Text question handler
  const handleQuestion = async (questionText) => {
    if (!questionText.trim()) return

    const userMessage = { sender: "user", text: questionText }
    setMessages((prev) => [...prev, userMessage])
    setQuestion("")
    setIsEvaTyping(true)

    try {
      const response = await fetch("http://127.0.0.1:8000/recieve_response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer: questionText, language }),
      })

      const data = await response.json()
      const evaText = data?.data || "Sorry, I couldn’t get a response."
      const evaImg = data?.image || null

      console.log("Image from backend:", evaImg)

      setMessages((prev) => [
        ...prev,
        { sender: "eva", text: evaText, image: evaImg },
      ])
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

  // 🎤 Audio upload handler (multipart/form-data)
  const handleMicClick = async () => {
    if (isListening) {
      mediaRecorder?.stop()
      setIsListening(false)
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      const chunks = []

      recorder.ondataavailable = (e) => e.data.size > 0 && chunks.push(e.data)

      recorder.onstop = async () => {
        const blob = new Blob(chunks, { type: "audio/wav" })
        const formData = new FormData()
        formData.append("file", blob, "recording.wav")
        formData.append("lang", language)

        setIsEvaTyping(true)

        const res = await fetch("http://127.0.0.1:8000/upload_audio", {
          method: "POST",
          body: formData,
        })

        const data = await res.json()
        const transcript = data.text || "Could not recognize speech"
        const evaReply = data.data || "EVA couldn’t respond."
        const evaImage =
          data?.image
            ? `data:image/png;base64,${data.image_base64}`
            : data?.image || null

        setMessages((prev) => [
          ...prev,
          { sender: "user", text: transcript },
          { sender: "eva", text: evaReply, image: evaImage },
        ])
        setIsEvaTyping(false)
      }

      recorder.start()
      setMediaRecorder(recorder)
      setIsListening(true)
    } catch (err) {
      console.error("Mic error:", err)
      alert("Microphone not available.")
    }
  }

  // 🗨️ Chat message renderer
  const renderMessage = (msg, i) => {
    const isUser = msg.sender === "user"

    return (
      <div key={i} className={`flex flex-col ${isUser ? "items-end" : "items-start"} px-2`}>
        {/* 💬 Message bubble */}
        <div
          className={`max-w-[75%] px-4 py-3 rounded-2xl leading-relaxed shadow-sm ${
            isUser
              ? "bg-zinc-700 text-gray-100 rounded-br-none"
              : "bg-zinc-800 text-gray-100 rounded-bl-none border border-zinc-700"
          }`}
        >
          {msg.text}
        </div>

        {/* 🖼️ Image BELOW EVA's text bubble */}
        {!isUser && msg.image && (
          <img
            src={msg.image}
            alt="EVA response"
            onError={(e) => (e.target.style.display = "none")}
            className="mt-2 ml-3 rounded-lg max-w-[220px] max-h-[160px] object-cover border border-zinc-700 shadow-md animate-fadeIn"
          />
        )}
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen p-4">
      <div className="flex-1 overflow-y-auto flex flex-col gap-3 pb-4">
        {messages.length === 0 && !isEvaTyping && (
          <div className="text-gray-500 text-center my-auto flex flex-col items-center">
            <MessageSquare className="h-8 w-8 mb-2" />
            Say "EVA" or click the mic to start talking.
          </div>
        )}

        {messages.map((msg, i) => renderMessage(msg, i))}

        {isEvaTyping && (
          <Card className="self-start p-3 bg-zinc-800 text-gray-100 mr-auto flex items-center gap-2">
            <TypingDots />
            <span className="text-sm text-gray-400">EVA is thinking...</span>
          </Card>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input Section */}
      <div className="flex items-center gap-3 relative pt-4 border-t border-zinc-800">
        <Input
          placeholder={`Ask EVA something... (${language})`}
          className="border-zinc-800"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleQuestion(question)}
        />
        <Button onClick={() => handleQuestion(question)} variant="default">
          <Send className="h-4 w-4" />
        </Button>

        {/* Mic Button */}
        <div className="relative flex-shrink-0">
          <Button onClick={handleMicClick} variant="outline" className="p-3">
            <Mic className={`h-4 w-4 ${isListening ? "text-purple-400" : ""}`} />
          </Button>
          {isListening && <SiriMic active={isListening} />}
        </div>

        {/* Language Selector */}
        <div className="relative">
          <Button
            onClick={() => setShowLangMenu((prev) => !prev)}
            variant="outline"
            className="p-3"
          >
            <LanguagesIcon className="h-4 w-4" />
          </Button>

          {showLangMenu && (
            <div className="absolute bottom-14 right-0 bg-zinc-800 border border-zinc-700 rounded-lg shadow-lg w-32 text-sm">
              {["English", "Hindi", "Tamil"].map((l) => (
                <div
                  key={l}
                  onClick={() => {
                    setLang(l)
                    setShowLangMenu(false)
                  }}
                  className={`px-4 py-2 cursor-pointer hover:bg-zinc-700 ${
                    language === l ? "text-purple-400 font-medium" : "text-gray-200"
                  }`}
                >
                  {l}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Image fade-in animation */}
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: scale(0.97);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out forwards;
        }
      `}</style>
    </div>
  )
}
