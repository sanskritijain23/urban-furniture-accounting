import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'

// Guards admin-only pages within the main app shell (currently just
// /admin/users/new). Nested inside ProtectedRoute, so isAuthenticated
// and the contact->/portal redirect are already handled by the time
// this runs — this only adds the stricter "must actually be an admin,
// not just an accountant" check on top.
export default function AdminRoute() {
  const { isAuthenticated, authLoading, role } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (authLoading) {
    return <div className="page-shell"><p className="card-empty">Loading...</p></div>
  }

  if (role !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
