// Shared year dropdown for report pages (Ledger, Balance Sheet, P&L).
// Purely a UI filter — the selected year is sent to the backend report
// endpoint as a query param; this component does no date math beyond
// building the list of selectable years.
const CURRENT_YEAR = new Date().getFullYear()
const YEARS = Array.from({ length: 7 }, (_, i) => CURRENT_YEAR - i)

export default function YearFilter({ value, onChange, label = 'Year' }) {
  return (
    <div className="form-field year-filter">
      <label htmlFor="year-filter-select">{label}</label>
      <select
        id="year-filter-select"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      >
        {YEARS.map((y) => (
          <option key={y} value={y}>{y}</option>
        ))}
      </select>
    </div>
  )
}
