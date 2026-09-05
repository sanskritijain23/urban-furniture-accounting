// Reusable Payment component (MUST HAVE — not a standalone route).
// Used from both VendorBillForm and CustomerInvoiceForm "Pay" buttons.
//
// No client-side accounting math is done here — the backend decides
// and posts the actual journal entry:
//   Vendor Bill payment:    Creditors/AP  Dr   Bank/Cash  Cr
//   Customer Invoice payment: Bank/Cash   Dr   Debtors/AR Cr
// This component only collects the inputs and calls the existing
// services/payment.service.js-adjacent endpoints already exposed on
// purchase.service.js / sales.service.js (payVendorBill / payCustomerInvoice).
//
// Field names sent to the backend (amount / payment_date / journal_id /
// note) follow this codebase's snake_case REST convention, matching the
// other *Create payloads in services/*.js. Confirm with backend if the
// actual PaymentCreate schema differs — same caveat other forms in this
// codebase already carry for unconfirmed payload shapes.
import { useEffect, useState } from 'react'
import Modal from '../common/Modal.jsx'
import Button from '../common/Button.jsx'
import FormField from './FormField.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { listJournals } from '../../services/journal.service.js'
import { payVendorBill } from '../../services/purchase.service.js'
import { payCustomerInvoice } from '../../services/sales.service.js'
import { formatCurrency } from '../../utils/formatters.js'

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10)
}

// Maps the two places this modal is launched from to the right pay
// endpoint and the (display-only) accounting direction shown to the user.
const SOURCE_CONFIG = {
  vendor_bill: {
    label: 'Vendor Bill',
    direction: 'Send',
    directionHint: 'Debits Creditors/AP and credits the Bank/Cash account below.',
    payFn: payVendorBill,
  },
  customer_invoice: {
    label: 'Customer Invoice',
    direction: 'Receive',
    directionHint: 'Debits the Bank/Cash account below and credits Debtors/AR.',
    payFn: payCustomerInvoice,
  },
}

export default function PaymentModal({ open, onClose, sourceType, sourceId, amountDue, onSuccess }) {
  const config = SOURCE_CONFIG[sourceType] ?? SOURCE_CONFIG.vendor_bill

  const [amount, setAmount] = useState('')
  const [paymentDate, setPaymentDate] = useState(todayIsoDate())
  const [journalId, setJournalId] = useState('')
  const [note, setNote] = useState('')
  const [formError, setFormError] = useState('')
  const [success, setSuccess] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Bank/Cash journals only — a bill/invoice payment always moves money
  // through one of those, never a Sales/Purchase journal. Failing to load
  // journals shouldn't crash the modal; the select just stays empty and
  // required-selection validation below is skipped in that case.
  const { data: journalsData, error: journalsError } = useFetch(listJournals, [open])
  const journals = (journalsData ?? []).filter((j) => j.type === 'bank' || j.type === 'cash')

  useEffect(() => {
    if (open) {
      setAmount(amountDue != null ? String(amountDue) : '')
      setPaymentDate(todayIsoDate())
      setJournalId('')
      setNote('')
      setFormError('')
      setSuccess('')
      setSubmitting(false)
    }
  }, [open, amountDue])

  if (!open) return null

  async function handleSubmit(e) {
    e.preventDefault()
    setFormError('')

    const numericAmount = Number(amount)
    if (!amount || Number.isNaN(numericAmount) || numericAmount <= 0) {
      setFormError('Enter a valid payment amount.')
      return
    }
    if (!paymentDate) {
      setFormError('Payment date is required.')
      return
    }
    if (journals.length > 0 && !journalId) {
      setFormError('Select the Bank/Cash journal for this payment.')
      return
    }

    setSubmitting(true)
    try {
      const payload = {
        amount: numericAmount,
        payment_date: paymentDate,
        ...(journalId ? { journal_id: journalId } : {}),
        ...(note.trim() ? { note: note.trim() } : {}),
      }
      const response = await config.payFn(sourceId, payload)
      setSuccess('Payment recorded successfully.')
      // Let the parent page re-fetch the bill/invoice (and any journal
      // entry) so status/details reflect the payment immediately.
      if (onSuccess) await onSuccess(response)
    } catch (err) {
      setFormError(err.message || 'Could not record this payment.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal open={open} onClose={submitting ? () => {} : onClose}>
      <h3 style={{ marginTop: 0 }}>Pay {config.label}</h3>
      <p className="page-description">{config.directionHint}</p>

      {formError && <div className="form-error-banner">{formError}</div>}
      {success && <div className="form-success-banner">{success}</div>}
      {journalsError && !success && (
        <div className="form-error-banner">
          Could not load Bank/Cash journals: {journalsError.message}
        </div>
      )}

      {!success && (
        <form onSubmit={handleSubmit}>
          <FormField label="Payment Type" htmlFor="pay-direction">
            <input id="pay-direction" type="text" value={config.direction} disabled readOnly />
          </FormField>

          <FormField label="Amount" htmlFor="pay-amount">
            <input
              id="pay-amount"
              type="number"
              min="0"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              disabled={submitting}
            />
          </FormField>
          {amountDue != null && (
            <p className="card-empty" style={{ marginTop: '-0.5rem' }}>
              Amount due: {formatCurrency(amountDue)}
            </p>
          )}

          <FormField label="Payment Date" htmlFor="pay-date">
            <input
              id="pay-date"
              type="date"
              value={paymentDate}
              onChange={(e) => setPaymentDate(e.target.value)}
              disabled={submitting}
            />
          </FormField>

          <FormField label="Bank/Cash Journal" htmlFor="pay-journal">
            <select
              id="pay-journal"
              value={journalId}
              onChange={(e) => setJournalId(e.target.value)}
              disabled={submitting}
            >
              <option value="">Select journal...</option>
              {journals.map((j) => (
                <option key={j.id} value={j.id}>{j.name}</option>
              ))}
            </select>
          </FormField>

          <FormField label="Note (optional)" htmlFor="pay-note">
            <input
              id="pay-note"
              type="text"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              disabled={submitting}
            />
          </FormField>

          <div className="form-actions">
            <Button type="submit" disabled={submitting}>
              {submitting ? 'Processing...' : 'Submit Payment'}
            </Button>
            <Button type="button" variant="secondary" onClick={onClose} disabled={submitting}>
              Cancel
            </Button>
          </div>
        </form>
      )}

      {success && (
        <div className="form-actions">
          <Button type="button" onClick={onClose}>Close</Button>
        </div>
      )}
    </Modal>
  )
}
