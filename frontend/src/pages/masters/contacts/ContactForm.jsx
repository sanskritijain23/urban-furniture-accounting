// Routes: /contacts/new, /contacts/:id
// Fields: Name, Type (Customer/Vendor/Both), Email, Mobile, Address
// (City/State/Pincode). Profile image upload simplified to a URL field.
import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import PageShell from '../../../components/common/PageShell.jsx'
import FormField from '../../../components/forms/FormField.jsx'
import Button from '../../../components/common/Button.jsx'
import { getContact, createContact, updateContact } from '../../../services/contact.service.js'
import { CONTACT_TYPE_MAP, CONTACT_TYPE_OPTIONS, toBackendEnum, toDisplayLabel } from '../../../utils/enumMap.js'

const CONTACT_TYPES = CONTACT_TYPE_OPTIONS

// Internal form state keeps the original UI field names (contact_type,
// city, state, pincode, image_url); these are translated to/from the
// backend's field names (type, address_city, address_state,
// address_pincode, profile_image_url) at the API boundary below.
const EMPTY_FORM = {
  name: '',
  contact_type: 'Customer',
  email: '',
  mobile: '',
  city: '',
  state: '',
  pincode: '',
  image_url: '',
}

// Backend ContactResponse -> UI form shape.
function fromBackend(contact) {
  return {
    name: contact.name ?? '',
    contact_type: toDisplayLabel(CONTACT_TYPE_MAP, contact.type) ?? 'Customer',
    email: contact.email ?? '',
    mobile: contact.mobile ?? '',
    city: contact.address_city ?? '',
    state: contact.address_state ?? '',
    pincode: contact.address_pincode ?? '',
    image_url: contact.profile_image_url ?? '',
  }
}

// UI form shape -> backend ContactCreate/ContactUpdate payload.
function toBackendPayload(form) {
  return {
    name: form.name,
    type: toBackendEnum(CONTACT_TYPE_MAP, form.contact_type),
    email: form.email,
    mobile: form.mobile || null,
    address_city: form.city || null,
    address_state: form.state || null,
    address_pincode: form.pincode || null,
    profile_image_url: form.image_url || null,
  }
}

export default function ContactForm() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()

  const [form, setForm] = useState(EMPTY_FORM)
  const [loading, setLoading] = useState(isEdit)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (!isEdit) return
    let cancelled = false
    setLoading(true)
    getContact(id)
      .then((contact) => {
        if (cancelled) return
        setForm({ ...EMPTY_FORM, ...fromBackend(contact) })
      })
      .catch((err) => { if (!cancelled) setError(err.message || 'Could not load contact.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [id, isEdit])

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function validate() {
    if (!form.name.trim()) return 'Contact name is required.'
    if (!form.contact_type) return 'Contact type is required.'
    // Backend ContactBase.email is a required EmailStr field, so this
    // must be enforced client-side too (previously only validated when
    // present, but never required).
    if (!form.email.trim()) return 'Email is required.'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      return 'Enter a valid email address.'
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
    const payload = toBackendPayload(form)
    try {
      if (isEdit) {
        await updateContact(id, payload)
      } else {
        await createContact(payload)
      }
      setSuccess(true)
      navigate('/contacts')
    } catch (err) {
      setError(err.message || 'Could not save this contact.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <PageShell title={isEdit ? 'Edit Contact' : 'New Contact'}>
        <p className="card-empty">Loading contact...</p>
      </PageShell>
    )
  }

  return (
    <PageShell title={isEdit ? 'Edit Contact' : 'New Contact'}>
      <form className="form-card" onSubmit={handleSubmit}>
        {success && <div className="form-success-banner">Contact saved.</div>}
        {error && <div className="form-error-banner">{error}</div>}

        <FormField label="Name" htmlFor="name">
          <input
            id="name"
            type="text"
            value={form.name}
            onChange={(e) => updateField('name', e.target.value)}
          />
        </FormField>

        <FormField label="Type" htmlFor="contact_type">
          <select
            id="contact_type"
            value={form.contact_type}
            onChange={(e) => updateField('contact_type', e.target.value)}
          >
            {CONTACT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </FormField>

        <FormField label="Email" htmlFor="email">
          <input
            id="email"
            type="email"
            value={form.email}
            onChange={(e) => updateField('email', e.target.value)}
          />
        </FormField>

        <FormField label="Mobile" htmlFor="mobile">
          <input
            id="mobile"
            type="text"
            value={form.mobile}
            onChange={(e) => updateField('mobile', e.target.value)}
          />
        </FormField>

        <div className="form-row">
          <FormField label="City" htmlFor="city">
            <input
              id="city"
              type="text"
              value={form.city}
              onChange={(e) => updateField('city', e.target.value)}
            />
          </FormField>
          <FormField label="State" htmlFor="state">
            <input
              id="state"
              type="text"
              value={form.state}
              onChange={(e) => updateField('state', e.target.value)}
            />
          </FormField>
          <FormField label="Pincode" htmlFor="pincode">
            <input
              id="pincode"
              type="text"
              value={form.pincode}
              onChange={(e) => updateField('pincode', e.target.value)}
            />
          </FormField>
        </div>

        <FormField label="Profile Image URL (optional)" htmlFor="image_url">
          <input
            id="image_url"
            type="text"
            value={form.image_url}
            onChange={(e) => updateField('image_url', e.target.value)}
          />
        </FormField>

        <div className="form-actions">
          <Button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Contact'}
          </Button>
          <Link to="/contacts"><Button type="button" variant="secondary">Cancel</Button></Link>
        </div>
      </form>
    </PageShell>
  )
}
