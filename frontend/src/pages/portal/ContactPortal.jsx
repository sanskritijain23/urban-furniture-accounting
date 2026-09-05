// Route: /portal
// Role allowed: contact ONLY (enforced by routes/ContactRoute.jsx).
//
// Read-only list of the logged-in contact's own Customer Invoices and
// Vendor Bills, plus a Pay action on each unpaid document. No
// create/edit affordance for any master data or other business record
// is exposed here — that's the whole point of this screen vs. the
// admin-side Sales/Purchases pages.
//
// listCustomerInvoices()/listVendorBills() are the exact same service
// calls the admin-side CustomerInvoiceList/VendorBillList pages use
// (see services/sales.service.js, services/purchase.service.js). Per
// the product spec ("Contact users ... only view their own
// invoice/bills"), the backend is assumed to scope these lists to the
// logged-in contact based on the JWT when the caller's role is
// "contact" — this page does no client-side filtering by contact, and
// must not, since it has no reliable way to know which rows are "its
// own" otherwise. If the backend does NOT scope these endpoints for
// the contact role, that's a backend fix, not a frontend one.
import { useCallback, useMemo, useState } from 'react'
import PageShell from '../../components/common/PageShell.jsx'
import Table from '../../components/common/Table.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import Button from '../../components/common/Button.jsx'
import PaymentModal from '../../components/forms/PaymentModal.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { listCustomerInvoices } from '../../services/sales.service.js'
import { listVendorBills } from '../../services/purchase.service.js'
import { formatCurrency, formatDate } from '../../utils/formatters.js'
import { DOC_STATUS_MAP, toDisplayLabel } from '../../utils/enumMap.js'

const TABS = [
  { key: 'invoices', label: 'My Invoices' },
  { key: 'bills', label: 'My Bills' },
]

// A document can only be paid once it's been confirmed (draft has no
// posted accounting entry yet) and isn't already fully paid.
function isPayable(row) {
  const status = String(row.status ?? 'draft').toLowerCase()
  if (status !== 'confirmed') return false
  const due = row.amount_due ?? row.balance_due ?? row.total_amount ?? 0
  return Number(due) > 0
}

export default function ContactPortal() {
  const [activeTab, setActiveTab] = useState('invoices')

  const [invoicesReloadKey, setInvoicesReloadKey] = useState(0)
  const [billsReloadKey, setBillsReloadKey] = useState(0)

  const invoicesFetch = useCallback(() => listCustomerInvoices(), [])
  const billsFetch = useCallback(() => listVendorBills(), [])

  const {
    data: invoicesData,
    loading: invoicesLoading,
    error: invoicesError,
  } = useFetch(invoicesFetch, [invoicesReloadKey])
  const {
    data: billsData,
    loading: billsLoading,
    error: billsError,
  } = useFetch(billsFetch, [billsReloadKey])

  const invoices = invoicesData ?? []
  const bills = billsData ?? []

  // { sourceType: 'customer_invoice' | 'vendor_bill', id, amountDue }
  const [payTarget, setPayTarget] = useState(null)

  function openPayment(sourceType, row) {
    const amountDue = row.amount_due ?? row.balance_due ?? row.total_amount ?? 0
    setPayTarget({ sourceType, id: row.id, amountDue })
  }

  async function handlePaymentSuccess() {
    if (payTarget?.sourceType === 'customer_invoice') {
      setInvoicesReloadKey((k) => k + 1)
    } else if (payTarget?.sourceType === 'vendor_bill') {
      setBillsReloadKey((k) => k + 1)
    }
  }

  const invoiceColumns = useMemo(() => [
    {
      key: 'invoice_no',
      label: 'Invoice #',
      render: (row) => row.invoice_no ?? row.reference ?? `#${row.id}`,
    },
    {
      key: 'invoice_date',
      label: 'Invoice Date',
      render: (row) => formatDate(row.invoice_date),
    },
    {
      key: 'due_date',
      label: 'Due Date',
      render: (row) => (row.due_date ? formatDate(row.due_date) : '—'),
    },
    {
      key: 'total_amount',
      label: 'Total',
      render: (row) => formatCurrency(row.total_amount),
    },
    {
      key: 'amount_due',
      label: 'Amount Due',
      render: (row) => formatCurrency(row.amount_due ?? row.balance_due ?? row.total_amount),
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
        isPayable(row) ? (
          <Button type="button" onClick={() => openPayment('customer_invoice', row)}>
            Pay
          </Button>
        ) : null,
    },
  ], [])

  const billColumns = useMemo(() => [
    {
      key: 'bill_no',
      label: 'Bill #',
      render: (row) => row.bill_no ?? row.reference ?? `#${row.id}`,
    },
    {
      key: 'bill_date',
      label: 'Bill Date',
      render: (row) => formatDate(row.bill_date),
    },
    {
      key: 'due_date',
      label: 'Due Date',
      render: (row) => (row.due_date ? formatDate(row.due_date) : '—'),
    },
    {
      key: 'total_amount',
      label: 'Total',
      render: (row) => formatCurrency(row.total_amount),
    },
    {
      key: 'amount_due',
      label: 'Amount Due',
      render: (row) => formatCurrency(row.amount_due ?? row.balance_due ?? row.total_amount),
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
        isPayable(row) ? (
          <Button type="button" onClick={() => openPayment('vendor_bill', row)}>
            Pay
          </Button>
        ) : null,
    },
  ], [])

  const showingInvoices = activeTab === 'invoices'
  const loading = showingInvoices ? invoicesLoading : billsLoading
  const error = showingInvoices ? invoicesError : billsError
  const rows = showingInvoices ? invoices : bills
  const columns = showingInvoices ? invoiceColumns : billColumns

  return (
    <PageShell
      title="My Invoices & Bills"
      description="View your invoices and bills and make a payment. You don't have access to any other part of this system."
    >
      <div className="list-toolbar">
        <div className="view-toggle">
          {TABS.map((tab) => (
            <Button
              key={tab.key}
              type="button"
              variant={activeTab === tab.key ? 'primary' : 'secondary'}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </Button>
          ))}
        </div>
      </div>

      {loading && (
        <p className="card-empty">
          Loading {showingInvoices ? 'your invoices' : 'your bills'}...
        </p>
      )}
      {error && !loading && (
        <div className="form-error-banner">
          Could not load {showingInvoices ? 'your invoices' : 'your bills'}: {error.message}
        </div>
      )}
      {!loading && !error && (
        <Table
          columns={columns}
          rows={rows}
          emptyMessage={
            showingInvoices
              ? "You don't have any invoices yet."
              : "You don't have any bills yet."
          }
        />
      )}

      <PaymentModal
        open={Boolean(payTarget)}
        onClose={() => setPayTarget(null)}
        sourceType={payTarget?.sourceType}
        sourceId={payTarget?.id}
        amountDue={payTarget?.amountDue}
        onSuccess={handlePaymentSuccess}
      />
    </PageShell>
  )
}
