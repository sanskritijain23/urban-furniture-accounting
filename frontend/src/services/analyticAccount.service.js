import { apiClient } from './apiClient.js'

export const listAnalyticAccounts = () => apiClient.get('/analytic-accounts/')
export const getAnalyticAccount = (id) => apiClient.get(`/analytic-accounts/${id}`)
export const createAnalyticAccount = (payload) => apiClient.post('/analytic-accounts/', payload)
export const updateAnalyticAccount = (id, payload) =>
  apiClient.put(`/analytic-accounts/${id}`, payload)
// Deactivate/delete endpoint contract not confirmed with backend yet;
// following the same REST convention as the rest of this file.
export const deleteAnalyticAccount = (id) => apiClient.del(`/analytic-accounts/${id}`)
