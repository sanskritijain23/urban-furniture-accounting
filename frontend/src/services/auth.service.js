import { apiClient } from './apiClient.js'

export const login = (loginId, password) =>
  apiClient.post('/auth/login', { login_id: loginId, password })

export const signup = (payload) => apiClient.post('/auth/signup', payload)

export const createUser = (payload) => apiClient.post('/users/', payload)
