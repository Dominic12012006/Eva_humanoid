import Navbar from "../../components/Navbar"

export default function Layout({ children }) {
  return (
    <div className="w-full h-screen flex flex-col">
      
      <div className="sticky top-0 z-50 ">
        <Navbar />
      </div>

 
      <div className="flex-1 overflow-y-auto px-4">
        {children}
      </div>

    </div>
  )
}
