import Navbar from "../../components/Navbar"

export default function Layout({children}) {
  return (
   
     
      
        <div className="w-full">
            <Navbar />
           <div className="mt-10 px-4">
            {children}
            </div> 
        </div>
        
      

  )
}