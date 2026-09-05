// Route: /payments
//
// Payments themselves have no standalone "create" flow — they're
// recorded from the reusable PaymentModal (see components/forms/
// PaymentModal.jsx), launched from a confirmed Vendor Bill's or
// Customer Invoice's "Pay" button. This page is the missing piece: a
// place to see every payment that's been recorded, across both
// directions, in one list — services/payment.service.js already
// exposed listPayments/confirmPayment but no page ever called them.
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import Table from '../../components/common/Table.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import Button from '../../components/common/Button.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { listPayments, confirmPayment } from '../../services/payment.service.js'
import { formatCurrency, formatDate } from '../../utils/formatters.js'
import { DOC_STATUS_MAP, toDisplayLabel } from '../../utils/enumMap.js'

const FILTERS = ['All', 'Draft', 'Confirmed']

// Backend response shape for which side a payment moved money on isn't
// confirmed — check the couple of field names that would make sense
// (an explicit direction, or the source document type) before falling
// back to a generic label.
function paymentDirection(row) {
  const explicit = row.direction ?? row.payment_type
  if (explicit) return String(explicit).toLowerCase()
  const sourceType = row.source_type ?? row.document_type
  if (sourceType === 'vendor_bill') return 'send'
  if (sourceType === 'customer_invoice') return 'receive'
  return null
}

function sourceLink(row) {
  const sourceType = row.source_type ?? row.document_type
  const sourceId = row.source_id ?? row.document_id ?? row.vendor_bill_id ?? row.customer_invoice_id
  if (!sourceId) return null
  if (sourceType === 'vendor_bill' || row.vendor_bill_id) {
    return { to: `/purchases/bills/${sourceId}`, label: 'View Bill' }
  }
  if (sourceType === 'customer_invoice' || row.customer_invoice_id) {
    return { to: `/sales/invoices/${sourceId}`, label: 'View Invoice' }
  }
  return null
}

export default function PaymentList() {
  const [filter, setFilter] = useState('All')
  const [reloadKey, setReloadKey] = useState(0)
  const [actionError, setActionError] = useState('')
  const [confirmingId, setConfirmingId] = useState(null)

  const { data, loading, error } = useFetch(listPayments, [reloadKey])
  const payments = data ?? []

  const filtered = useMemo(() => {
    return payments.filter((p) => {
      const status = String(p.status ?? 'draft').toLowerCase()
      return filter === 'All' || status === filter.toLowerCase()
    })
  }, [payments, filter])

  async function handleConfirm(payment) {
    setActionError('')
    setConfirmingId(payment.id)
    try {
      await confirmPayment(payment.id)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setActionError(err.message || 'Could not confirm this payment.')
    } finally {
      setConfirmingId(null)
    }
  }

  const columns = [
    {
      key: 'date',
      label: 'Date',
      render: (row) => formatDate(row.payment_date ?? row.date),
    },
    {
      key: 'reference',
      label: 'Reference',
      render: (row) => row.reference ?? row.payment_number ?? `#${row.id}`,
    },
    {
      key: 'partner',
      label: 'Partner',
      render: (row) => row.partner_name ?? row.partner?.name ?? row.partner_id ?? '—',
    },
    {
      key: 'direction',
      label: 'Type',
      render: (row) => {
        const direction = paymentDirection(row)
        if (direction === 'send') return 'Sent (to vendor)'
        if (direction === 'receive') return 'Received (from customer)'
        return '—'
      },
    },
    {
      key: 'source',
      label: 'Document',
      render: (row) => {
        const link = sourceLink(row)
        return link ? <Link className="link-action" to={link.to}>{link.label}</Link> : '—'
      },
    },
    {
      key: 'amount',
      label: 'Amount',
      render: (row) => formatCurrency(row.amount),
    },
    {
      key: 'status',
      label: 'Status',
      render: (row) => (
        <StatusBadge status={toDisplayLabel(DOC_STATUS_MAP, String(row.status ?? 'draft').toLowerCase())} />
      ),
    },
    {
      key: 'actions',
      label: '',
      render: (row) =>
        String(row.status ?? '').toLowerCase() === 'draft' ? (
          <Button
            type="button"
            onClick={() => handleConfirm(row)}
            disabled={confirmingId === row.id}
          >
            {confirmingId === row.id ? 'Confirming...' : 'Confirm'}
          </Button>
        ) : null,
    },
  ]

  return (
    <PageShell
      title="Payments"
      description="Every payment recorded against a vendor bill or customer invoice. Payments are recorded from the Pay button on a confirmed bill or invoice, not created here directly."
    >
      <div className="list-toolbar">
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

      {actionError && <div className="form-error-banner">{actionError}</div>}

      {loading && <p className="card-empty">Loading payments...</p>}
      {error && !loading && (
        <div className="form-error-banner">Could not load payments: {error.message}</div>
      )}
      {!loading && !error && (
        <Table
          columns={columns}
          rows={filtered}
          emptyMessage="No payments recorded yet. Pay a confirmed vendor bill or customer invoice to see it here."
        />
      )}
    </PageShell>
  )
}
