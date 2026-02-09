import * as React from "react"
import { NavLink, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/Button"
import {
  Home,
  Briefcase,
  Bot,
  FileText,
  Shield,
  Database,
  BookOpen,
  Plug,
  Bell,
  ChevronLeft,
  ChevronRight,
  Building2,
} from "lucide-react"
import { useUIStore } from "@/stores/uiStore"
import { useWorkspaces, useTenantContext } from "@/hooks/useTenant"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/Select"

const navItems = [
  { to: "/", icon: Home, label: "Home" },
  { to: "/workspaces", icon: Briefcase, label: "Workspaces" },
  { to: "/ai/chat", icon: Bot, label: "AI Advisor" },
  { to: "/blueprints", icon: FileText, label: "Blueprints" },
  { to: "/security", icon: Shield, label: "Security" },
  { to: "/data/retention", icon: Database, label: "Data Control" },
  { to: "/knowledge", icon: BookOpen, label: "Knowledge" },
  { to: "/connectors", icon: Plug, label: "Connectors" },
  { to: "/notifications", icon: Bell, label: "Notifications" },
]

export function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const { data: workspaces } = useWorkspaces()
  const { currentWorkspace, switchWorkspace } = useTenantContext()
  const location = useLocation()

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen border-r bg-background transition-all duration-300 lg:static",
        sidebarOpen ? "w-64 translate-x-0" : "w-0 -translate-x-full lg:w-16 lg:translate-x-0"
      )}
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center border-b px-4">
          <div className={cn("flex items-center gap-2 font-bold text-xl", !sidebarOpen && "lg:hidden")}>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Building2 className="h-5 w-5" />
            </div>
            <span>Area X</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="ml-auto hidden lg:flex"
          >
            {sidebarOpen ? (
              <ChevronLeft className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Workspace Selector */}
        {sidebarOpen && (
          <div className="border-b p-4">
            <label className="text-xs font-medium text-muted-foreground mb-2 block">
              Workspace
            </label>
            <Select value={currentWorkspace || ""} onValueChange={switchWorkspace}>
              <SelectTrigger>
                <SelectValue placeholder="Select workspace" />
              </SelectTrigger>
              <SelectContent>
                {workspaces?.map((workspace) => (
                  <SelectItem key={workspace.id} value={workspace.id}>
                    {workspace.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 overflow-auto p-2">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const isActive = location.pathname.startsWith(item.to)
              return (
                <li key={item.to}>
                  <NavLink
                    to={item.to}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                      !sidebarOpen && "lg:justify-center lg:px-2"
                    )}
                  >
                    <item.icon className="h-5 w-5 flex-shrink-0" />
                    {sidebarOpen && <span>{item.label}</span>}
                  </NavLink>
                </li>
              )
            })}
          </ul>
        </nav>
      </div>
    </aside>
  )
}