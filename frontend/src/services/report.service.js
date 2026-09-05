import { apiClient } from './apiClient.js'

export const getBalanceSheet = (year) => apiClient.get(`/reports/balance-sheet?year=${year}`)
export const getProfitAndLoss = (year) => apiClient.get(`/reports/profit-loss?year=${year}`)
export const getBudgetReport = (year) => apiClient.get(`/reports/budget?year=${year}`)
