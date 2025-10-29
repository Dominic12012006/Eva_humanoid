'use client'
import { useRef } from 'react'
import Gif from '@/components/home/gif'
import Time from '@/components/home/Time'
import Link from 'next/link'
import Collage from '@/components/home/Collage'
import { Settings, MessageCircle, LucideHome } from 'lucide-react'
import BatteryIndicator from '@/components/Battery'



export default function Page() {
  const secondSectionRef = useRef(null)

  const handleClick = () => {
    secondSectionRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="snap-y snap-mandatory h-screen w-full overflow-scroll">
      <Collage />
      <div className="snap-start h-screen relative bg-transparent" onClick={handleClick}>
         <div className='absolute tope-0 right-0'>
            <BatteryIndicator />
          </div>
        <main className="h-screen flex items-center justify-center">
         
          <div className="z-50 text-center">
            <Time />
          </div>
        </main>
        <Gif />
      </div>

      <div ref={secondSectionRef} className="snap-start h-screen w-full backdrop-blur-sm z-50">
        <div className="grid grid-cols-3 gap-8 p-16">
          <Link href="/" className="flex flex-col items-center gap-2 p-4 rounded-lg hover:bg-white/10 transition-all">
            <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center">
              <LucideHome className="w-8 h-8" />
            </div>
            <span>Home</span>
          </Link>
          <Link href="/dashboard" className="flex flex-col items-center gap-2 p-4 rounded-lg hover:bg-white/10 transition-all">
            <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center">
              <MessageCircle className="w-8 h-8" />
            </div>
            <span>Dashboard</span>
          </Link>
          <Link href="/about" className="flex flex-col items-center gap-2 p-4 rounded-lg hover:bg-white/10 transition-all">
            <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center">
              <Settings className="w-8 h-8" />
            </div>
            <span>About</span>
          </Link>
        </div>
      </div>
    </div>
  )
  

}
