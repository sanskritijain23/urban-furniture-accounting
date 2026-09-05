// Route: /purchases/bills
// List of Vendor Bills. Bills are only created from a confirmed
// Purchase Order (see PurchaseOrderForm's "Create Vendor Bill" action),
// so this list has no standalone "Add" button.
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import Table from '../../components/common/Table.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import Button from '../../components/common/Button.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { listVendorBills } from '../../services/purchase.service.js'
import { formatCurrency, formatDate } from '../../utils/formatters.js'
import { DOC_STATUS_MAP, toDisplayLabel } from '../../utils/enumMap.js'

const FILTERS = ['All', 'Draft', 'Confirmed', 'Paid']

export default function VendorBillList() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('All')

  const { data, loading, error } = useFetch(listVendorBills, [])
  const bills = data ?? []

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    return bills.filter((b) => {
      const status = String(b.status ?? 'draft').toLowerCase()
      const matchesFilter = filter === 'All' || status === filter.toLowerCase()
      if (!matchesFilter) return false
      if (!term) return true
      const vendorName = b.vendor_name ?? b.vendor?.name ?? ''
      return [b.bill_no, b.reference, vendorName].some((field) =>
        String(field ?? '').toLowerCase().includes(term)
      )
    })
  }, [bills, search, filter])

  const columns = [
    {
      key: 'bill_no',
      label: 'Bill #',
      render: (row) => (
        <Link className="link-action" to={`/purchases/bills/${row.id}`}>
          {row.bill_no ?? row.reference ?? `#${row.id}`}
        </Link>
      ),
    },
    {
      key: 'vendor',
      label: 'Vendor',
      render: (row) => row.vendor_name ?? row.vendor?.name ?? row.vendor_id ?? '—',
    },
    {
      key: 'bill_date',
      label: 'Bill Date',
      render: (row) => formatDate(row.bill_date),
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
      title="Vendor Bills"
      description="Bills created from confirmed purchase orders. Confirming a bill posts the accounting entry (Purchase Expense Dr / Creditors Cr)."
    >
      <div className="list-toolbar">
        <input
          className="search-input"
          type="text"
          placeholder="Search by bill #, reference or vendor..."
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

      {loading && <p className="card-empty">Loading vendor bills...</p>}
      {error && !loading && (
        <div className="form-error-banner">Could not load vendor bills: {error.message}</div>
      )}
      {!loading && !error && (
        <Table columns={columns} rows={filtered} emptyMessage="No vendor bills found." />
      )}
    </PageShell>
  )
}
