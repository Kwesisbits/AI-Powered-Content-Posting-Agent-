'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { jwtDecode } from 'jwt-decode'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'

interface User {
  id: number
  email: string
  full_name: string | null
  role: 'admin' | 'reviewer' | 'client'
  is_active: boolean
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check for stored token on mount
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      try {
        const decoded: any = jwtDecode(storedToken)
        const userData = JSON.parse(localStorage.getItem('user') || '{}')
        
        // Check if token is expired
        if (decoded.exp * 1000 > Date.now()) {
          setToken(storedToken)
          setUser(userData)
          api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
        } else {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
        }
      } catch (error) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      const { access_token, user } = response.data
      
      // Store token and user
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(user))
      
      // Update state
      setToken(access_token)
      setUser(user)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      toast.success(`Welcome back, ${user.full_name || user.email}!`)
      
      // Redirect based on role
      if (user.role === 'admin') {
        router.push('/dashboard')
      } else if (user.role === 'reviewer') {
        router.push('/approvals')
      } else {
        router.push('/content')
      }
      
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed')
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
    delete api.defaults.headers.common['Authorization']
    router.push('/')
    toast.success('Logged out successfully')
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
