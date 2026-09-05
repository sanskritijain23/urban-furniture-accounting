// title/description-only usage (no children) renders the original
// "not built yet" placeholder box, so existing stub pages are untouched.
// Pages that pass children render a normal page header (title + optional
// actions, e.g. an "Add" button) followed by their own content.
export default function PageShell({ title, description, actions, children }) {
  if (!children) {
    return (
      <div className="page-shell">
        <h2>{title}</h2>
        <p>{description || 'This module is not built yet.'}</p>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>{title}</h2>
          {description && <p className="page-description">{description}</p>}
        </div>
        {actions && <div className="page-header-actions">{actions}</div>}
      </div>
      {children}
    </div>
  )
}
