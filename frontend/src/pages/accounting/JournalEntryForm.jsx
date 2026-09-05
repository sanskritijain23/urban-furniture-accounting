// Route: /journal-entries/new
// MUST HAVE (manual Journal Entry screen).
// TODO: Accounting Date, Journal (selection), Account/Partner/Debit/Credit
// line grid, Post/Cancel/Back buttons. Post must be BLOCKED client-side
// (in addition to the backend check) if SUM(debit) != SUM(credit).

import PageShell from '../../components/common/PageShell.jsx'

export default function JournalEntryForm() {
  return (
    <PageShell
      title="Manual Journal Entry Form"
      description="This module will be implemented in a later checkpoint."
    />
  )
}
