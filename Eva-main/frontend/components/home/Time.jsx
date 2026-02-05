"use client"

import { useEffect, useState } from "react"

export default function Time() {
  const [date, setDate] = useState(null)

  useEffect(() => {
    const formattedDate = new Date().toLocaleDateString("en-GB", {
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
    })

    setDate(formattedDate)
  }, [])

  if (!date) return null 

  return (
    <div className="lockscreen-time select-none text-center z-50">
      <div className="time font-extrabold text-7xl sm:text-8xl leading-tight">
        Welcome To SRM
      </div>
      <div className="date text-lg opacity-90 mt-2">
        {date}
      </div>
    </div>
  )
}
