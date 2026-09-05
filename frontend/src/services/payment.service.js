import { apiClient } from './apiClient.js'

export const listPayments = () => apiClient.get('/payments/')
export const getPayment = (id) => apiClient.get(`/payments/${id}`)
export const confirmPayment = (id) => apiClient.post(`/payments/${id}/confirm`)
