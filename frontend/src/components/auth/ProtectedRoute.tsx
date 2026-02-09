import { Navigate, useLocation } from "react-router-dom"
import { useAuthStore } from "@/stores/authStore"
import { LoadingOverlay } from "@/components/ui/Loading"

interface ProtectedRouteProps {
  children: React.ReactNode
  requireMFA?: boolean
}

export function ProtectedRoute({ children, requireMFA = false }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, requiresMFA, user } = useAuthStore()
  const location = useLocation()

  if (isLoading) {
    return <LoadingOverlay message="Loading..." />
  }

  // Not authenticated
  if (!isAuthenticated && !user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // MFA required but not completed
  if (requireMFA && requiresMFA) {
    return <Navigate to="/mfa-setup" state={{ from: location }} replace />
  }

  // If at login and already authenticated
  if (location.pathname === "/login" && isAuthenticated) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}