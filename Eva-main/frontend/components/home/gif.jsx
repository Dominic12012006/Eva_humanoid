"use client"

import React, { useEffect, useRef, useState } from 'react'

const SIZE = 140 

const Gif = () => {
  const ref = useRef(null)
  const [pos, setPos] = useState({ left: 20, top: 20 })

  useEffect(() => {
    if (typeof window === 'undefined') return

    const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const padding = 24
    const pickRandom = () => {
      const vw = Math.max(window.innerWidth, 0)
      const vh = Math.max(window.innerHeight, 0)
      const maxLeft = Math.max(vw - SIZE - padding, padding)
      const maxTop = Math.max(vh - SIZE - padding, padding)
      const left = Math.floor(Math.random() * (maxLeft - padding + 1)) + padding
      const top = Math.floor(Math.random() * (maxTop - padding + 1)) + padding
      return { left, top }
    }

    if (prefersReduced) {
      const vw = window.innerWidth
      const vh = window.innerHeight
      setPos({ left: Math.max(vw - SIZE - padding, padding), top: Math.max(vh - SIZE - padding, padding) })
      return
    }
    setPos({ left: Math.max(Math.floor(window.innerWidth / 2 - SIZE / 2), padding), top: Math.max(Math.floor(window.innerHeight / 2 - SIZE / 2), padding) })

    let mounted = true
    let timer = null

    const scheduleNext = () => {
      if (!mounted) return
      const delay = 2800 + Math.floor(Math.random() * 5200) 
      timer = setTimeout(() => {
        if (!mounted) return
        setPos(pickRandom())
        scheduleNext()
      }, delay)
    }
    timer = setTimeout(() => {
      if (!mounted) return
      setPos(pickRandom())
      scheduleNext()
    }, 700)

    const handleResize = () => {
      setPos(prev => {
        const vw = Math.max(window.innerWidth, 0)
        const vh = Math.max(window.innerHeight, 0)
        const maxLeft = Math.max(vw - SIZE - padding, padding)
        const maxTop = Math.max(vh - SIZE - padding, padding)
        return {
          left: Math.min(Math.max(prev.left, padding), maxLeft),
          top: Math.min(Math.max(prev.top, padding), maxTop),
        }
      })
    }

    window.addEventListener('resize', handleResize)

    return () => {
      mounted = false
      clearTimeout(timer)
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  return (
    <>
      <div
        ref={ref}
        className="floating-video"
        aria-hidden="false"
        role="img"
        aria-label="Chatbot demonstration video"
        style={{ left: `${pos.left}px`, top: `${pos.top}px`, width: `${SIZE}px`, height: `${SIZE}px` }}
      >
        <video
          src={'/Chatbot.mp4'}
          autoPlay
          muted
          loop
          playsInline
          className="floating-media"
        />
      </div>

      <style jsx>{`
        .floating-video {
          position: fixed;
          transform: translate(0, 0);
          border-radius: 50%;
          overflow: hidden;
          box-shadow: 0 12px 34px rgba(0,0,0,0.35);
          z-index: -30;
          pointer-events: none; /* don't block clicks */
          transition: left 2.2s cubic-bezier(.22,.9,.29,1), top 2.2s cubic-bezier(.22,.9,.29,1);
        }

        .floating-media {
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
        }

        @media (prefers-reduced-motion: reduce) {
          .floating-video {
            transition: none;
          }
        }
      `}</style>
    </>
  )
}

export default Gif