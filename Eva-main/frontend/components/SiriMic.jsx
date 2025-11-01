"use client"

import React, { useEffect, useState, useRef } from "react"
import { Mic, Speech } from "lucide-react"

export default function SiriMic({ active: controlledActive, onToggle }) {
  const [active, setActive] = useState(!!controlledActive)
  const [speaking, setSpeaking] = useState(false)
  const audioContextRef = useRef(null)
  const analyserRef = useRef(null)
  const dataArrayRef = useRef(null)
  const silenceTimerRef = useRef(null)
  const sourceRef = useRef(null)

  // Sync with external control
  useEffect(() => {
    if (typeof controlledActive === "boolean") setActive(controlledActive)
  }, [controlledActive])

  // Main effect for mic activity
  useEffect(() => {
    if (!active) {
      stopListening()
      return
    }
    startListening()
    return () => stopListening()
  }, [active])

  const toggle = () => {
    const next = !active
    if (typeof controlledActive !== "boolean") setActive(next)
    if (onToggle) onToggle(next)
  }

  const handleKey = (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault()
      toggle()
    }
  }

  // --------------------------
  // 🎤 Mic listening + silence detection
  // --------------------------
  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      const analyser = audioContext.createAnalyser()
      const source = audioContext.createMediaStreamSource(stream)
      const dataArray = new Uint8Array(analyser.frequencyBinCount)

      source.connect(analyser)
      audioContextRef.current = audioContext
      analyserRef.current = analyser
      dataArrayRef.current = dataArray
      sourceRef.current = source

      const checkSilence = () => {
        analyser.getByteFrequencyData(dataArray)
        const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length

        // adjust thresholds as needed
        const speakingThreshold = 25
        const silenceThreshold = 10

        if (avg > speakingThreshold) {
          if (!speaking) setSpeaking(true)
          clearTimeout(silenceTimerRef.current)
        } else if (avg < silenceThreshold && speaking) {
          clearTimeout(silenceTimerRef.current)
          silenceTimerRef.current = setTimeout(() => {
            setSpeaking(false)
            // Auto stop listening after silence
            setActive(false)
            if (onToggle) onToggle(false)
          }, 1000) // 1 second of silence = stop
        }

        requestAnimationFrame(checkSilence)
      }

      checkSilence()
    } catch (err) {
      console.error("🎙️ Mic error:", err)
      setActive(false)
    }
  }

  const stopListening = () => {
    if (audioContextRef.current) audioContextRef.current.close()
    audioContextRef.current = null
    analyserRef.current = null
    sourceRef.current = null
    clearTimeout(silenceTimerRef.current)
    setSpeaking(false)
  }

  return (
    <div className="siri-mic-container fixed bottom-8 left-8 z-50">
      <button
        aria-pressed={active}
        aria-label={active ? "Stop voice capture" : "Start voice capture"}
        onClick={toggle}
        onKeyDown={handleKey}
        className={`siri-mic relative flex items-center justify-center rounded-full focus:outline-none focus-visible:ring-4 focus-visible:ring-purple-300/40 transition-transform will-change-transform ${
          active ? "siri-active" : ""
        }`}
        style={{ width: 84, height: 84, pointerEvents: "auto" }}
      >
        <span className="ring ring-1" aria-hidden />
        <span className="ring ring-2" aria-hidden />
        <span className="ring ring-3" aria-hidden />
        <span className="center-bg" aria-hidden />
        {speaking ? <Speech size={32} /> : <Mic size={32} />}
      </button>

      <style jsx>{`
        .siri-mic {
          background: transparent;
          border: none;
          user-select: none;
        }
        .center-bg {
          position: absolute;
          width: 64px;
          height: 64px;
          border-radius: 9999px;
          background: radial-gradient(circle at 30% 30%, rgba(168,85,247,0.95), rgba(99,102,241,0.9) 40%, rgba(76,29,149,0.85) 100%);
          box-shadow: 0 8px 30px rgba(99,102,241,0.22), inset 0 2px 10px rgba(255,255,255,0.06);
          z-index: 2;
          transition: transform 260ms cubic-bezier(.2,.9,.3,1), box-shadow 260ms;
        }
        .siri-active .center-bg { transform: scale(1.03); box-shadow: 0 18px 50px rgba(99,102,241,0.28), inset 0 2px 12px rgba(255,255,255,0.08); }
        .ring { position: absolute; border-radius: 9999px; pointer-events: none; z-index: 1; opacity: 0; transform: scale(0.6); }
        .ring-1 { width: 84px; height: 84px; }
        .ring-2 { width: 110px; height: 110px; }
        .ring-3 { width: 140px; height: 140px; }
        .siri-active .ring-1, .siri-active .ring-2, .siri-active .ring-3 {
          animation: siri-ring 1.8s ease-out infinite; opacity: 1;
        }
        .siri-active .ring-2 { animation-delay: 0.18s; }
        .siri-active .ring-3 { animation-delay: 0.36s; }
        @keyframes siri-ring {
          0% { transform: scale(0.6); opacity: 0.7; }
          70% { transform: scale(1.15); opacity: 0.08; }
          100% { transform: scale(1.5); opacity: 0; }
        }
        .siri-mic:active { transform: scale(0.96); }
        .siri-mic:focus-visible { box-shadow: 0 0 0 6px rgba(168,85,247,0.12); }
      `}</style>
    </div>
  )
}
