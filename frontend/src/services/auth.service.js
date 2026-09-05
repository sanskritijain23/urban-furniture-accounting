import { apiClient } from './apiClient.js'

export const login = (loginId, password) =>
  apiClient.post('/auth/login', { login_id: loginId, password })

export const signup = (payload) => apiClient.post('/auth/signup', payload)

export const createUser = (payload) => apiClient.post('/users/', payload)

// Backend has no logout endpoint (JWT logout is stateless), so logging
// out only needs to clear the stored token. See hooks/useAuth.jsx.
export const logout = () => {}

// Backend Checkpoint 1 exposes the current user at GET /users/me
// (there is no /auth/me route).
export const getCurrentUser = () => apiClient.get('/users/me')
