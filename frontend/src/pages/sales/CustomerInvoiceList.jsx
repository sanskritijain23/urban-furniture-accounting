// Route: /sales/invoices
// List of Customer Invoices. Invoices are only created from a confirmed
// Sales Order (see SalesOrderForm's "Create Customer Invoice" action),
// so this list has no standalone "Add" button.
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import Table from '../../components/common/Table.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import Button from '../../components/common/Button.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { listCustomerInvoices } from '../../services/sales.service.js'
import { formatCurrency, formatDate } from '../../utils/formatters.js'
import { DOC_STATUS_MAP, toDisplayLabel } from '../../utils/enumMap.js'

const FILTERS = ['All', 'Draft', 'Confirmed', 'Paid']

export default function CustomerInvoiceList() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('All')

  const { data, loading, error } = useFetch(listCustomerInvoices, [])
  const invoices = data ?? []

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    return invoices.filter((inv) => {
      const status = String(inv.status ?? 'draft').toLowerCase()
      const matchesFilter = filter === 'All' || status === filter.toLowerCase()
      if (!matchesFilter) return false
      if (!term) return true
      const customerName = inv.customer_name ?? inv.customer?.name ?? ''
      return [inv.invoice_no, inv.reference, customerName].some((field) =>
        String(field ?? '').toLowerCase().includes(term)
      )
    })
  }, [invoices, search, filter])

  const columns = [
    {
      key: 'invoice_no',
      label: 'Invoice #',
      render: (row) => (
        <Link className="link-action" to={`/sales/invoices/${row.id}`}>
          {row.invoice_no ?? row.reference ?? `#${row.id}`}
        </Link>
      ),
    },
    {
      key: 'customer',
      label: 'Customer',
      render: (row) => row.customer_name ?? row.customer?.name ?? row.customer_id ?? '—',
    },
    {
      key: 'invoice_date',
      label: 'Invoice Date',
      render: (row) => formatDate(row.invoice_date),
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
      title="Customer Invoices"
      description="Invoices created from confirmed sales orders. Confirming an invoice posts the accounting entry (Debtors/AR Dr / Sales Income Cr)."
      actions={<Link to="/sales/orders"><Button variant="secondary">Back to Sales Orders</Button></Link>}
    >
      <div className="list-toolbar">
        <input
          className="search-input"
          type="text"
          placeholder="Search by invoice #, reference or customer..."
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

      {loading && <p className="card-empty">Loading customer invoices...</p>}
      {error && !loading && (
        <div className="form-error-banner">Could not load customer invoices: {error.message}</div>
      )}
      {!loading && !error && (
        <Table columns={columns} rows={filtered} emptyMessage="No customer invoices found." />
      )}
    </PageShell>
  )
}
