import { Menu, User } from 'lucide-react'
import { useUIStore } from '../../stores/uiStore'
import { useAuthStore } from '../../stores/authStore'

export default function Header() {
  const { toggleSidebar } = useUIStore()
  const { user, logout } = useAuthStore()

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 lg:px-6">
      <button
        onClick={toggleSidebar}
        className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
      >
        <Menu className="w-5 h-5" />
      </button>

      <div className="flex-1" />

      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-600 hidden sm:block">
          {user?.email}
        </span>
        <button
          onClick={logout}
          className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg"
        >
          <User className="w-5 h-5" />
        </button>
      </div>
    </header>
  )
}
