"use client"

import React, { useEffect, useState } from "react"

export default function SiriMic({ active: controlledActive, onToggle }) {
  const [active, setActive] = useState(!!controlledActive)

  useEffect(() => {
    if (typeof controlledActive === 'boolean') setActive(controlledActive)
  }, [controlledActive])

  const toggle = () => {
    const next = !active
    if (typeof controlledActive !== 'boolean') setActive(next)
    if (onToggle) onToggle(next)
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      toggle()
    }
  }

  return (
    <div className="siri-mic-container fixed bottom-8 left-8 z-50">
      <button
        aria-pressed={active}
        aria-label={active ? 'Stop voice capture' : 'Start voice capture'}
        onClick={toggle}
        onKeyDown={handleKey}
        className={`siri-mic relative flex items-center justify-center rounded-full focus:outline-none focus-visible:ring-4 focus-visible:ring-purple-300/40 transition-transform will-change-transform ${active ? 'siri-active' : ''}`}
        style={{ width: 84, height: 84, pointerEvents: 'auto' }}
      >
        <span className="ring ring-1" aria-hidden />
        <span className="ring ring-2" aria-hidden />
        <span className="ring ring-3" aria-hidden />
        <span className="center-bg" aria-hidden />
        <svg className="mic-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="34" height="34" fill="none" aria-hidden>
          <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3z" stroke="white" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M19 11v1a7 7 0 0 1-14 0v-1" stroke="white" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" opacity="0.9"/>
          <path d="M12 19v3" stroke="white" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" opacity="0.9"/>
        </svg>

      </button>

      <style jsx>{`
        .siri-mic-container { }

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

        .mic-icon {
          position: relative;
          z-index: 3;
          filter: drop-shadow(0 6px 14px rgba(0,0,0,0.25));
        }

        .ring {
          position: absolute;
          border-radius: 9999px;
          pointer-events: none;
          z-index: 1;
          opacity: 0;
          transform: scale(0.6);
        }

        .ring-1 { width: 84px; height: 84px; }
        .ring-2 { width: 110px; height: 110px; }
        .ring-3 { width: 140px; height: 140px; }

        /* active state: rings pulse and center scales */
        .siri-active .center-bg { transform: scale(1.03); box-shadow: 0 18px 50px rgba(99,102,241,0.28), inset 0 2px 12px rgba(255,255,255,0.08); }

        .siri-active .ring-1,
        .siri-active .ring-2,
        .siri-active .ring-3 {
          animation: siri-ring 1.8s ease-out infinite;
          opacity: 1;
        }

        .siri-active .ring-2 { animation-delay: 0.18s }
        .siri-active .ring-3 { animation-delay: 0.36s }

        @keyframes siri-ring {
          0% { transform: scale(0.6); opacity: 0.7; }
          70% { transform: scale(1.15); opacity: 0.08; }
          100% { transform: scale(1.5); opacity: 0; }
        }

        /* subtle idle breathing */
        .siri-mic { transition: transform 220ms; }
        .siri-mic:active { transform: scale(0.96); }

        /* Focus ring for keyboard users */
        .siri-mic:focus-visible { box-shadow: 0 0 0 6px rgba(168,85,247,0.12); }

        /* Respect reduced motion */
        @media (prefers-reduced-motion: reduce) {
          .siri-active .ring { animation: none; opacity: 0.2 }
          .center-bg { transition: none }
        }
      `}</style>
    </div>
  )
}
