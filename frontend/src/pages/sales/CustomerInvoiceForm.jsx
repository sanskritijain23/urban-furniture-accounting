// Route: /sales/invoices/:id
// TODO: Invoice No/Reference/Customer/Dates, line items, New/Confirm/Pay
// buttons, Payment modal on Pay click. Confirming DOES create a
// Journal Entry (server-side only — no client accounting math here).

import PageShell from '../../components/common/PageShell.jsx'

export default function CustomerInvoiceForm() {
  return (
    <PageShell
      title="Customer Invoice Form"
      description="This module will be implemented in a later checkpoint."
    />
  )
}
