// Route: /budgets/:id
// TODO: Budget Name, Period (Start/End), Responsible (from Contacts),
// Analytic Account, Committed Amount. When Confirmed, show read-only
// Achieved Amount / Achieved % / Amount to Achieve (computed server-side).
// Revise creates a NEW linked budget record — never edits committed_amount in place.

import PageShell from '../../components/common/PageShell.jsx'

export default function BudgetForm() {
  return (
    <PageShell
      title="Budget Form"
      description="This module will be implemented in a later checkpoint."
    />
  )
}
