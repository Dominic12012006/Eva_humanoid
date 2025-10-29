"use client"

import React, { useState, useEffect, useRef } from "react"
import { Send, Mic, MessageSquare } from "lucide-react" 
import SiriMic from "@/components/SiriMic" 
import MapComponent from "./Map"
const Input = ({ placeholder, className, value, onChange, onKeyDown }) => (
  <input
    placeholder={placeholder}
    className={`p-3 border rounded-lg flex-1  ${className}`}
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
  <div className={`p-3 rounded-xl shadow-lg ${className}`}>
    {children}
  </div>
)
function TypingDots() {
  return (
    <div className="typing-dots flex items-center gap-1">
      <span className="dot w-2 h-2 rounded-full animate-bounce-slow" />
      <span className="dot w-2 h-2 rounded-full animate-bounce-slow delay-150" />
      <span className="dot w-2 h-2 rounded-full animate-bounce-slow delay-300" />

      <style jsx>{`
        .dot { background-color: currentColor; opacity: 0.6 }
        .animate-bounce-slow { animation: bounce 1s infinite ease-in-out; }
        .delay-150 { animation-delay: 0.15s; }
        .delay-300 { animation-delay: 0.30s; }

        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); opacity: 0.6 }
          40% { transform: translateY(-6px); opacity: 1 }
        }
      `}</style>
    </div>
  )
}

export default function ChatSectionDemo() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [isListening, setIsListening] = useState(false)
  const [isEvaTyping, setIsEvaTyping] = useState(false)
  const chatEndRef = useRef(null)
  const [data, setData] = useState('')
  const [types, setType] = useState('')
  const [question, setQuestion] = useState('')
  const [answers, setAnswer] = useState('')
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isEvaTyping])
  const sleep = (ms) => new Promise((res) => setTimeout(res, ms))
  const handleQuestion = async (questionText) => {
    if (!questionText || !String(questionText).trim()) return
    const userMessage = { type: 'text', sender: 'user', content: { text: questionText } }
    setMessages((prev) => [...prev, userMessage])
    setQuestion('')
    setIsEvaTyping(true)
    try {
      await fetch('http://127.0.0.1:8000/send_question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answer: questionText }),
      })
      const res=await fetch('http://127.0.0.1:8000/recieve_response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'text', data: questionText, llm_name: 'Eva', confidence: 1.0 }),
      })
      const latestData = await res.json()
      let evaMessage
      if (latestData.type === 'map' && latestData.map_data) {
        const { lat, lon, lat1, lat2 } = latestData.map_data || {}
        evaMessage = {
          type: 'map',
          sender: 'eva',
          content: {
            text: latestData.data || '',
            lat: lat ?? lat1,
            lon: lon ?? lat2,
          },
        }
      } else {
        evaMessage = {
          type: latestData.type || 'text',
          sender: 'eva',
          content: { text: latestData.data ?? JSON.stringify(latestData) },
        }
      }
      if (latestData.llm_name) evaMessage.content = { ...evaMessage.content, llm_name: latestData.llm_name }
      if (latestData.confidence !== undefined) evaMessage.content = { ...evaMessage.content, confidence: latestData.confidence }
      const delay = (latestData.type === 'map' ? 800 : 400) + Math.random() * 900
      await sleep(delay)

      setMessages((prev) => [...prev, evaMessage])
    } catch (e) {
      console.error('Error in handleQuestion: ', e)
      setMessages((prev) => [
        ...prev,
        { type: 'text', sender: 'eva', content: { text: 'Error: Could not connect to EVA.' } },
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

    const recognition = new window.webkitSpeechRecognition()
    recognition.lang = "en-US"
    recognition.interimResults = false
    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => setIsListening(false)
    recognition.onresult = (event) => setInput(event.results[0][0].transcript)
    isListening ? recognition.stop() : recognition.start()
  }
  const renderMessage = (msg, i) => {
    const isUser = msg.sender === "user"

    if (msg.type === "text") {
      return (
        <Card
          key={i}
          className={`p-3 max-w-[75%] ${isUser ? "ml-auto" : "mr-auto"} ${
            isUser ? "bg-purple-600 text-white" : "bg-zinc-800 text-gray-100"
          }`}
        >
          {msg.content?.text || ""}
          {msg.content?.llm_name || msg.content?.confidence ? (
            <div className="text-xs text-gray-400 mt-2">
              {msg.content?.llm_name && <span className="mr-2">{msg.content.llm_name}</span>}
              {msg.content?.confidence !== undefined && <span>conf: {Number(msg.content.confidence).toFixed(2)}</span>}
            </div>
          ) : null}
        </Card>
      )
    } else if (msg.type === "image") {
      return (
        <Card key={i} className="self-start p-1 bg-zinc-800 mr-auto">
          <img src={msg.content?.url} alt="EVA Image" className="rounded-lg max-w-xs" />
        </Card>
      )
    } else if (msg.type === "map") {
      const lat = msg.content?.lat
      const lon = msg.content?.lon
      return (
        <div className="flex flex-col gap-2">
          <Card className="self-start p-3 bg-zinc-800 text-gray-100 mr-auto">
            {msg.content?.text}
            {msg.content?.llm_name || msg.content?.confidence ? (
              <div className="text-xs text-gray-400 mt-2">
                {msg.content?.llm_name && <span className="mr-2">{msg.content.llm_name}</span>}
                {msg.content?.confidence !== undefined && <span>conf: {Number(msg.content.confidence).toFixed(2)}</span>}
              </div>
            ) : null}
          </Card>
          <div key={i} className="self-start w-full md:max-w-md mr-auto h-64 bg-zinc-800 rounded-xl overflow-hidden">
            <MapComponent lat={lat} lon={lon} />
          </div>
        </div>
      )
    }
    return null
  }
  return (
    <div className="flex flex-col h-screen  p-4">
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
            <TypingDots />
          </Card>
        )}
        <div ref={chatEndRef} />
      </div>
      <div className="flex items-center gap-3 relative pt-4 border-t border-zinc-800">
        <Input
          placeholder="Ask EVA something..."
          className=" border-zinc-800"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleQuestion(question)}
        />
        <Button onClick={() => handleQuestion(question)} variant="default" className="flex-shrink-0">
          <Send className="h-4 w-4" />
        </Button>

        <div className="relative flex-shrink-0">
          <Button onClick={handleMicClick} variant="outline" className="p-3">
            <Mic className={`h-4 w-4 ${isListening ? "text-purple-400" : ""}`} />
          </Button>
          {isListening && <SiriMic active={isListening} />}
        </div>
      </div>
    </div>
  )
}