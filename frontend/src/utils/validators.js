// TODO: shared client-side validators mirroring backend rules
// (login_id length, email format, password complexity, debit==credit).
export function isPasswordComplex(password) {
  return /^(?=.*[a-z])(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,}$/.test(password)
}
