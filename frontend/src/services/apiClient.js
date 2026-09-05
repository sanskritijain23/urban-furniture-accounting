// Thin fetch wrapper — the ONLY place that knows the API base URL and
// attaches the auth token. All other services/* files call this
// instead of using fetch() directly.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

function getToken() {
  return localStorage.getItem('ufa_token')
}

// FastAPI validation errors come back as:
//   { "detail": [ { "loc": [...], "msg": "...", "type": "..." }, ... ] }
// or, for non-validation errors, simply { "detail": "some string" }.
// This turns either shape into one readable line instead of the raw
// JSON blob previously shown to the user.
function formatErrorDetail(bodyText) {
  try {
    const parsed = JSON.parse(bodyText)
    const detail = parsed?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          const field = Array.isArray(item.loc) ? item.loc.at(-1) : null
          return field ? `${field}: ${item.msg}` : item.msg
        })
        .join('; ')
    }
  } catch {
    // Not JSON (or no `detail` key) — fall through to the raw text.
  }
  return bodyText
}

async function request(path, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }
  let res
  try {
    res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  } catch {
    // fetch() itself throws (not a non-2xx response) when the server is
    // unreachable — offline, backend down, CORS, etc. Surface something
    // readable instead of letting the raw "Failed to fetch" TypeError
    // reach the UI.
    throw new Error('Could not reach the server. Check your connection and try again.')
  }
  if (!res.ok) {
    const bodyText = await res.text()
    const err = new Error(formatErrorDetail(bodyText) || `API error ${res.status}`)
    // Callers (see hooks/useAuth.jsx's session refresh) need to tell a
    // real "token is invalid/expired" (401/403) apart from a transient
    // failure (500, a route that doesn't exist yet, etc.) — the message
    // string alone doesn't carry that, so attach the status code too.
    err.status = res.status
    throw err
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
