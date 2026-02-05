'use client'
import { useRef, useEffect } from 'react'
import Gif from '../components/home/gif'
import Time from '../components/home/Time'
import Link from 'next/link'
import Collage from '../components/home/Collage'
import { Settings, MessageCircle, LucideHome, School, PersonStanding, ArrowUp, ArrowLeft } from 'lucide-react'
import BatteryIndicator from '../components/Battery'
import { useRouter } from 'next/navigation'
import { Button } from '../components/ui/button'

export default function Page() {
  const secondSectionRef = useRef(null)
  const router = useRouter()

  const handleClick = () => {
    secondSectionRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch('http://localhost:8000/status', { method: 'GET' })
        const data = await res.json()
        console.log(data)
        if (data.wake_detected === true) {
          console.log('Wake word detected → Redirecting...')
          router.push('/dashboard')
        }
      } catch (err) {
        console.error('Wake check failed:', err)
      }
    }, 1500)

    return () => clearInterval(interval)
  }, [router])

  return (
    <div className="snap-y snap-mandatory h-screen w-full overflow-scroll relative">



      <Collage />

      <div className="snap-start h-screen relative bg-transparent" onClick={handleClick}>
        <div className="flex flex-col justify-end mt-4">
          <div className="absolute top-0 right-0">
            <BatteryIndicator />
          </div>

          <div className="mt-4 ">
            <Link href="/authorize">
              <Button>
                Authorize
              </Button>
            </Link>
          </div>
        </div>

        <main className="h-screen flex items-center justify-center">
          <div className="z-50 text-center">
            <Time />
          </div>
        </main>

      
      </div>

      <div ref={secondSectionRef}  className="snap-start h-screen w-full backdrop-blur-sm z-50 flex items-center justify-center">
        <div className="grid grid-cols-1 gap-7 p-16 ">
          <Link href="/about" className="flex flex-col items-center gap-2 p-4 rounded-lg hover:bg-white/10 transition-all">
            <div className="w-30 h-30 rounded-full bg-white/10 flex items-center justify-center">
              <PersonStanding className="w-20 h-20" />
            </div>
            <span className='font-bold'>About exa</span>
          </Link>

          <Link href="/dashboard" className="flex flex-col items-center gap-2 p-4 rounded-lg hover:bg-white/10 transition-all">
            <div className="w-30 h-30 rounded-full bg-white/10 flex items-center justify-center">
              <MessageCircle className="w-20 h-20" />
            </div>
            <span className='font-bold'>Chat with Eva</span>
          </Link>

          <a
            href="https://www.srmist.edu.in/about-us/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex flex-col items-center gap-2 p-4 rounded-lg hover:bg-white/10 transition-all"
          >
            <div className="w-30 h-30 rounded-full bg-white/10 flex items-center justify-center">
              <School className="w-20 h-20" />
            </div>
            <span className='font-bold'>About SRM</span>
          </a>
        </div>
      </div>
    </div>
  )
}
