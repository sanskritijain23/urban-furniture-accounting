// Shell for Login/Signup/AdminCreateUser — centered card, app logo.
export default function AuthLayout({ subtitle, children }) {
  return (
    <div className="auth-layout">
      <div className="auth-card">
        <h1>Urban Furniture Accounting</h1>
        {subtitle && <p className="auth-subtitle">{subtitle}</p>}
        {children}
      </div>
    </div>
  )
}
