// Routes: /products/new, /products/:id
// Fields: Product Name, Type (Goods/Service/Combo), Category
// (selectable from Chart of Categories API), Sales Price, Cost.
// Inventory/stock management is out of scope for this checkpoint.
import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import PageShell from '../../../components/common/PageShell.jsx'
import FormField from '../../../components/forms/FormField.jsx'
import Button from '../../../components/common/Button.jsx'
import {
  getProduct,
  createProduct,
  updateProduct,
  listCategories,
} from '../../../services/product.service.js'
import { PRODUCT_TYPE_MAP, PRODUCT_TYPE_OPTIONS, toBackendEnum, toDisplayLabel } from '../../../utils/enumMap.js'

const PRODUCT_TYPES = PRODUCT_TYPE_OPTIONS

// `code` is kept as a local/UI-only field: Backend Checkpoint 1's
// Product model has no `code` column, so it is never sent to or read
// from the API. It remains backend-dependent until that column exists.
const EMPTY_FORM = {
  name: '',
  code: '',
  product_type: 'Goods',
  category_id: '',
  sales_price: '',
  purchase_price: '',
}

// Backend ProductResponse -> UI form shape. Preserves any `code` the
// user already typed locally, since the backend never returns one.
function fromBackend(product, previousCode) {
  return {
    name: product.name ?? '',
    code: previousCode ?? '',
    product_type: toDisplayLabel(PRODUCT_TYPE_MAP, product.type) ?? 'Goods',
    category_id: product.category_id ?? '',
    sales_price: product.sales_price ?? '',
    purchase_price: product.cost ?? '',
  }
}

// UI form shape -> backend ProductCreate/ProductUpdate payload.
// `code` is intentionally omitted: it isn't a real backend field yet.
function toBackendPayload(form) {
  return {
    name: form.name,
    type: toBackendEnum(PRODUCT_TYPE_MAP, form.product_type),
    sales_price: form.sales_price === '' ? null : Number(form.sales_price),
    cost: form.purchase_price === '' ? null : Number(form.purchase_price),
    category_id: form.category_id === '' ? null : form.category_id,
  }
}

export default function ProductForm() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()

  const [form, setForm] = useState(EMPTY_FORM)
  const [categories, setCategories] = useState([])
  const [categoriesUnavailable, setCategoriesUnavailable] = useState(false)
  const [loading, setLoading] = useState(isEdit)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    listCategories()
      .then((result) => setCategories(result ?? []))
      .catch(() => setCategoriesUnavailable(true))
  }, [])

  useEffect(() => {
    if (!isEdit) return
    let cancelled = false
    setLoading(true)
    getProduct(id)
      .then((product) => {
        if (cancelled) return
        setForm((prev) => ({ ...EMPTY_FORM, ...fromBackend(product, prev.code) }))
      })
      .catch((err) => { if (!cancelled) setError(err.message || 'Could not load product.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [id, isEdit])

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function validate() {
    if (!form.name.trim()) return 'Product name is required.'
    if (!form.product_type) return 'Product type is required.'
    if (form.sales_price !== '' && Number.isNaN(Number(form.sales_price))) {
      return 'Sales price must be a number.'
    }
    if (form.purchase_price !== '' && Number.isNaN(Number(form.purchase_price))) {
      return 'Purchase price must be a number.'
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
        await updateProduct(id, payload)
      } else {
        await createProduct(payload)
      }
      setSuccess(true)
      navigate('/products')
    } catch (err) {
      setError(err.message || 'Could not save this product.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <PageShell title={isEdit ? 'Edit Product' : 'New Product'}>
        <p className="card-empty">Loading product...</p>
      </PageShell>
    )
  }

  return (
    <PageShell title={isEdit ? 'Edit Product' : 'New Product'}>
      <form className="form-card" onSubmit={handleSubmit}>
        {success && <div className="form-success-banner">Product saved.</div>}
        {error && <div className="form-error-banner">{error}</div>}

        <FormField label="Name" htmlFor="name">
          <input
            id="name"
            type="text"
            value={form.name}
            onChange={(e) => updateField('name', e.target.value)}
          />
        </FormField>

        <FormField label="Code / Reference (local only — not saved by backend yet)" htmlFor="code">
          <input
            id="code"
            type="text"
            value={form.code}
            onChange={(e) => updateField('code', e.target.value)}
          />
        </FormField>

        <FormField label="Type" htmlFor="product_type">
          <select
            id="product_type"
            value={form.product_type}
            onChange={(e) => updateField('product_type', e.target.value)}
          >
            {PRODUCT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </FormField>

        <FormField label="Category" htmlFor="category_id">
          {categoriesUnavailable ? (
            <input
              id="category_id"
              type="text"
              placeholder="Category name (category API not available yet)"
              value={form.category_id}
              onChange={(e) => updateField('category_id', e.target.value)}
            />
          ) : (
            <select
              id="category_id"
              value={form.category_id}
              onChange={(e) => updateField('category_id', e.target.value)}
            >
              <option value="">No category</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          )}
        </FormField>

        <div className="form-row">
          <FormField label="Sales Price" htmlFor="sales_price">
            <input
              id="sales_price"
              type="number"
              step="0.01"
              value={form.sales_price}
              onChange={(e) => updateField('sales_price', e.target.value)}
            />
          </FormField>
          <FormField label="Purchase Price" htmlFor="purchase_price">
            <input
              id="purchase_price"
              type="number"
              step="0.01"
              value={form.purchase_price}
              onChange={(e) => updateField('purchase_price', e.target.value)}
            />
          </FormField>
        </div>

        <div className="form-actions">
          <Button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Product'}
          </Button>
          <Link to="/products"><Button type="button" variant="secondary">Cancel</Button></Link>
        </div>
      </form>
    </PageShell>
  )
}
