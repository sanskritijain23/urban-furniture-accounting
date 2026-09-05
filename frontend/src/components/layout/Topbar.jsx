import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth.jsx'
import Button from '../common/Button.jsx'
import ConfirmDialog from '../common/ConfirmDialog.jsx'

export default function Topbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [confirmingLogout, setConfirmingLogout] = useState(false)

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="topbar">
      <span className="topbar-user">
        Logged in as <strong>{user?.name || user?.loginId || 'user'}</strong>
      </span>
      <Button variant="secondary" onClick={() => setConfirmingLogout(true)}>
        Logout
      </Button>

      <ConfirmDialog
        open={confirmingLogout}
        title="Log out?"
        message="You'll need to sign in again to get back to the dashboard."
        confirmLabel="Logout"
        onConfirm={handleLogout}
        onCancel={() => setConfirmingLogout(false)}
      />
    </header>
  )
}
