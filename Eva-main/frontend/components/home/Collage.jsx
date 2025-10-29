"use client"
import React from 'react'

const images = [
  '/srm1.webp',
  '/srm2.webp',
  '/srm3.webp',
  '/srm4.webp',
  '/srm5.webp',
  '/srm6.webp',
  '/srm7.webp',
  '/srm8.webp',
  '/srm9.webp',
]

export default function Collage() {
  const Grid = () => (
    <div className="collage-grid">
      {images.map((src, i) => (
        <div key={`${src}-${i}`} className="collage-item">
          <img src={src} alt={`collage-${i}`} className="collage-img" />
        </div>
      ))}
    </div>
  )

  return (
    <div className="collage fixed inset-0 -z-20 pointer-events-none">
      <div className="collage-track">
        <Grid />
        <Grid />
      </div>
    </div>
  )
}
