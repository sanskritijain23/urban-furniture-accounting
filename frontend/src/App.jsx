import { Routes, Route, Navigate } from 'react-router-dom'

import AuthRoutes from './routes/auth.routes.jsx'
import MastersRoutes from './routes/masters.routes.jsx'
import TransactionsRoutes from './routes/transactions.routes.jsx'
import BudgetRoutes from './routes/budget.routes.jsx'
import ReportsRoutes from './routes/reports.routes.jsx'
import PortalRoutes from './routes/portal.routes.jsx'
import ProtectedRoute from './routes/ProtectedRoute.jsx'
import AdminRoute from './routes/AdminRoute.jsx'

import AppLayout from './layouts/AppLayout.jsx'
import Dashboard from './pages/dashboard/Dashboard.jsx'
import AdminCreateUser from './pages/auth/AdminCreateUser.jsx'

/**
 * Root router. Split into per-domain route files under src/routes/
 * so two developers adding different pages rarely touch this file's
 * lines (see docs/architecture.md - merge conflict mitigation).
 *
 * Everything except auth/portal pages sits behind ProtectedRoute and
 * shares AppLayout (sidebar + topbar) as a nested layout route.
 */
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      {AuthRoutes}
      {PortalRoutes}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          {MastersRoutes}
          {TransactionsRoutes}
          {BudgetRoutes}
          {ReportsRoutes}
          <Route element={<AdminRoute />}>
            <Route path="/admin/users/new" element={<AdminCreateUser />} />
          </Route>
        </Route>
      </Route>
      {/* Unknown paths fall back to /dashboard, which itself redirects
          unauthenticated users to /login and contacts to /portal — so
          this one route covers every role sensibly. */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
