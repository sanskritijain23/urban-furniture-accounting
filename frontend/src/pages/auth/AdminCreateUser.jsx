// Route: /admin/users/new
// Role allowed: admin only — enforced by routes/AdminRoute.jsx, nested
// inside the main ProtectedRoute + AppLayout in App.jsx (see that
// file's comment: this used to be registered as a public auth route
// with no login required at all, which was a real access bug on top
// of being an unbuilt placeholder).
//
// Reuses the exact same createUser() call and password/login-id
// validators Signup.jsx already uses — the only real difference is an
// admin can also pick the role (Signup always creates 'accountant'
// server-side).
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import FormField from '../../components/forms/FormField.jsx'
import Button from '../../components/common/Button.jsx'
import { createUser } from '../../services/auth.service.js'
import { isPasswordComplex, isValidLoginId } from '../../utils/validators.js'
import { USER_ROLE_MAP, USER_ROLE_OPTIONS, toBackendEnum } from '../../utils/enumMap.js'

const EMPTY_FORM = {
  name: '',
  loginId: '',
  email: '',
  role: 'Accountant',
  password: '',
  confirmPassword: '',
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export default function AdminCreateUser() {
  const navigate = useNavigate()

  const [form, setForm] = useState(EMPTY_FORM)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [saving, setSaving] = useState(false)

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function validate() {
    if (!isValidLoginId(form.loginId)) {
      return 'Login ID must be between 6 and 12 characters.'
    }
    if (!form.email.trim() || !isValidEmail(form.email)) {
      return 'Enter a valid email address.'
    }
    if (!form.role) {
      return 'Role is required.'
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
    setSuccess(false)
    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }
    setError('')
    setSaving(true)
    try {
      await createUser({
        login_id: form.loginId.trim(),
        email: form.email.trim(),
        password: form.password,
        role: toBackendEnum(USER_ROLE_MAP, form.role),
        name: form.name.trim() || undefined,
      })
      setSuccess(true)
      setForm(EMPTY_FORM)
    } catch (err) {
      setError(err.message || 'Could not create this user.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <PageShell
      title="Admin: Create User"
      description="Create a login for an Admin, Accountant, or Contact user."
      actions={<Link to="/dashboard"><Button variant="secondary">Back to dashboard</Button></Link>}
    >
      <form className="form-card" onSubmit={handleSubmit}>
        {success && (
          <div className="form-success-banner">
            User created. They can now sign in with the login ID and password you set.
          </div>
        )}
        {error && <div className="form-error-banner">{error}</div>}

        <FormField label="Name (optional)" htmlFor="admin-new-name">
          <input
            id="admin-new-name"
            type="text"
            value={form.name}
            onChange={(e) => updateField('name', e.target.value)}
            disabled={saving}
          />
        </FormField>

        <FormField label="Login ID" htmlFor="admin-new-login-id">
          <input
            id="admin-new-login-id"
            type="text"
            value={form.loginId}
            onChange={(e) => updateField('loginId', e.target.value)}
            autoComplete="off"
            disabled={saving}
          />
        </FormField>

        <FormField label="Email" htmlFor="admin-new-email">
          <input
            id="admin-new-email"
            type="email"
            value={form.email}
            onChange={(e) => updateField('email', e.target.value)}
            autoComplete="off"
            disabled={saving}
          />
        </FormField>

        <FormField label="Role" htmlFor="admin-new-role">
          <select
            id="admin-new-role"
            value={form.role}
            onChange={(e) => updateField('role', e.target.value)}
            disabled={saving}
          >
            {USER_ROLE_OPTIONS.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </FormField>

        <FormField label="Password" htmlFor="admin-new-password">
          <input
            id="admin-new-password"
            type="password"
            value={form.password}
            onChange={(e) => updateField('password', e.target.value)}
            autoComplete="new-password"
            disabled={saving}
          />
        </FormField>

        <FormField label="Re-enter Password" htmlFor="admin-new-confirm-password">
          <input
            id="admin-new-confirm-password"
            type="password"
            value={form.confirmPassword}
            onChange={(e) => updateField('confirmPassword', e.target.value)}
            autoComplete="new-password"
            disabled={saving}
          />
        </FormField>

        <div className="form-actions">
          <Button type="submit" disabled={saving}>
            {saving ? 'Creating user...' : 'Create User'}
          </Button>
        </div>
      </form>
    </PageShell>
  )
}
