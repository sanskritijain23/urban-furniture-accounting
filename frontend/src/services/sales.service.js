import { apiClient } from './apiClient.js'

export const listSalesOrders = () => apiClient.get('/sales-orders/')
export const createSalesOrder = (payload) => apiClient.post('/sales-orders/', payload)
export const getSalesOrder = (id) => apiClient.get(`/sales-orders/${id}`)
export const confirmSalesOrder = (id) => apiClient.post(`/sales-orders/${id}/confirm`)
export const createInvoiceFromSO = (id, payload) => apiClient.post(`/sales-orders/${id}/create-invoice`, payload)

// List endpoint for Customer Invoices was not part of the original stub —
// added for Checkpoint 4's Customer Invoices list screen, following the
// same REST convention as every other list*() export in this codebase
// (GET on the plural collection root). Confirm with backend if the
// actual route differs.
export const listCustomerInvoices = () => apiClient.get('/customer-invoices/')
export const getCustomerInvoice = (id) => apiClient.get(`/customer-invoices/${id}`)
export const confirmCustomerInvoice = (id) => apiClient.post(`/customer-invoices/${id}/confirm`)
export const payCustomerInvoice = (id, payload) => apiClient.post(`/customer-invoices/${id}/pay`, payload)
