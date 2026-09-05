export default function PageShell({ title, description }) {
  return (
    <div className="page-shell">
      <h2>{title}</h2>
      <p>{description || 'This module is not built yet.'}</p>
    </div>
  )
}
