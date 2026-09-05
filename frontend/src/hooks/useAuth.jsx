import { createContext, useContext, useEffect, useState } from 'react'
import { login as loginRequest, getCurrentUser } from '../services/auth.service.js'
import {
  findDemoAccount,
  issueDemoToken,
  isDemoToken,
  getDemoUserFromToken,
} from '../services/demoAuth.service.js'

const TOKEN_KEY = 'ufa_token'
const USER_KEY = 'ufa_user'

const AuthContext = createContext(null)

// Single message shown for every login failure — a real backend
// rejection, a real backend that's unreachable with no matching demo
// account, or a demo lookup miss. Never leaks backend error text and
// never hints at which of those actually happened.
const INVALID_CREDENTIALS_MESSAGE = 'Invalid login ID or password'

function readStoredUser() {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

// GET /users/me's exact field names for role/contact linkage aren't
// confirmed against the backend, so this normalizes whichever of these
// commonly-used names comes back into one lowercase `role` string that
// the rest of the app (route guards, portal redirect) can rely on.
// Falls back to 'user' (the accountant/invoicing-user role) if nothing
// matches, so an unrecognised shape never accidentally locks a real
// admin/accountant user out of the app.
function normalizeRole(profile) {
  const raw = profile?.role ?? profile?.user_role ?? profile?.type ?? ''
  return String(raw).toLowerCase() || 'user'
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(() => readStoredUser())
  // True while we still don't know the logged-in user's role (either
  // right after login, or right after a page refresh where only the
  // token survived). Route guards wait on this instead of guessing.
  const [authLoading, setAuthLoading] = useState(Boolean(localStorage.getItem(TOKEN_KEY)))

  // On refresh, only the token and last-known user survive in
  // localStorage. Re-fetch the full profile (role, contact_id, etc.) so
  // role-based route protection has fresh data instead of stale/missing
  // role info from a previous session.
  useEffect(() => {
    if (!token) {
      setAuthLoading(false)
      return
    }

    // A demo session's role is already fully known from the token
    // itself (see demoAuth.service.js) — no network call needed, and
    // none would succeed anyway, since the real backend being down is
    // exactly why this session exists in the first place.
    if (isDemoToken(token)) {
      const demoUser = getDemoUserFromToken(token)
      if (demoUser) {
        localStorage.setItem(USER_KEY, JSON.stringify(demoUser))
        setUser(demoUser)
      } else {
        // Token doesn't match any current demo account — treat like an
        // expired/invalid real session rather than getting stuck.
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(USER_KEY)
        setToken(null)
        setUser(null)
      }
      setAuthLoading(false)
      return
    }

    let cancelled = false
    getCurrentUser()
      .then((profile) => {
        if (cancelled) return
        const refreshedUser = {
          ...(readStoredUser() || {}),
          ...profile,
          role: normalizeRole(profile),
        }
        localStorage.setItem(USER_KEY, JSON.stringify(refreshedUser))
        setUser(refreshedUser)
      })
      .catch((err) => {
        if (cancelled) return
        // Only a real "token rejected" response (401/403) should log the
        // user out here. Anything else — a network blip, /users/me
        // being briefly unreachable, a 500 — must NOT wipe a valid
        // session; that would silently kick an already-logged-in admin/
        // accountant back to /login on an ordinary page refresh. The
        // previously-stored user (with its last-known role) is kept as-is
        // so route guards keep working off stale-but-valid data instead
        // of losing role info entirely.
        if (err?.status === 401 || err?.status === 403) {
          localStorage.removeItem(TOKEN_KEY)
          localStorage.removeItem(USER_KEY)
          setToken(null)
          setUser(null)
        }
      })
      .finally(() => {
        if (!cancelled) setAuthLoading(false)
      })
    return () => { cancelled = true }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function login(loginId, password) {
    try {
      const response = await loginRequest(loginId, password)
      localStorage.setItem(TOKEN_KEY, response.access_token)
      setToken(response.access_token)
      setAuthLoading(true)
      // The login endpoint only returns a token, not user details, so the
      // login id typed in is kept as a display fallback while the real
      // profile (including role) is fetched.
      let loggedInUser = { loginId, role: 'user' }
      try {
        const profile = await getCurrentUser()
        loggedInUser = { loginId, ...profile, role: normalizeRole(profile) }
      } catch {
        // Profile fetch failing shouldn't block a successful login —
        // the user just won't get role-based redirect/guarding until the
        // next successful fetch.
      }
      localStorage.setItem(USER_KEY, JSON.stringify(loggedInUser))
      setUser(loggedInUser)
      setAuthLoading(false)
      return loggedInUser
    } catch (err) {
      // apiClient.js attaches `.status` whenever the server actually
      // responded (see services/apiClient.js) — including a 401 for
      // wrong credentials. A response with a status means the real
      // backend is reachable and rejected this login itself, so the
      // temporary demo fallback below must NOT run: falling back here
      // would mean a real backend's "invalid credentials" could still
      // let someone in just because the fixed demo list happens to
      // contain a match, which defeats the point of real auth.
      if (err?.status != null) {
        throw new Error(INVALID_CREDENTIALS_MESSAGE)
      }

      // No `.status` means the request never got a response at all —
      // apiClient.js's fetch() call itself threw (offline, backend not
      // running, CORS, etc.), i.e. the real backend is unreachable
      // rather than merely rejecting these credentials. Only in this
      // specific case does the temporary demo fallback apply.
      const demoAccount = findDemoAccount(loginId, password)
      if (!demoAccount) {
        throw new Error(INVALID_CREDENTIALS_MESSAGE)
      }
      const demoToken = issueDemoToken(demoAccount.loginId)
      const demoUser = { loginId: demoAccount.loginId, role: demoAccount.role }
      localStorage.setItem(TOKEN_KEY, demoToken)
      localStorage.setItem(USER_KEY, JSON.stringify(demoUser))
      setToken(demoToken)
      setUser(demoUser)
      setAuthLoading(false)
      return demoUser
    }
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setToken(null)
    setUser(null)
  }

  const value = {
    user,
    role: user?.role ?? null,
    isAuthenticated: Boolean(token),
    authLoading,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
