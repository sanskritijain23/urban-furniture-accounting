// Route: /dashboard
// Role allowed: admin, accountant
import { useAuth } from '../../hooks/useAuth.jsx'

const SECTIONS = ['Sales', 'Purchase', 'Accounting', 'Reports', 'Budget']

export default function Dashboard() {
  const { user } = useAuth()

  return (
    <div>
      <h2>Dashboard</h2>
      <p>Welcome{user?.loginId ? `, ${user.loginId}` : ''}.</p>

      <div className="dashboard-grid">
        {SECTIONS.map((section) => (
          <div className="card" key={section}>
            <h3>{section}</h3>
            <p className="card-empty">No data available</p>
          </div>
        ))}
      </div>
    </div>
  )
}
