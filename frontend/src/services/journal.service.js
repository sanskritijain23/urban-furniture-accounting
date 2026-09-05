import { apiClient } from './apiClient.js'

export const listJournals = () => apiClient.get('/journals/')
export const createJournal = (payload) => apiClient.post('/journals/', payload)
