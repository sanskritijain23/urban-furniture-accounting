import { apiClient } from './apiClient.js'

export const listContacts = () => apiClient.get('/contacts/')
export const getContact = (id) => apiClient.get(`/contacts/${id}`)
export const createContact = (payload) => apiClient.post('/contacts/', payload)
export const updateContact = (id, payload) => apiClient.put(`/contacts/${id}`, payload)
