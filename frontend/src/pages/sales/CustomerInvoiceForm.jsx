// Route: /sales/invoices/:id
//
// Customer Invoices are only created from a confirmed Sales Order (see
// SalesOrderForm's "Create Customer Invoice" modal) — there is no
// standalone "new invoice" form, so this page is a read-only detail +
// Confirm screen, not a create form.
//
// Confirming DOES trigger backend accounting (Debtors/AR Dr / Sales
// Income Cr). No client-side accounting math is done here — the
// resulting Journal Entry is simply fetched and displayed if the API
// provides one.
//
// Checkpoint 5: Pay button opens the reusable PaymentModal, which posts
// to the existing payCustomerInvoice endpoint (Bank/Cash Dr, Debtors/AR
// Cr — posted by the backend, not computed here).
import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import Button from '../../components/common/Button.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import PaymentModal from '../../components/forms/PaymentModal.jsx'
import { getCustomerInvoice, confirmCustomerInvoice } from '../../services/sales.service.js'
import { getJournalEntry } from '../../services/journalEntry.service.js'
import { formatCurrency, formatDate } from '../../utils/formatters.js'
import { DOC_STATUS_MAP, toDisplayLabel } from '../../utils/enumMap.js'

function lineAmount(l) {
  const qty = Number(l.quantity) || 0
  const price = Number(l.unit_price) || 0
  return qty * price
}

// Journal entry info may come back a few different ways depending on
// what the backend actually returns: inline on the confirm response,
// inline on the invoice itself, or only as an id that needs a follow-up
// GET /journal-entries/{id}. Try each in order and fall back to null
// (in which case the confirm success banner alone is shown).
async function resolveJournalEntry(confirmResponse, invoice) {
  if (confirmResponse?.journal_entry) return confirmResponse.journal_entry
  if (invoice?.journal_entry) return invoice.journal_entry
  const journalEntryId = confirmResponse?.journal_entry_id ?? invoice?.journal_entry_id
  if (!journalEntryId) return null
  try {
    return await getJournalEntry(journalEntryId)
  } catch {
    return null
  }
}

