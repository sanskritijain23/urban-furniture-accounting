import { apiClient } from './apiClient.js'

export const login = (loginId, password) =>
  apiClient.post('/auth/login', { login_id: loginId, password })

export const signup = (payload) => apiClient.post('/auth/signup', payload)

export const createUser = (payload) => apiClient.post('/users/', payload)

// Backend has no logout endpoint (JWT logout is stateless), so logging
// out only needs to clear the stored token. See hooks/useAuth.jsx.
export const logout = () => {}

// No GET /auth/me endpoint exists in the backend yet. Once the backend
// team adds one, call it here instead of relying on locally stored
// login details in hooks/useAuth.jsx.
export const getCurrentUser = () => apiClient.get('/auth/me')
