import { apiClient } from './apiClient.js'

export const listBudgets = () => apiClient.get('/budgets/')
export const createBudget = (payload) => apiClient.post('/budgets/', payload)
export const getBudget = (id) => apiClient.get(`/budgets/${id}`)
export const confirmBudget = (id) => apiClient.post(`/budgets/${id}/confirm`)
export const reviseBudget = (id, payload) => apiClient.post(`/budgets/${id}/revise`, payload)
export const cancelBudget = (id) => apiClient.post(`/budgets/${id}/cancel`)
