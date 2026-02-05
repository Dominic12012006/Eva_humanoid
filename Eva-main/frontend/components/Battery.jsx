"use client"

import React, { useEffect, useState } from "react"
import { Battery } from "lucide-react"

const MAX_VOLTAGE = 27.17          
const BATTERY_ENDPOINT = "http://localhost:8000/battery"

export default function BatteryIndicator() {
  const [level, setLevel] = useState(null)
  const [charging, setCharging] = useState(false) // optional, static for now

  useEffect(() => {
    let mounted = true

    const fetchBattery = async () => {
      try {
        const res = await fetch(BATTERY_ENDPOINT)
        const data = await res.json()

        if (!mounted) return

        if (data.status === "ok" && typeof data.percentage === "number") {
          let pct = Math.round(data.percentage)
          pct = Math.max(0, Math.min(100, pct)) // clamp
          setLevel(pct)
        } else {
          setLevel(null)
        }
      } catch (err) {
        setLevel(null)
      }
    }

    fetchBattery()
    const interval = setInterval(fetchBattery, 2000) // 🔁 poll every 2s

    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [])

  const colorClass =
    level === null
      ? "text-gray-400"
      : level > 60
      ? "text-green-500"
      : level > 30
      ? "text-yellow-500"
      : "text-red-500"

  return (
    <div
      className={`flex items-center gap-1 px-2 py-0 select-none ${
        level === null ? "opacity-80" : ""
      }`}
      title={
        level === null
          ? "Battery status not available"
          : `${level}%${charging ? " (charging)" : ""}`
      }
    >
      <Battery className={`w-5 h-5 ${colorClass}`} />
      <span className={`text-sm font-medium ${colorClass}`}>
        {level === null ? "—" : `${level}%`}
      </span>
    </div>
  )
}
