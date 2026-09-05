// Route: /portal
// Role allowed: contact ONLY.
// TODO: read-only list of the logged-in contact's own Invoices/Bills,
// plus a Pay action per document. Must NOT expose create/edit for any
// master data or other business records.

import PageShell from '../../components/common/PageShell.jsx'

export default function ContactPortal() {
  return (
    <PageShell
      title="Contact Portal"
      description="This module will be implemented in a later checkpoint."
    />
  )
}
