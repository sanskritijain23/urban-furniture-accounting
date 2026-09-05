// TODO: manage current user/session (login, logout, role check).
// Backed by localStorage/sessionStorage token + services/auth.service.js.
export function useAuth() {
  return {
    user: null,
    isAuthenticated: false,
    login: async () => { throw new Error('not implemented') },
    logout: () => {},
  }
}
