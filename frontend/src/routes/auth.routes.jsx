import { Route } from 'react-router-dom'
import Login from '../pages/auth/Login.jsx'
import Signup from '../pages/auth/Signup.jsx'

// Admin: Create User (/admin/users/new) is NOT listed here — it's an
// authenticated, admin-only page, not a public auth page. It lives
// under App.jsx's main ProtectedRoute + AppLayout, gated further by
// AdminRoute. Registering it here would have made it publicly
// reachable with no login at all, which is what the placeholder
// version of this route actually did.
export default [
  <Route key="login" path="/login" element={<Login />} />,
  <Route key="signup" path="/signup" element={<Signup />} />,
]
