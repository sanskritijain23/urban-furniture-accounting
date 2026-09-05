// Shared table component for List views (Contacts, Products, Journals,
// etc.) with column config. Each column is { key, label, render? } —
// render(row) is optional and lets a page format a cell (currency,
// status badge, action buttons) instead of printing row[key] as-is.
export default function Table({ columns = [], rows = [], emptyMessage = 'No records found.' }) {
  if (rows.length === 0) {
    return <p className="card-empty">{emptyMessage}</p>
  }

  return (
    <table>
      <thead>
        <tr>{columns.map((c) => <th key={c.key}>{c.label}</th>)}</tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={row.id ?? i}>
            {columns.map((c) => (
              <td key={c.key}>{c.render ? c.render(row) : row[c.key]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
