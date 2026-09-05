// TODO: reusable labeled input wrapper used across master/transaction forms.
export default function FormField({ label, children }) {
  return (
    <div className="form-field">
      <label>{label}</label>
      {children}
    </div>
  )
}
