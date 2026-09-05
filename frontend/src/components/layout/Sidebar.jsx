import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Contacts', to: '/contacts' },
  { label: 'Products', to: '/products' },
  { label: 'Purchase', to: '/purchases/orders' },
  { label: 'Sales', to: '/sales/orders' },
  { label: 'Accounting', to: '/journal-entries' },
  { label: 'Reports', to: '/reports/balance-sheet' },
  { label: 'Budget', to: '/budgets' },
]

export default function Sidebar() {
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
      </nav>
    </aside>
  )
}
