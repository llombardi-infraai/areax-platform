import { Outlet } from "react-router-dom"
import { Building2 } from "lucide-react"

export function AuthLayout() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-muted/40 p-4">
      <div className="mb-8 flex items-center gap-2 text-2xl font-bold">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Building2 className="h-6 w-6" />
        </div>
        <span>Area X</span>
      </div>
      <Outlet />
    </div>
  )
}