export default function CustomerInvoiceForm() {
  const { id } = useParams()

  const [invoice, setInvoice] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')

  const [confirming, setConfirming] = useState(false)
  const [confirmError, setConfirmError] = useState('')
  const [journalEntry, setJournalEntry] = useState(null)
  const [reloadKey, setReloadKey] = useState(0)
  const [paymentModalOpen, setPaymentModalOpen] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    getCustomerInvoice(id)
      .then((result) => { if (!cancelled) setInvoice(result) })
      .catch((err) => { if (!cancelled) setLoadError(err.message || 'Could not load this customer invoice.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [id, reloadKey])

  async function handleConfirm() {
    setConfirmError('')
    setConfirming(true)
    try {
      const response = await confirmCustomerInvoice(id)
      const refreshedInvoice = await getCustomerInvoice(id)
      setInvoice(refreshedInvoice)
      const je = await resolveJournalEntry(response, refreshedInvoice)
      setJournalEntry(je)
    } catch (err) {
      setConfirmError(err.message || 'Could not confirm this customer invoice.')
    } finally {
      setConfirming(false)
    }
  }

  // Re-fetches the invoice (and its journal entry, if any) after a
  // payment is recorded, so status/details on this page reflect it
  // immediately — no page reload needed.
  async function handlePaymentSuccess() {
    const refreshedInvoice = await getCustomerInvoice(id)
    setInvoice(refreshedInvoice)
    const je = await resolveJournalEntry(null, refreshedInvoice)
    if (je) setJournalEntry(je)
  }

  if (loading) {
    return (
      <PageShell title="Customer Invoice">
        <p className="card-empty">Loading customer invoice...</p>
      </PageShell>
    )
  }

  if (loadError) {
    return (
      <PageShell title="Customer Invoice">
        <div className="form-error-banner">{loadError}</div>
      </PageShell>
    )
  }

  const status = String(invoice?.status ?? 'draft').toLowerCase()
  const lines = invoice?.lines ?? []
  const total = invoice?.total_amount ?? lines.reduce((sum, l) => sum + Number(l.amount ?? lineAmount(l)), 0)
  const customerName = invoice?.customer_name ?? invoice?.customer?.name ?? invoice?.customer_id
  // Backend may expose the outstanding balance as amount_due or
  // balance_due; fall back to the full total if neither is present.
  const amountDue = invoice?.amount_due ?? invoice?.balance_due ?? total

  return (
    <PageShell
      title={`Customer Invoice ${invoice?.invoice_no ? `— ${invoice.invoice_no}` : `#${invoice?.id ?? id}`}`}
      actions={<Link to="/sales/invoices"><Button variant="secondary">Back to list</Button></Link>}
    >
      {confirmError && <div className="form-error-banner">{confirmError}</div>}
      {status === 'confirmed' && !confirmError && (
        <div className="form-success-banner">
          Customer invoice confirmed — accounting entry posted.
        </div>
      )}

      <div className="detail-card">
        <div className="detail-grid">
          <div>
            <div className="detail-field-label">Status</div>
            <StatusBadge status={toDisplayLabel(DOC_STATUS_MAP, status)} />
          </div>
          <div>
            <div className="detail-field-label">Customer</div>
            <div className="detail-field-value">{customerName ?? '—'}</div>
          </div>
          <div>
            <div className="detail-field-label">Invoice Date</div>
            <div className="detail-field-value">{formatDate(invoice?.invoice_date)}</div>
          </div>
          <div>
            <div className="detail-field-label">Due Date</div>
            <div className="detail-field-value">{invoice?.due_date ? formatDate(invoice.due_date) : '—'}</div>
          </div>
          <div>
            <div className="detail-field-label">Reference</div>
            <div className="detail-field-value">{invoice?.reference || '—'}</div>
          </div>
          {invoice?.sales_order_id && (
            <div>
              <div className="detail-field-label">Sales Order</div>
              <div className="detail-field-value">
                <Link className="link-action" to={`/sales/orders/${invoice.sales_order_id}`}>
                  View SO
                </Link>
              </div>
            </div>
          )}
        </div>

        <table className="line-items-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Qty</th>
              <th>Unit Price</th>
              <th className="text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {lines.length === 0 && (
              <tr><td colSpan={4} className="card-empty">No lines on this invoice.</td></tr>
            )}
            {lines.map((l, i) => (
              <tr key={l.id ?? i}>
                <td>{l.product_name ?? l.product?.name ?? l.product_id}</td>
                <td>{l.quantity}</td>
                <td>{formatCurrency(l.unit_price)}</td>
                <td className="text-right">{formatCurrency(l.amount ?? lineAmount(l))}</td>
              </tr>
            ))}
            <tr className="line-items-total-row">
              <td colSpan={3}>Total</td>
              <td className="text-right">{formatCurrency(total)}</td>
            </tr>
          </tbody>
        </table>

        <div className="form-actions">
          {status === 'draft' && (
            <Button type="button" onClick={handleConfirm} disabled={confirming}>
              {confirming ? 'Confirming...' : 'Confirm'}
            </Button>
          )}
          {status === 'confirmed' && (
            <Button type="button" onClick={() => setPaymentModalOpen(true)}>
              Pay
            </Button>
          )}
        </div>
      </div>

      {(journalEntry || invoice?.journal_entry) && (
        <div className="detail-card">
          <h3 style={{ marginTop: 0 }}>Journal Entry</h3>
          {(() => {
            const je = journalEntry ?? invoice.journal_entry
            return (
              <>
                <div className="detail-grid">
                  <div>
                    <div className="detail-field-label">Entry #</div>
                    <div className="detail-field-value">{je.entry_number ?? je.id}</div>
                  </div>
                  <div>
                    <div className="detail-field-label">Date</div>
                    <div className="detail-field-value">{formatDate(je.date ?? je.entry_date)}</div>
                  </div>
                </div>
                <table className="line-items-table">
                  <thead>
                    <tr>
                      <th>Account</th>
                      <th className="text-right">Debit</th>
                      <th className="text-right">Credit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(je.lines ?? []).map((jl, i) => (
                      <tr key={jl.id ?? i}>
                        <td>{jl.account_name ?? jl.account?.name ?? jl.account_id}</td>
                        <td className="text-right">{jl.debit ? formatCurrency(jl.debit) : '—'}</td>
                        <td className="text-right">{jl.credit ? formatCurrency(jl.credit) : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </>
            )
          })()}
        </div>
      )}

      <PaymentModal
        open={paymentModalOpen}
        onClose={() => setPaymentModalOpen(false)}
        sourceType="customer_invoice"
        sourceId={id}
        amountDue={amountDue}
        onSuccess={handlePaymentSuccess}
      />
    </PageShell>
  )
}
