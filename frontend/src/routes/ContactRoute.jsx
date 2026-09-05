import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'

// Guards the Contact Portal (/portal). Role allowed: contact ONLY —
// admin/accountant users are sent to the main dashboard instead, since
// the portal deliberately has none of the master-data/reporting nav
// they'd expect.
export default function ContactRoute() {
  const { isAuthenticated, authLoading, role } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (authLoading) {
    return <div className="page-shell"><p className="card-empty">Loading...</p></div>
  }

  if (role !== 'contact') {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
