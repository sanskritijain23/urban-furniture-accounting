import { NavLink } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth.jsx'

const NAV_ITEMS = [
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Contacts', to: '/contacts' },
  { label: 'Products', to: '/products' },
  { label: 'Chart of Accounts', to: '/accounts' },
  { label: 'Journals', to: '/journals' },
  { label: 'Analytic Accounts', to: '/analytics' },
  { label: 'Purchase', to: '/purchases/orders' },
  { label: 'Sales', to: '/sales/orders' },
  { label: 'Payments', to: '/payments' },
  { label: 'Accounting', to: '/journal-entries' },
  { label: 'Ledger', to: '/reports/ledger' },
  { label: 'Balance Sheet', to: '/reports/balance-sheet' },
  { label: 'Profit & Loss', to: '/reports/profit-loss' },
  { label: 'Budget', to: '/budgets' },
  { label: 'Budget Report', to: '/reports/budget' },
]

// Shown only to admins — the route itself is also enforced by
// routes/AdminRoute.jsx, this just keeps the link from appearing for
// accountants who'd be bounced straight back to /dashboard anyway.
const ADMIN_NAV_ITEM = { label: 'Create User', to: '/admin/users/new' }

export default function Sidebar() {
  const { role } = useAuth()

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">Urban Furniture</div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
          >
            {item.label}
          </NavLink>
        ))}
        {role === 'admin' && (
          <NavLink
            key={ADMIN_NAV_ITEM.to}
            to={ADMIN_NAV_ITEM.to}
            className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
          >
            {ADMIN_NAV_ITEM.label}
          </NavLink>
        )}
      </nav>
    </aside>
  )
}
