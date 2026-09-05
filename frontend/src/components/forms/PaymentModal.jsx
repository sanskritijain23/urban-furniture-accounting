// Reusable Payment component (MUST HAVE — not a standalone route).
// Used from both VendorBillForm and CustomerInvoiceForm "Pay" buttons.
// Fields: Payment Type (Send/Receive), Payment Via (Cash/Bank), Amount
// (defaults to Amount Due, editable), Note.
// TODO: wire to services/payment.service.js
export default function PaymentModal({ open, onClose, sourceType, sourceId, amountDue }) {
  return (
    <div>
      {/* TODO: form fields as documented above */}
      Payment Modal — TODO ({sourceType} #{sourceId}, due {amountDue})
    </div>
  )
}
