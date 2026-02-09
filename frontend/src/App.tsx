import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import { ROUTES } from './lib/constants'

// Pages
import Login from './pages/Login'
import Home from './pages/Home'
import Workspaces from './pages/Workspaces'
import Security from './pages/Security'

// Layouts
import MainLayout from './components/layout/MainLayout'
import AuthLayout from './components/layout/AuthLayout'
import ProtectedRoute from './components/auth/ProtectedRoute'

function App() {
  const { isLoading, setLoading } = useAuthStore()

  useEffect(() => {
    // Check for existing session
    const init = async () => {
      // TODO: Validate token with API
      setLoading(false)
    }
    init()
  }, [setLoading])

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <Routes>
      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route path={ROUTES.LOGIN} element={<Login />} />
      </Route>

      {/* Protected Routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>
          <Route path={ROUTES.HOME} element={<Home />} />
          <Route path={ROUTES.WORKSPACES} element={<Workspaces />} />
          <Route path={ROUTES.SECURITY} element={<Security />} />
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to={ROUTES.HOME} replace />} />
    </Routes>
  )
}

export default App
