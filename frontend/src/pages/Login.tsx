import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useUIStore } from '../stores/uiStore'
import { api } from '../lib/api'
import { ROUTES } from '../lib/constants'
import { Mail, Lock, Loader2 } from 'lucide-react'

export default function Login() {
  const navigate = useNavigate()
  const { setUser, setToken, setRefreshToken, setAuthenticated, setMFARequired, setTempToken } = useAuthStore()
  const { addNotification } = useUIStore()
  
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [mfaCode, setMfaCode] = useState('')
  const [showMFA, setShowMFA] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await api.login(email, password)
      
      if (response.data.mfaRequired) {
        setShowMFA(true)
        setTempToken(response.data.tempToken)
        return
      }

      setToken(response.data.token)
      setRefreshToken(response.data.refreshToken)
      setUser(response.data.user)
      setAuthenticated(true)
      navigate(ROUTES.HOME)
    } catch (error: any) {
      addNotification({
        id: Date.now().toString(),
        type: 'error',
        title: 'Login failed',
        message: error.response?.data?.message || 'Invalid credentials',
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleMFASubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const tempToken = useAuthStore.getState().tempToken
      const response = await api.verifyMFA(mfaCode, tempToken!)
      
      setToken(response.data.token)
      setRefreshToken(response.data.refreshToken)
      setUser(response.data.user)
      setAuthenticated(true)
      setMFARequired(false)
      setTempToken(null)
      navigate(ROUTES.HOME)
    } catch (error: any) {
      addNotification({
        id: Date.now().toString(),
        type: 'error',
        title: 'MFA verification failed',
        message: error.response?.data?.message || 'Invalid code',
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-md">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-primary-600 rounded-xl flex items-center justify-center mx-auto mb-4">
          <span className="text-white font-bold text-2xl">X</span>
        </div>
        <h1 className="text-2xl font-bold">Area X</h1>
        <p className="text-gray-500 mt-2">
          {showMFA ? 'Enter your MFA code' : 'Sign in to your account'}
        </p>
      </div>

      <form onSubmit={showMFA ? handleMFASubmit : handleSubmit} className="space-y-4">
        {!showMFA ? (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>
          </>
        ) : (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              MFA Code
            </label>
            <input
              type="text"
              value={mfaCode}
              onChange={(e) => setMfaCode(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="000000"
              maxLength={6}
              required
            />
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Signing in...
            </>
          ) : (
            showMFA ? 'Verify' : 'Sign in'
          )}
        </button>
      </form>
    </div>
  )
}
