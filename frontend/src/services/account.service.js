import { apiClient } from './apiClient.js'

export const listAccounts = () => apiClient.get('/accounts/')
export const getAccount = (id) => apiClient.get(`/accounts/${id}`)
export const createAccount = (payload) => apiClient.post('/accounts/', payload)
export const updateAccount = (id, payload) => apiClient.put(`/accounts/${id}`, payload)
// Deactivate/delete endpoint contract not confirmed with backend yet;
// following the same REST convention as the rest of this file.
export const deleteAccount = (id) => apiClient.del(`/accounts/${id}`)
