import { Route } from 'react-router-dom'
import Login from '../pages/auth/Login.jsx'
import Signup from '../pages/auth/Signup.jsx'
import AdminCreateUser from '../pages/auth/AdminCreateUser.jsx'

export default [
  <Route key="login" path="/login" element={<Login />} />,
  <Route key="signup" path="/signup" element={<Signup />} />,
  <Route key="admin-create-user" path="/admin/users/new" element={<AdminCreateUser />} />,
]
