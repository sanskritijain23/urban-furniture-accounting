import { apiClient } from './apiClient.js'

export const listProducts = () => apiClient.get('/products/')
export const getProduct = (id) => apiClient.get(`/products/${id}`)
export const createProduct = (payload) => apiClient.post('/products/', payload)
export const updateProduct = (id, payload) => apiClient.put(`/products/${id}`, payload)
// Deactivate/delete endpoint contract not confirmed with backend yet;
// following the same REST convention as the rest of this file.
export const deleteProduct = (id) => apiClient.del(`/products/${id}`)
export const createCategory = (payload) => apiClient.post('/products/categories', payload)
export const listCategories = () => apiClient.get('/products/categories')
