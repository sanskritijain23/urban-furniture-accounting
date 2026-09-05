import { apiClient } from './apiClient.js'

export const listAnalyticAccounts = () => apiClient.get('/analytic-accounts/')
export const createAnalyticAccount = (payload) => apiClient.post('/analytic-accounts/', payload)
