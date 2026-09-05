// Route: /purchases/orders
// List of Purchase Orders with All/Draft/Confirmed filters.
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import Table from '../../components/common/Table.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import Button from '../../components/common/Button.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { listPurchaseOrders } from '../../services/purchase.service.js'
import { formatCurrency, formatDate } from '../../utils/formatters.js'
import { DOC_STATUS_MAP, toDisplayLabel } from '../../utils/enumMap.js'

const FILTERS = ['All', 'Draft', 'Confirmed']

export default function PurchaseOrderList() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('All')

  const { data, loading, error } = useFetch(listPurchaseOrders, [])
  const orders = data ?? []

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    return orders.filter((o) => {
      const status = String(o.status ?? 'draft').toLowerCase()
      const matchesFilter = filter === 'All' || status === filter.toLowerCase()
      if (!matchesFilter) return false
      if (!term) return true
      const vendorName = o.vendor_name ?? o.vendor?.name ?? ''
      return [o.reference, vendorName].some((field) =>
        String(field ?? '').toLowerCase().includes(term)
      )
    })
  }, [orders, search, filter])

  const columns = [
    {
      key: 'reference',
      label: 'PO #',
      render: (row) => (
        <Link className="link-action" to={`/purchases/orders/${row.id}`}>
          {row.reference || `#${row.id}`}
        </Link>
      ),
    },
    {
      key: 'vendor',
      label: 'Vendor',
      render: (row) => row.vendor_name ?? row.vendor?.name ?? row.vendor_id ?? '—',
    },
    {
      key: 'po_date',
      label: 'PO Date',
      render: (row) => formatDate(row.po_date ?? row.order_date),
    },
    {
      key: 'total_amount',
      label: 'Total',
      render: (row) => formatCurrency(row.total_amount),
    },
    {
      key: 'status',
      label: 'Status',
      render: (row) => <StatusBadge status={toDisplayLabel(DOC_STATUS_MAP, String(row.status ?? 'draft').toLowerCase())} />,
    },
  ]

  return (
    <PageShell
      title="Purchase Orders"
      description="Orders raised with vendors, ready to be turned into vendor bills once confirmed."
      actions={<Link to="/purchases/orders/new"><Button>New Purchase Order</Button></Link>}
    >
      <div className="list-toolbar">
        <input
          className="search-input"
          type="text"
          placeholder="Search by reference or vendor..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="view-toggle">
          {FILTERS.map((f) => (
            <Button
              key={f}
              type="button"
              variant={filter === f ? 'primary' : 'secondary'}
              onClick={() => setFilter(f)}
            >
              {f}
            </Button>
          ))}
        </div>
      </div>

      {loading && <p className="card-empty">Loading purchase orders...</p>}
      {error && !loading && (
        <div className="form-error-banner">Could not load purchase orders: {error.message}</div>
      )}
      {!loading && !error && (
        <Table columns={columns} rows={filtered} emptyMessage="No purchase orders found." />
      )}
    </PageShell>
  )
}
