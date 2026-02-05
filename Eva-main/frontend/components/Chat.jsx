"use client"

import React, { useState, useEffect, useRef } from "react"
import { Send, Mic, MessageSquare, LanguagesIcon } from "lucide-react"
import SiriMic from "../components/SiriMic"

const Input = ({ placeholder, className, value, onChange, onKeyDown }) => (
  <input
    placeholder={placeholder}
    className={`p-3 border rounded-lg flex-1 bg-zinc-900 text-gray-100 placeholder-gray-500 focus:outline-none ${className}`}
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
        : "bg-zinc-800 hover:bg-zinc-700 text-white border border-zinc-700"
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

const translations = {
  English: {
    placeholder: "Ask EVA something...",
    thinking: "EVA is thinking...",
    startMessage: `Say "EVA" or click the mic to start talking.`,
  },
  Hindi: {
    placeholder: "ईवीए से कुछ पूछें...",
    thinking: "EVA सोच रही है...",
    startMessage: `"ईवीए" बोलें या बात करने के लिए माइक पर क्लिक करें।`,
  },
  Tamil: {
    placeholder: "EVA-விடம் ஏதாவது கேளுங்கள்...",
    thinking: "EVA யோசித்து கொண்டிருக்கிறது...",
    startMessage: `"EVA" என்று சொல்லவோ அல்லது மைக் அழுத்தவோ பேசத் தொடங்கலாம்.`,
  },
  Malayalam: {
  placeholder: "EVAയോട് എന്തെങ്കിലും ചോദിക്കൂ...",
  thinking: "EVA ചിന്തിച്ചുകൊണ്ടിരിക്കുന്നു...",
  startMessage: `"EVA" എന്ന് പറയുക അല്ലെങ്കിൽ സംസാരിക്കാൻ മൈക്ക് ക്ലിക്ക് ചെയ്യുക.`,
},

Telugu: {
  placeholder: "EVAని ఏదైనా అడగండి...",
  thinking: "EVA ఆలోచిస్తోంది...",
  startMessage: `"EVA" అని చెప్పండి లేదా మాట్లాడేందుకు మైక్‌పై క్లిక్ చేయండి.`,
},

Kannada: {
  placeholder: "EVAಗೆ ಏನಾದರೂ ಕೇಳಿ...",
  thinking: "EVA ಯೋಚಿಸುತ್ತಿದೆ...",
  startMessage: `"EVA" ಎಂದು ಹೇಳಿ ಅಥವಾ ಮಾತನಾಡಲು ಮೈಕ್ ಕ್ಲಿಕ್ ಮಾಡಿ.`,
},
  Other: {
    placeholder: "Ask EVA something...",
    thinking: "EVA is thinking...",
    startMessage: `Say "EVA" or click the mic to start talking.`,
  },

}

export default function ChatSection({ language }) {
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState("")
  const [lang, setLang] = useState(language)
  const [showLangMenu, setShowLangMenu] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isEvaTyping, setIsEvaTyping] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState(null)
  const [lastEvaIndex, setLastEvaIndex] = useState(0)
  const [lastImageIndex,setLastImageIndex]=useState(0)

  const chatEndRef = useRef(null)

  const fetchQuestions = async () => {
    const res = await fetch("http://127.0.0.1:8000/show_questions")
    return res.json()
  }

  const fetchAnswers = async () => {
    const res = await fetch("http://127.0.0.1:8000/show_answer")
    return res.json()
  }

  const fetchImages = async () => {
    const res = await fetch("http://127.0.0.1:8000/show_images")
    return res.json()
  }

  const t = translations[lang] || translations.English

  useEffect(() => {
    localStorage.setItem("app_language", lang)
  }, [lang])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isEvaTyping])

  useEffect(() => {
    const init = async () => {
      const q = await fetchQuestions()
      const a = await fetchAnswers()
      const i = await fetchImages()
      setLastEvaIndex(Math.min(q.length, a.length, i.length))
    }
    init()
  }, [])

  useEffect(() => {
    let isMounted = true

    const loadQA = async () => {
      try {
        const questions = await fetchQuestions()
        const answers = await fetchAnswers()
        const images = await fetchImages()

        const q = [...questions].reverse()
        const a = [...answers].reverse()
        const i = [...images].reverse()

        if (q.length > lastEvaIndex && a[lastEvaIndex]) {
          setIsEvaTyping(true)
          setTimeout(() => {
  if (!isMounted) return

   let latestImage = null

if (i.length > lastImageIndex) {
  latestImage = i[lastImageIndex]
}


  setMessages((prev) => [
    ...prev,
    { sender: "user", text: q[lastEvaIndex].question },
    {
      sender: "eva",
      text: a[lastEvaIndex].answer,
      image: latestImage
        ? latestImage.image
          ? latestImage.image
          : latestImage.image_base64
            ? `data:image/png;base64,${latestImage.image_base64}`
            : null
        : null,
    },
  ])
  setLastEvaIndex((idx) => idx + 1)

if (i.length > lastImageIndex) {
  setLastImageIndex((idx) => idx + 1)
}

  setIsEvaTyping(false)
}, 2500)

        }
      } catch (err) {
        console.error("Polling failed:", err)
      }
    }

    const interval = setInterval(loadQA, 1000)
    loadQA()

    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [lastEvaIndex])

  const handleQuestion = async (questionText) => {
    if (!questionText.trim()) return
    setQuestion("")
    setIsEvaTyping(true)

    try {
      await fetch("http://127.0.0.1:8000/recieve_response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer: questionText, lang }),
      })
    } catch (err) {
      console.error("Error:", err)
    } finally {
      setIsEvaTyping(false)
    }
  }

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

      recorder.ondataavailable = (e) => e.data.size && chunks.push(e.data)
      recorder.onstop = async () => {
        const blob = new Blob(chunks, { type: "audio/wav" })
        const formData = new FormData()
        formData.append("file", blob)
        formData.append("lang", lang)

        setIsEvaTyping(true)

        try {
          await fetch("http://127.0.0.1:8000/upload_audio", {
            method: "POST",
            body: formData,
          })
        } catch (err) {
          console.error("Upload audio error:", err)
        } finally {
          setIsEvaTyping(false)
        }
      }

      recorder.start()
      setMediaRecorder(recorder)
      setIsListening(true)
    } catch {
      alert("Microphone not available.")
    }
  }

  const renderMessage = (msg, i) => (
    <div
      key={i}
      className={`flex flex-col ${
        msg.sender === "user" ? "items-end" : "items-start"
      } px-2`}
    >
      <div className="max-w-[75%] px-4 py-3 rounded-2xl shadow-sm">
        {msg.text}
      </div>

      {msg.image && (
        <img
          src={msg.image}
          alt="EVA visual"
          className="mt-2 rounded-lg max-w-xs"
        />
      )}
    </div>
  )

  return (
    <div className="flex flex-col h-screen p-4">
      <div className="flex-1 overflow-y-auto flex flex-col gap-3">
        {messages.length === 0 && !isEvaTyping && (
          <div className="text-gray-500 text-center my-auto">
            <MessageSquare className="h-8 w-8 mx-auto mb-2" />
            {t.startMessage}
          </div>
        )}

        {messages.map(renderMessage)}

        {isEvaTyping && (
          <Card className="self-start bg-zinc-800 text-gray-100 flex gap-2">
            <TypingDots />
            <span className="text-sm text-gray-400">{t.thinking}</span>
          </Card>
        )}

        <div ref={chatEndRef} />
      </div>

      <div className="flex items-center gap-3 pt-4 border-t sticky bottom-3">
        <Input
          placeholder={t.placeholder}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleQuestion(question)}
        />

        <Button onClick={() => handleQuestion(question)}>
          <Send className="h-4 w-4" />
        </Button>

        <Button onClick={handleMicClick} variant="outline">
          <Mic className={isListening ? "text-purple-400" : ""} />
        </Button>

        {isListening && <SiriMic active />}

        <div className="relative">
          <Button
            onClick={() => setShowLangMenu((p) => !p)}
            variant="outline"
          >
            <LanguagesIcon className="h-4 w-4" />
          </Button>

          {showLangMenu && (
            <div className="absolute bottom-14 right-0 bg-zinc-900 border border-zinc-700 rounded-lg shadow-lg w-32 text-sm">
              {["English", "Hindi", "Tamil", "Malayalam","Telugu","Kannada"].map((l) => (
                <div
                  key={l}
                  onClick={() => {
                    setLang(l)
                    setShowLangMenu(false)
                  }}
                  className={`px-4 py-2 cursor-pointer hover:bg-zinc-800 ${
                    lang === l
                      ? "text-purple-400 font-medium"
                      : "text-gray-300"
                  }`}
                >
                  {l}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
