// Shell for the public Login/Signup pages — centered card, app logo.
// (Admin: Create User is a separate, authenticated admin-only page that
// uses AppLayout instead — see routes/AdminRoute.jsx.)
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
