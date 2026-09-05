// Route: /login
import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import AuthLayout from '../../layouts/AuthLayout.jsx'
import FormField from '../../components/forms/FormField.jsx'
import Button from '../../components/common/Button.jsx'
import { useAuth } from '../../hooks/useAuth.jsx'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const signupSuccess = location.state?.signupSuccess

  const [loginId, setLoginId] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (!loginId.trim() || !password) {
      setError('Login ID and password are required.')
      return
    }

    setLoading(true)
    try {
      await login(loginId.trim(), password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout subtitle="Sign in to your account">
      <form onSubmit={handleSubmit}>
        {signupSuccess && !error && (
          <div className="form-success-banner">Account created. You can now sign in.</div>
        )}
        {error && <div className="form-error-banner">{error}</div>}

        <FormField label="Login ID" htmlFor="loginId">
          <input
            id="loginId"
            type="text"
            value={loginId}
            onChange={(e) => setLoginId(e.target.value)}
            autoComplete="username"
          />
        </FormField>

        <FormField label="Password" htmlFor="password">
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
        </FormField>

        <Button type="submit" block disabled={loading}>
          {loading ? 'Signing in...' : 'Sign In'}
        </Button>
      </form>

      <p className="auth-footer">
        Don't have an account? <Link to="/signup">Sign up</Link>
      </p>
    </AuthLayout>
  )
}
