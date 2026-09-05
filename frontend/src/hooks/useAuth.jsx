import { createContext, useContext, useState } from 'react'
import { login as loginRequest } from '../services/auth.service.js'

const TOKEN_KEY = 'ufa_token'
const USER_KEY = 'ufa_user'

const AuthContext = createContext(null)

function readStoredUser() {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(() => readStoredUser())

  async function login(loginId, password) {
    const response = await loginRequest(loginId, password)
    localStorage.setItem(TOKEN_KEY, response.access_token)
    // The login endpoint only returns a token, not user details, so we
    // keep the login id the user typed in for display purposes.
    const loggedInUser = { loginId }
    localStorage.setItem(USER_KEY, JSON.stringify(loggedInUser))
    setToken(response.access_token)
    setUser(loggedInUser)
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setToken(null)
    setUser(null)
  }

  const value = {
    user,
    isAuthenticated: Boolean(token),
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
