// Route: /signup
// Public sign-up. Always creates a role=accountant user (server-enforced).
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../../layouts/AuthLayout.jsx'
import FormField from '../../components/forms/FormField.jsx'
import Button from '../../components/common/Button.jsx'
import { signup } from '../../services/auth.service.js'
import { isPasswordComplex, isValidLoginId } from '../../utils/validators.js'

export default function Signup() {
  const navigate = useNavigate()

  const [form, setForm] = useState({
    name: '',
    loginId: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function validate() {
    if (!isValidLoginId(form.loginId)) {
      return 'Login ID must be between 6 and 12 characters.'
    }
    if (!form.email.trim()) {
      return 'Email is required.'
    }
    if (!isPasswordComplex(form.password)) {
      return 'Password must be at least 8 characters and include an uppercase letter, a lowercase letter, and a special character.'
    }
    if (form.password !== form.confirmPassword) {
      return 'Passwords do not match.'
    }
    return ''
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }

    setError('')
    setLoading(true)
    try {
      await signup({
        login_id: form.loginId.trim(),
        email: form.email.trim(),
        password: form.password,
        name: form.name.trim() || undefined,
      })
      navigate('/login', { state: { signupSuccess: true } })
    } catch (err) {
      setError(err.message || 'Sign up failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout subtitle="Create your account">
      <form onSubmit={handleSubmit}>
        {error && <div className="form-error-banner">{error}</div>}

        <FormField label="Name" htmlFor="name">
          <input
            id="name"
            type="text"
            value={form.name}
            onChange={(e) => updateField('name', e.target.value)}
          />
        </FormField>

        <FormField label="Login ID" htmlFor="loginId">
          <input
            id="loginId"
            type="text"
            value={form.loginId}
            onChange={(e) => updateField('loginId', e.target.value)}
            autoComplete="username"
          />
        </FormField>

        <FormField label="Email" htmlFor="email">
          <input
            id="email"
            type="email"
            value={form.email}
            onChange={(e) => updateField('email', e.target.value)}
            autoComplete="email"
          />
        </FormField>

        <FormField label="Password" htmlFor="password">
          <input
            id="password"
            type="password"
            value={form.password}
            onChange={(e) => updateField('password', e.target.value)}
            autoComplete="new-password"
          />
        </FormField>

        <FormField label="Re-enter Password" htmlFor="confirmPassword">
          <input
            id="confirmPassword"
            type="password"
            value={form.confirmPassword}
            onChange={(e) => updateField('confirmPassword', e.target.value)}
            autoComplete="new-password"
          />
        </FormField>

        <Button type="submit" block disabled={loading}>
          {loading ? 'Creating account...' : 'Sign Up'}
        </Button>
      </form>

      <p className="auth-footer">
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </AuthLayout>
  )
}
