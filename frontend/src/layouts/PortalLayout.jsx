// Shell for the restricted Contact Portal — deliberately minimal nav
// (no master-data links), since contacts can only view+pay their own docs.
// Used as a layout route (see routes/portal.routes.jsx), so page content
// comes from <Outlet />, matching the AppLayout convention.
import { Outlet, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../hooks/useAuth.jsx'
import Button from '../components/common/Button.jsx'
import ConfirmDialog from '../components/common/ConfirmDialog.jsx'

export default function PortalLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [confirmingLogout, setConfirmingLogout] = useState(false)

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="portal-layout">
      <header className="topbar">
        <span className="topbar-user">
          Logged in as <strong>{user?.name || user?.loginId || 'contact'}</strong>
        </span>
        <Button variant="secondary" onClick={() => setConfirmingLogout(true)}>
          Logout
        </Button>
      </header>
      <main className="app-content">
        <Outlet />
      </main>

      <ConfirmDialog
        open={confirmingLogout}
        title="Log out?"
        message="You'll need to sign in again to view your invoices, bills, or make a payment."
        confirmLabel="Logout"
        onConfirm={handleLogout}
        onCancel={() => setConfirmingLogout(false)}
      />
    </div>
  )
}
