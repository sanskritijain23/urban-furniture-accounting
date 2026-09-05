import { Route } from 'react-router-dom'
import ContactPortal from '../pages/portal/ContactPortal.jsx'
import ContactRoute from './ContactRoute.jsx'
import PortalLayout from '../layouts/PortalLayout.jsx'

// Checkpoint 7: /portal is gated to role=contact by ContactRoute and
// wrapped in the minimal PortalLayout (no master-data/admin nav), same
// nesting pattern as the admin area's ProtectedRoute + AppLayout in App.jsx.
export default [
  <Route key="portal" element={<ContactRoute />}>
    <Route element={<PortalLayout />}>
      <Route path="/portal" element={<ContactPortal />} />
    </Route>
  </Route>,
]
