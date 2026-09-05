// Route: /products/categories
//
// Product Categories are a required master-data module on their own,
// but services/product.service.js's createCategory/listCategories were
// never called from any page — ProductForm.jsx only *reads* the list
// for its dropdown, with a free-text fallback if the endpoint errors.
// This page is the missing piece: a simple way to actually create a
// category, so that dropdown has something real to offer.
//
// Backend Checkpoint 1 only exposes GET/POST for categories (no PUT/
// DELETE), so — same convention as Journals/Analytic Accounts — this
// is list + create only; Edit/Deactivate aren't offered since there's
// no route for them yet.
import { useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../../../components/common/PageShell.jsx'
import Table from '../../../components/common/Table.jsx'
import Button from '../../../components/common/Button.jsx'
import Modal from '../../../components/common/Modal.jsx'
import FormField from '../../../components/forms/FormField.jsx'
import { useFetch } from '../../../hooks/useFetch.js'
import { listCategories, createCategory } from '../../../services/product.service.js'

export default function ProductCategoryList() {
  const [reloadKey, setReloadKey] = useState(0)
  const [modalOpen, setModalOpen] = useState(false)
  const [name, setName] = useState('')
  const [formError, setFormError] = useState('')
  const [saving, setSaving] = useState(false)

  const { data, loading, error } = useFetch(listCategories, [reloadKey])
  const categories = data ?? []

  function openCreate() {
    setName('')
    setFormError('')
    setModalOpen(true)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!name.trim()) {
      setFormError('Category name is required.')
      return
    }
    setFormError('')
    setSaving(true)
    try {
      await createCategory({ name: name.trim() })
      setModalOpen(false)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setFormError(err.message || 'Could not create this category.')
    } finally {
      setSaving(false)
    }
  }

  const columns = [
    { key: 'name', label: 'Name' },
  ]

  return (
    <PageShell
      title="Product Categories"
      description="Categories used to group products on the Product master."
      actions={<Button onClick={openCreate}>Add Category</Button>}
    >
      <p className="page-description" style={{ marginTop: 0 }}>
        <Link className="link-action" to="/products">Back to Products</Link>
      </p>

      {loading && <p className="card-empty">Loading categories...</p>}
      {error && !loading && (
        <div className="form-error-banner">Could not load categories: {error.message}</div>
      )}
      {!loading && !error && (
        <Table
          columns={columns}
          rows={categories}
          emptyMessage="No categories yet. Add one so it shows up on the Product form."
        />
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <h3 style={{ marginTop: 0 }}>Add Category</h3>
        <form onSubmit={handleSubmit}>
          {formError && <div className="form-error-banner">{formError}</div>}
          <FormField label="Name" htmlFor="category-name">
            <input
              id="category-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </FormField>
          <div className="form-actions">
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save Category'}
            </Button>
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </PageShell>
  )
}
