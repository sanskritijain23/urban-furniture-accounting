// Thin fetch wrapper — the ONLY place that knows the API base URL and
// attaches the auth token. All other services/* files call this
// instead of using fetch() directly.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

function getToken() {
  return localStorage.getItem('ufa_token')
}

async function request(path, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  if (!res.ok) {
    // TODO: standardize error handling/toast notifications
    throw new Error(`API error ${res.status}: ${await res.text()}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export const apiClient = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => request(path, { method: 'PUT', body: JSON.stringify(body) }),
  del: (path) => request(path, { method: 'DELETE' }),
}
