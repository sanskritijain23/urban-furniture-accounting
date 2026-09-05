import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'

// Guards the admin/accountant area (dashboard, masters, transactions,
// budget, reports). Contacts are authenticated users too, but per the
// Contact Portal spec they must not reach master-data create/edit
// screens or any other business-side page — they're sent to their own
// portal instead.
export default function ProtectedRoute() {
  const { isAuthenticated, authLoading, role } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Wait for the role to be known before deciding whether this is the
  // right area for this user, rather than briefly rendering admin pages
  // (or bouncing a real admin to /portal) while the profile is in flight.
  if (authLoading) {
    return <div className="page-shell"><p className="card-empty">Loading...</p></div>
  }

  if (role === 'contact') {
    return <Navigate to="/portal" replace />
  }

  return <Outlet />
}
