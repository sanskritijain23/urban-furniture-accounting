// Route: /products
// Role allowed: admin, accountant
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../../../components/common/PageShell.jsx'
import Table from '../../../components/common/Table.jsx'
import StatusBadge from '../../../components/common/StatusBadge.jsx'
import Button from '../../../components/common/Button.jsx'
import { useFetch } from '../../../hooks/useFetch.js'
import { listProducts, deleteProduct } from '../../../services/product.service.js'
import { formatCurrency } from '../../../utils/formatters.js'
import { PRODUCT_TYPE_MAP, toDisplayLabel } from '../../../utils/enumMap.js'

export default function ProductList() {
  const [search, setSearch] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const [actionError, setActionError] = useState('')

  const { data, loading, error } = useFetch(listProducts, [reloadKey])
  const products = data ?? []

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return products
    return products.filter((p) =>
      [p.name, p.code].some((field) => String(field ?? '').toLowerCase().includes(term))
    )
  }, [products, search])

  async function handleDelete(product) {
    if (!window.confirm(`Deactivate product "${product.name}"?`)) return
    setActionError('')
    try {
      await deleteProduct(product.id)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setActionError(err.message || 'Could not deactivate this product.')
    }
  }

  const columns = [
    { key: 'name', label: 'Name' },
    {
      // Backend Checkpoint 1's Product has no `code` column, so this is
      // never populated from the API (see ProductForm.jsx notes).
      key: 'code',
      label: 'Code',
      render: (row) => row.code ?? '—',
    },
    {
      key: 'type',
      label: 'Type',
      render: (row) => toDisplayLabel(PRODUCT_TYPE_MAP, row.type),
    },
    {
      key: 'category',
      label: 'Category',
      render: (row) => row.category_name ?? row.category ?? '—',
    },
    {
      key: 'sales_price',
      label: 'Sales Price',
      render: (row) => formatCurrency(row.sales_price),
    },
    {
      key: 'cost',
      label: 'Cost',
      render: (row) => formatCurrency(row.cost),
    },
    {
      // Backend Checkpoint 1's ProductResponse has no status/is_active
      // field at all, so there is nothing real to show here yet.
      key: 'status',
      label: 'Status',
      render: () => <StatusBadge status="Backend pending" />,
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (row) => (
        <div className="table-actions">
          <Link className="link-action" to={`/products/${row.id}`}>Edit</Link>
          <button
            className="link-action danger"
            onClick={() => handleDelete(row)}
            disabled
            title="Backend Checkpoint 1 does not provide a DELETE /products/{id} route yet."
          >
            Deactivate
          </button>
        </div>
      ),
    },
  ]

  return (
    <PageShell
      title="Products"
      description="Goods and services sold or purchased."
      actions={(
        <>
          <Link to="/products/categories"><Button variant="secondary">Manage Categories</Button></Link>
          <Link to="/products/new"><Button>Add Product</Button></Link>
        </>
      )}
    >
      <div className="list-toolbar">
        <input
          className="search-input"
          type="text"
          placeholder="Search by name or code..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {actionError && <div className="form-error-banner">{actionError}</div>}

      {loading && <p className="card-empty">Loading products...</p>}
      {error && !loading && (
        <div className="form-error-banner">
          Could not load products: {error.message}
        </div>
      )}
      {!loading && !error && (
        <Table columns={columns} rows={filtered} emptyMessage="No products found." />
      )}
    </PageShell>
  )
}
