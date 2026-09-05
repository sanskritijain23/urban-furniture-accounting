import { apiClient } from './apiClient.js'

export const listJournalEntries = () => apiClient.get('/journal-entries/')
export const getJournalEntry = (id) => apiClient.get(`/journal-entries/${id}`)
export const createManualJournalEntry = (payload) => apiClient.post('/journal-entries/', payload)
export const postJournalEntry = (id) => apiClient.post(`/journal-entries/${id}/post`)
