import { apiClient } from './apiClient.js'

export const listContacts = () => apiClient.get('/contacts/')
export const getContact = (id) => apiClient.get(`/contacts/${id}`)
export const createContact = (payload) => apiClient.post('/contacts/', payload)
export const updateContact = (id, payload) => apiClient.put(`/contacts/${id}`, payload)
// Deactivate/delete endpoint contract not confirmed with backend yet;
// following the same REST convention as the rest of this file.
export const deleteContact = (id) => apiClient.del(`/contacts/${id}`)
