import { Routes, Route } from 'react-router-dom'

import AuthRoutes from './routes/auth.routes.jsx'
import MastersRoutes from './routes/masters.routes.jsx'
import TransactionsRoutes from './routes/transactions.routes.jsx'
import BudgetRoutes from './routes/budget.routes.jsx'
import ReportsRoutes from './routes/reports.routes.jsx'
import PortalRoutes from './routes/portal.routes.jsx'

import Dashboard from './pages/dashboard/Dashboard.jsx'

/**
 * Root router. Split into per-domain route files under src/routes/
 * so two developers adding different pages rarely touch this file's
 * lines (see docs/architecture.md - merge conflict mitigation).
 */
export default function App() {
  return (
    <Routes>
      <Route path="/dashboard" element={<Dashboard />} />
      {AuthRoutes}
      {MastersRoutes}
      {TransactionsRoutes}
      {BudgetRoutes}
      {ReportsRoutes}
      {PortalRoutes}
    </Routes>
  )
}
