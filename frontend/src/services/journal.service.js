import { apiClient } from './apiClient.js'

export const listJournals = () => apiClient.get('/journals/')
export const getJournal = (id) => apiClient.get(`/journals/${id}`)
export const createJournal = (payload) => apiClient.post('/journals/', payload)
export const updateJournal = (id, payload) => apiClient.put(`/journals/${id}`, payload)
// Deactivate/delete endpoint contract not confirmed with backend yet;
// following the same REST convention as the rest of this file.
export const deleteJournal = (id) => apiClient.del(`/journals/${id}`)
