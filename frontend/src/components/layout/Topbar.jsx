import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth.jsx'
import Button from '../common/Button.jsx'

export default function Topbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="topbar">
      <span className="topbar-user">
        Logged in as <strong>{user?.loginId || 'user'}</strong>
      </span>
      <Button variant="secondary" onClick={handleLogout}>
        Logout
      </Button>
    </header>
  )
}
