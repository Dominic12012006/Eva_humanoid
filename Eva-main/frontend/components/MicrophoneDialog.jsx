"use client"

import React from "react"

export default function MicrophoneDialog({ open, transcript, onStop, onCancel }) {
  if (!open) return null

  return (
    <div className="mic-dialog-overlay fixed inset-0 z-50 flex items-center justify-center">
      <div className="mic-dialog bg-zinc-900 text-white rounded-xl p-6 w-11/12 max-w-lg shadow-2xl">
        <h3 className="text-lg font-semibold mb-2">Listening for you</h3>
        <p className="text-sm text-zinc-300 mb-4">
          Say your message and press Stop when finished. You can also Cancel to abort.
        </p>

        <div className="transcript bg-zinc-800 p-3 rounded-md min-h-[72px] mb-4">
          <div className="text-md text-gray-100">{transcript || <span className="text-zinc-400">(no speech detected yet)</span>}</div>
        </div>

        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-lg bg-zinc-700 hover:bg-zinc-600"
          >
            Cancel
          </button>
          <button
            onClick={onStop}
            className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 text-white"
          >
            Stop & Send
          </button>
        </div>
      </div>

      <style jsx>{`
        .mic-dialog-overlay { background: rgba(2,6,23,0.6); }
      `}</style>
    </div>
  )
}
