import { apiClient } from './apiClient.js'

export const listProducts = () => apiClient.get('/products/')
export const getProduct = (id) => apiClient.get(`/products/${id}`)
export const createProduct = (payload) => apiClient.post('/products/', payload)
export const updateProduct = (id, payload) => apiClient.put(`/products/${id}`, payload)
export const createCategory = (payload) => apiClient.post('/products/categories', payload)
export const listCategories = () => apiClient.get('/products/categories')
