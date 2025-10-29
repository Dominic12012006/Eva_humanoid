"use client"
import React, { useEffect, useState } from 'react'
import { Battery } from 'lucide-react'

export default function BatteryIndicator() {
  const [level, setLevel] = useState(null)
  const [charging, setCharging] = useState(false)

  useEffect(() => {
    let mounted = true
    let battery = null

    const update = () => {
      if (!battery || !mounted) return
      setLevel(Math.round(battery.level * 100))
      setCharging(Boolean(battery.charging))
    }

    if (typeof navigator !== 'undefined' && 'getBattery' in navigator) {
      navigator.getBattery().then((b) => {
        battery = b
        update()
        battery.addEventListener('levelchange', update)
        battery.addEventListener('chargingchange', update)
      }).catch(() => {
      })
    } else {
    }

    return () => {
      mounted = false
      if (battery) {
        try {
          battery.removeEventListener('levelchange', update)
          battery.removeEventListener('chargingchange', update)
        } catch (e) {
        }
      }
    }
  }, [])

  const colorClass =
    level === null ? 'text-gray-400' : level > 60 ? 'text-green-500' : level > 30 ? 'text-yellow-500' : 'text-red-500'

  return (
    <div
      className={`flex items-center gap-1 px-2 py-0 select-none ${level === null ? 'opacity-80' : ''}`}
      title={
        level === null
          ? 'Battery status not available'
          : `${level}%${charging ? ' (charging)' : ''}`
      }
    >
      <Battery className={`w-5 h-5 ${colorClass}`} />
      <span className={`text-sm font-medium ${colorClass}`}>{level === null ? '—' : `${level}%`}</span>
    </div>
  )
}
