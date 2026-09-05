// TODO: currency (Rs./INR) and date formatting helpers shared across pages.
export function formatCurrency(amount) {
  return `Rs. ${Number(amount ?? 0).toLocaleString('en-IN')}`
}

export function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-IN')
}

// Used by Budget detail/list for Achieved % (backend-calculated, see
// budget.service.js). Accepts either a fraction (0.42) or an already
// backend-scaled percentage (42) — anything over 3 is treated as
// already-a-percentage rather than a fraction, since real fractions
// for this field never exceed ~3x.
export function formatPercent(value) {
  if (value === null || value === undefined || value === '') return '—'
  const num = Number(value)
  if (Number.isNaN(num)) return '—'
  const pct = Math.abs(num) > 3 ? num : num * 100
  return `${pct.toLocaleString('en-IN', { maximumFractionDigits: 1 })}%`
}
