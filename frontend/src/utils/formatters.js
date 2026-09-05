// TODO: currency (Rs./INR) and date formatting helpers shared across pages.
export function formatCurrency(amount) {
  return `Rs. ${Number(amount ?? 0).toLocaleString('en-IN')}`
}

export function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-IN')
}
