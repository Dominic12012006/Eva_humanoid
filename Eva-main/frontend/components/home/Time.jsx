"use client"

import React, { useEffect, useState } from 'react'

function Time() {
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  // Use Asia/Kolkata timezone (Indian Standard Time)
  const time = now.toLocaleTimeString('en-IN', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: 'Asia/Kolkata',
  })

  const date = now.toLocaleDateString('en-IN', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'Asia/Kolkata',
  })

  return (
    <div className="lockscreen-time select-none text-center z-50">
      <div className="time font-extrabold text-7xl sm:text-8xl leading-tight">{time}</div>
      <div className="date text-lg opacity-90 mt-2">{date}</div>
    </div>
  )
}

export default Time