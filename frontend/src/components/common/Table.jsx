// TODO: shared table component for List views (Contacts, Products,
// Journal Entries, etc.) with column config.
export default function Table({ columns = [], rows = [] }) {
  return (
    <table>
      <thead>
        <tr>{columns.map((c) => <th key={c.key}>{c.label}</th>)}</tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i}>{columns.map((c) => <td key={c.key}>{row[c.key]}</td>)}</tr>
        ))}
      </tbody>
    </table>
  )
}
