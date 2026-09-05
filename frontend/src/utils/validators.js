// Shared client-side validators mirroring backend rules
// (login_id length, password complexity). Debit/credit balancing and
// other business-rule validators will be added with those modules.
export function isPasswordComplex(password) {
  return /^(?=.*[a-z])(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,}$/.test(password)
}

export function isValidLoginId(loginId) {
  return typeof loginId === 'string' && loginId.length >= 6 && loginId.length <= 12
}
