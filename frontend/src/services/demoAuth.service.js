// TEMPORARY demo-authentication fallback.
//
// This entire module exists only so the frontend can still be
// demoed end-to-end (all three roles) when the real backend isn't
// running. It is deliberately isolated to this one file plus its two
// call sites in hooks/useAuth.jsx — no page component imports this
// module directly or knows it exists, so removing it later (once the
// real backend is always available) means deleting this file and the
// small fallback branch in useAuth.jsx's login()/refresh effect, with
// zero changes anywhere else.
//
// The credential list below is intentionally not exported — only the
// three functions below it are. Nothing outside this file can read the
// login IDs/passwords directly.
const DEMO_TOKEN_PREFIX = 'demo-session:'

const DEMO_ACCOUNTS = [
  { loginId: 'admin01', password: 'Admin@123', role: 'admin' },
  { loginId: 'account01', password: 'Account@123', role: 'accountant' },
  { loginId: 'contact01', password: 'Contact@123', role: 'contact' },
]

/** Looks up a demo account by exact login ID + password match. Returns
 * null (never throws, never leaks *why* it didn't match) if there's no
 * match. */
export function findDemoAccount(loginId, password) {
  return DEMO_ACCOUNTS.find(
    (acc) => acc.loginId === loginId && acc.password === password
  ) ?? null
}

/** A demo session's "token" is just a tagged marker so useAuth can tell
 * it apart from a real JWT on page refresh, without ever needing to
 * call the (unavailable) real backend for that session again. */
export function issueDemoToken(loginId) {
  return `${DEMO_TOKEN_PREFIX}${loginId}`
}

export function isDemoToken(token) {
  return typeof token === 'string' && token.startsWith(DEMO_TOKEN_PREFIX)
}

/** Rebuilds the { loginId, role } pair a demo token was issued for, so
 * a demo session survives a page refresh without hitting the network.
 * Returns null if the token doesn't match a known demo account (e.g.
 * the fixed list changed) — the caller treats that as an invalid
 * session, same as an expired real token. */
export function getDemoUserFromToken(token) {
  if (!isDemoToken(token)) return null
  const loginId = token.slice(DEMO_TOKEN_PREFIX.length)
  const account = DEMO_ACCOUNTS.find((acc) => acc.loginId === loginId)
  return account ? { loginId: account.loginId, role: account.role } : null
}
