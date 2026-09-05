export default function FormField({ label, htmlFor, error, children }) {
  return (
    <div className="form-field">
      <label htmlFor={htmlFor}>{label}</label>
      {children}
      {error && <div className="form-field-error">{error}</div>}
    </div>
  )
}
