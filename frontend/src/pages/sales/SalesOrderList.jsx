// Route: /sales/orders
// List of Sales Orders with All/Draft/Confirmed filters.
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import Table from '../../components/common/Table.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import Button from '../../components/common/Button.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { listSalesOrders } from '../../services/sales.service.js'
import { formatCurrency, formatDate } from '../../utils/formatters.js'
import { DOC_STATUS_MAP, toDisplayLabel } from '../../utils/enumMap.js'

const FILTERS = ['All', 'Draft', 'Confirmed']

export default function SalesOrderList() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('All')

  const { data, loading, error } = useFetch(listSalesOrders, [])
  const orders = data ?? []

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    return orders.filter((o) => {
      const status = String(o.status ?? 'draft').toLowerCase()
      const matchesFilter = filter === 'All' || status === filter.toLowerCase()
      if (!matchesFilter) return false
      if (!term) return true
      const customerName = o.customer_name ?? o.customer?.name ?? ''
      return [o.reference, customerName].some((field) =>
        String(field ?? '').toLowerCase().includes(term)
      )
    })
  }, [orders, search, filter])

  const columns = [
    {
      key: 'reference',
      label: 'SO #',
      render: (row) => (
        <Link className="link-action" to={`/sales/orders/${row.id}`}>
          {row.reference || `#${row.id}`}
        </Link>
      ),
    },
    {
      key: 'customer',
      label: 'Customer',
      render: (row) => row.customer_name ?? row.customer?.name ?? row.customer_id ?? '—',
    },
    {
      key: 'so_date',
      label: 'SO Date',
      render: (row) => formatDate(row.so_date ?? row.order_date),
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
      title="Sales Orders"
      description="Orders raised with customers, ready to be turned into customer invoices once confirmed."
      actions={(
        <>
          <Link to="/sales/invoices"><Button variant="secondary">View Invoices</Button></Link>
          <Link to="/sales/orders/new"><Button>New Sales Order</Button></Link>
        </>
      )}
    >
      <div className="list-toolbar">
        <input
          className="search-input"
          type="text"
          placeholder="Search by reference or customer..."
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

      {loading && <p className="card-empty">Loading sales orders...</p>}
      {error && !loading && (
        <div className="form-error-banner">Could not load sales orders: {error.message}</div>
      )}
      {!loading && !error && (
        <Table columns={columns} rows={filtered} emptyMessage="No sales orders found." />
      )}
    </PageShell>
  )
}
