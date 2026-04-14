import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface User {
  id: number
  email: string
  full_name: string | null
  plan: 'free' | 'pro' | 'enterprise'
  is_verified: boolean
  daily_scans: number
  daily_limit: number
  created_at: string
}

interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('va_token'))
  const [loading, setLoading] = useState(true)

  const authHeader = (t = token) => t ? { Authorization: `Bearer ${t}` } : {}

  const refreshUser = async () => {
    if (!token) { setLoading(false); return }
    try {
      const { data } = await axios.get(`${API}/api/auth/me`, { headers: authHeader() })
      setUser(data)
    } catch {
      setToken(null)
      setUser(null)
      localStorage.removeItem('va_token')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { refreshUser() }, [token]) // eslint-disable-line

  const login = async (email: string, password: string) => {
    const { data } = await axios.post(`${API}/api/auth/login`, { email, password })
    localStorage.setItem('va_token', data.access_token)
    setToken(data.access_token)
    setUser(data.user)
  }

  const register = async (email: string, password: string, fullName?: string) => {
    const { data } = await axios.post(`${API}/api/auth/register`, {
      email,
      password,
      full_name: fullName || null,
    })
    localStorage.setItem('va_token', data.access_token)
    setToken(data.access_token)
    setUser(data.user)
  }

  const logout = () => {
    localStorage.removeItem('va_token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
