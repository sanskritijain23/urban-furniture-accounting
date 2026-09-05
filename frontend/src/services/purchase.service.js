import { apiClient } from './apiClient.js'

export const listPurchaseOrders = () => apiClient.get('/purchase-orders/')
export const createPurchaseOrder = (payload) => apiClient.post('/purchase-orders/', payload)
export const getPurchaseOrder = (id) => apiClient.get(`/purchase-orders/${id}`)
export const confirmPurchaseOrder = (id) => apiClient.post(`/purchase-orders/${id}/confirm`)
export const createBillFromPO = (id, payload) => apiClient.post(`/purchase-orders/${id}/create-bill`, payload)

// List endpoint for Vendor Bills was not part of the original stub —
// added for Checkpoint 3's Vendor Bills list screen, following the
// same REST convention as every other list*() export in this file
// (GET on the plural collection root). Confirm with backend if the
// actual route differs.
export const listVendorBills = () => apiClient.get('/vendor-bills/')
export const getVendorBill = (id) => apiClient.get(`/vendor-bills/${id}`)
export const confirmVendorBill = (id) => apiClient.post(`/vendor-bills/${id}/confirm`)
export const payVendorBill = (id, payload) => apiClient.post(`/vendor-bills/${id}/pay`, payload)
