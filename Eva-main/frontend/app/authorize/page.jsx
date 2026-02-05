'use client'
import { useState } from "react"
import { Button } from "../../components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../../components/ui/card"
import { Input } from "../../components/ui/input"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
// import { Label } from "../../components/label"

export default function page() {
  const [password , setPassword]=useState("")
  const [email,setEmail]=useState("")
  const emaiLChange=(e)=>{
    const text=e.target.value
    setEmail(text)
    console.log(text)
  }
  const passwordChange=(e)=>{
    const pass=e.target.value
    setPassword(pass)
    console.log(pass)
  }
  const handleSubmit=async (e)=>{
    try{
      const res=await fetch('http://127.0.0.1:8000/authenticate',{
        method:'POST',
        headers:{
          'Content-Type':'application/x-www-form-urlencoded'
        },
        body:new URLSearchParams({
          username:email,
          password:password
        })
      })
      const data=await res.json()
      console.log(data.access_token)
      if(data.access_token){
         alert('Successfully Logged in')
         window.close()

      }else{
        alert('Not authorized ')
      }
     
    }catch(error){
      console.log(`Error :${error}`)
    }
  }
  return (
    <div>
      <Link href='/'>
            <button
        
        style={{
          position: "absolute",
          top: "16px",
          left: "16px",
          zIndex: 10,
          border: "none",
          borderRadius: "9999px",
          padding: "10px",
          cursor: "pointer",
        }}
        aria-label="Go back home"
      >
        <ArrowLeft size={20} color="white" />
      </button>
      </Link>
   
      <Card className="w-full max-w-sm ml-50 mt-12 ">
      <CardHeader>
        <CardTitle>Admin Access </CardTitle>
      
        <CardDescription>
          Welcome to Eva
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form>
         <div className="flex flex-col gap-6">
          <div className=''>
          <p>Email</p> 
         </div>  
            <div className="grid gap-2">
              
               <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                required
                onChange={emaiLChange}
              /> 
            </div>
            <div className="grid gap-2">
               <div>
                Password
               </div>
              <Input id="password" placeholder='Enter Your Password' type="password" required onChange={passwordChange} />
            </div>
          </div>
        </form>
      </CardContent>
      <CardFooter className="flex-col gap-2">
        <Button type="submit" className="w-full "onClick={handleSubmit}>
          Login
        </Button>
        </CardFooter>
      
    </Card>
      
    </div>

  )
}
