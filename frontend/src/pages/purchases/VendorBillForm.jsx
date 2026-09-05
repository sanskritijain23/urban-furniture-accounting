// Route: /purchases/bills/:id
//
// Vendor Bills are only created from a confirmed Purchase Order (see
// PurchaseOrderForm's "Create Vendor Bill" modal) — there is no
// standalone "new bill" form, so this page is a read-only detail +
// Confirm screen, not a create form.
//
// Confirming DOES trigger backend accounting (Purchase Expense Dr /
// Creditors-AP Cr). No client-side accounting math is done here — the
// resulting Journal Entry is simply fetched and displayed if the API
// provides one.
//
// Checkpoint 5: Pay button opens the reusable PaymentModal, which posts
// to the existing payVendorBill endpoint (Creditors/AP Dr, Bank/Cash Cr —
// posted by the backend, not computed here).
import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import Button from '../../components/common/Button.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import PaymentModal from '../../components/forms/PaymentModal.jsx'
import { getVendorBill, confirmVendorBill } from '../../services/purchase.service.js'
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
// inline on the bill itself, or only as an id that needs a follow-up
// GET /journal-entries/{id}. Try each in order and fall back to null
// (in which case the confirm success banner alone is shown).
async function resolveJournalEntry(confirmResponse, bill) {
  if (confirmResponse?.journal_entry) return confirmResponse.journal_entry
  if (bill?.journal_entry) return bill.journal_entry
  const journalEntryId = confirmResponse?.journal_entry_id ?? bill?.journal_entry_id
  if (!journalEntryId) return null
  try {
    return await getJournalEntry(journalEntryId)
  } catch {
    return null
  }
}

export default function VendorBillForm() {
  const { id } = useParams()

  const [bill, setBill] = useState(null)
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
    getVendorBill(id)
      .then((result) => { if (!cancelled) setBill(result) })
      .catch((err) => { if (!cancelled) setLoadError(err.message || 'Could not load this vendor bill.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [id, reloadKey])

  async function handleConfirm() {
    setConfirmError('')
    setConfirming(true)
    try {
      const response = await confirmVendorBill(id)
      const refreshedBill = await getVendorBill(id)
      setBill(refreshedBill)
      const je = await resolveJournalEntry(response, refreshedBill)
      setJournalEntry(je)
    } catch (err) {
      setConfirmError(err.message || 'Could not confirm this vendor bill.')
    } finally {
      setConfirming(false)
    }
  }

  // Re-fetches the bill (and its journal entry, if any) after a payment
  // is recorded, so status/details on this page reflect it immediately —
  // no page reload needed.
  async function handlePaymentSuccess() {
    const refreshedBill = await getVendorBill(id)
    setBill(refreshedBill)
    const je = await resolveJournalEntry(null, refreshedBill)
    if (je) setJournalEntry(je)
  }

  if (loading) {
    return (
      <PageShell title="Vendor Bill">
        <p className="card-empty">Loading vendor bill...</p>
      </PageShell>
    )
  }

  if (loadError) {
    return (
      <PageShell title="Vendor Bill">
        <div className="form-error-banner">{loadError}</div>
      </PageShell>
    )
  }

  const status = String(bill?.status ?? 'draft').toLowerCase()
  const lines = bill?.lines ?? []
  const total = bill?.total_amount ?? lines.reduce((sum, l) => sum + Number(l.amount ?? lineAmount(l)), 0)
  const vendorName = bill?.vendor_name ?? bill?.vendor?.name ?? bill?.vendor_id
  // Backend may expose the outstanding balance as amount_due or
  // balance_due; fall back to the full total if neither is present.
  const amountDue = bill?.amount_due ?? bill?.balance_due ?? total

  return (
    <PageShell
      title={`Vendor Bill ${bill?.bill_no ? `— ${bill.bill_no}` : `#${bill?.id ?? id}`}`}
      actions={<Link to="/purchases/bills"><Button variant="secondary">Back to list</Button></Link>}
    >
      {confirmError && <div className="form-error-banner">{confirmError}</div>}
      {status === 'confirmed' && !confirmError && (
        <div className="form-success-banner">
          Vendor bill confirmed — accounting entry posted.
        </div>
      )}

      <div className="detail-card">
        <div className="detail-grid">
          <div>
            <div className="detail-field-label">Status</div>
            <StatusBadge status={toDisplayLabel(DOC_STATUS_MAP, status)} />
          </div>
          <div>
            <div className="detail-field-label">Vendor</div>
            <div className="detail-field-value">{vendorName ?? '—'}</div>
          </div>
          <div>
            <div className="detail-field-label">Bill Date</div>
            <div className="detail-field-value">{formatDate(bill?.bill_date)}</div>
          </div>
          <div>
            <div className="detail-field-label">Due Date</div>
            <div className="detail-field-value">{bill?.due_date ? formatDate(bill.due_date) : '—'}</div>
          </div>
          <div>
            <div className="detail-field-label">Reference</div>
            <div className="detail-field-value">{bill?.reference || '—'}</div>
          </div>
          {bill?.purchase_order_id && (
            <div>
              <div className="detail-field-label">Purchase Order</div>
              <div className="detail-field-value">
                <Link className="link-action" to={`/purchases/orders/${bill.purchase_order_id}`}>
                  View PO
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
              <tr><td colSpan={4} className="card-empty">No lines on this bill.</td></tr>
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

      {(journalEntry || bill?.journal_entry) && (
        <div className="detail-card">
          <h3 style={{ marginTop: 0 }}>Journal Entry</h3>
          {(() => {
            const je = journalEntry ?? bill.journal_entry
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
        sourceType="vendor_bill"
        sourceId={id}
        amountDue={amountDue}
        onSuccess={handlePaymentSuccess}
      />
    </PageShell>
  )
}
