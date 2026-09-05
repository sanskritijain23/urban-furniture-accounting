import { apiClient } from './apiClient.js'

export const listAccounts = () => apiClient.get('/accounts/')
export const createAccount = (payload) => apiClient.post('/accounts/', payload)
export const updateAccount = (id, payload) => apiClient.put(`/accounts/${id}`, payload)
