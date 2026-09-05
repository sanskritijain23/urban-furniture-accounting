import { apiClient } from './apiClient.js'

export const getBalanceSheet = (year) => apiClient.get(`/reports/balance-sheet?year=${year}`)
export const getProfitAndLoss = (year) => apiClient.get(`/reports/profit-loss?year=${year}`)
export const getBudgetReport = (year) => apiClient.get(`/reports/budget?year=${year}`)

// General Ledger for one account. Endpoint contract not confirmed with
// backend yet — following the same /reports/* REST convention as the
// other report endpoints above, filtered by account_id (required) and
// year (optional). Adjust the path/params here if the API differs;
// nothing else in Ledger.jsx should need to change.
export const getLedger = (accountId, year) => {
  const params = new URLSearchParams()
  if (accountId) params.set('account_id', accountId)
  if (year) params.set('year', year)
  return apiClient.get(`/reports/ledger?${params.toString()}`)
}
