import { Outlet } from "react-router-dom"
import { Sidebar } from "./Sidebar"
import { Header } from "@/components/ui/Header"
import { cn } from "@/lib/utils"
import { useUIStore } from "@/stores/uiStore"

export function MainLayout() {
  const { sidebarOpen } = useUIStore()

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className={cn(
        "flex flex-1 flex-col overflow-hidden transition-all duration-300",
      )}>
        <Header />
        <main className="flex-1 overflow-auto p-4 sm:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}