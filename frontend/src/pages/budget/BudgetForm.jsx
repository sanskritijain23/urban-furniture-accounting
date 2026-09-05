// Routes: /budgets/new, /budgets/:id
//
// /new renders an editable creation form (Name, Period Start/End,
// Responsible from Contacts, Analytic Account, Amount).
// /:id renders a read-only detail view (no Budget update endpoint
// exists in services/budget.service.js — only create/confirm/revise/
// cancel) with:
//   - Confirm button while status is Draft
//   - Revise button while status is Confirmed, opening a small modal
//     (new Amount + optional note) that calls reviseBudget. Revising
//     never edits committed_amount in place — the backend creates a
//     new linked Budget record and this page navigates to it.
//   - Cancel button while status is Draft or Confirmed
//   - Read-only Achieved Amount / Achieved % / Amount to Achieve,
//     computed server-side (never derived on the frontend)
//   - A non-blocking warning banner when the achieved amount has
//     exceeded the budgeted amount
import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import FormField from '../../components/forms/FormField.jsx'
import Button from '../../components/common/Button.jsx'
import Modal from '../../components/common/Modal.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import {
  getBudget,
  createBudget,
  confirmBudget,
  reviseBudget,
  cancelBudget,
} from '../../services/budget.service.js'
import { listContacts } from '../../services/contact.service.js'
import { listAnalyticAccounts } from '../../services/analyticAccount.service.js'
import { formatCurrency, formatDate, formatPercent } from '../../utils/formatters.js'
import { BUDGET_STATUS_MAP, toDisplayLabel } from '../../utils/enumMap.js'

// ---------- Create mode ----------

function BudgetCreateForm() {
  const navigate = useNavigate()
  const [contacts, setContacts] = useState([])
  const [analyticAccounts, setAnalyticAccounts] = useState([])

  const [name, setName] = useState('')
  const [periodStart, setPeriodStart] = useState(() => new Date().toISOString().slice(0, 10))
  const [periodEnd, setPeriodEnd] = useState('')
  const [responsibleId, setResponsibleId] = useState('')
  const [analyticAccountId, setAnalyticAccountId] = useState('')
  const [amount, setAmount] = useState('')

  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    listContacts().then((result) => setContacts(result ?? [])).catch(() => setContacts([]))
    listAnalyticAccounts()
      .then((result) => setAnalyticAccounts(result ?? []))
      .catch(() => setAnalyticAccounts([]))
  }, [])

  function validate() {
    if (!name.trim()) return 'Budget name is required.'
    if (!periodStart) return 'Period start date is required.'
    if (!periodEnd) return 'Period end date is required.'
    if (periodEnd < periodStart) return 'Period end date must be on or after the start date.'
    if (!analyticAccountId) return 'Analytic account is required.'
    if (amount === '' || Number.isNaN(Number(amount)) || Number(amount) <= 0) {
      return 'Amount must be greater than 0.'
    }
    return ''
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }
    setError('')
    setSaving(true)
    const payload = {
      name: name.trim(),
      period_start: periodStart,
      period_end: periodEnd,
      responsible_id: responsibleId || null,
      analytic_account_id: analyticAccountId,
      committed_amount: Number(amount),
    }
    try {
      const created = await createBudget(payload)
      navigate(created?.id ? `/budgets/${created.id}` : '/budgets')
    } catch (err) {
      setError(err.message || 'Could not create this budget.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <PageShell title="New Budget" description="Draft a budget for an analytic account.">
      <form className="detail-card" onSubmit={handleSubmit} style={{ maxWidth: 640 }}>
        {error && <div className="form-error-banner">{error}</div>}

        <FormField label="Budget Name" htmlFor="budget_name">
          <input
            id="budget_name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </FormField>

        <div className="form-row">
          <FormField label="Period Start" htmlFor="period_start">
            <input
              id="period_start"
              type="date"
              value={periodStart}
              onChange={(e) => setPeriodStart(e.target.value)}
            />
          </FormField>
          <FormField label="Period End" htmlFor="period_end">
            <input
              id="period_end"
              type="date"
              value={periodEnd}
              onChange={(e) => setPeriodEnd(e.target.value)}
            />
          </FormField>
        </div>

        <div className="form-row">
          <FormField label="Responsible (optional)" htmlFor="responsible_id">
            <select
              id="responsible_id"
              value={responsibleId}
              onChange={(e) => setResponsibleId(e.target.value)}
            >
              <option value="">Unassigned</option>
              {contacts.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </FormField>
          <FormField label="Analytic Account" htmlFor="analytic_account_id">
            <select
              id="analytic_account_id"
              value={analyticAccountId}
              onChange={(e) => setAnalyticAccountId(e.target.value)}
            >
              <option value="">Select an analytic account...</option>
              {analyticAccounts.map((a) => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
          </FormField>
        </div>

        <FormField label="Amount" htmlFor="amount">
          <input
            id="amount"
            type="number"
            min="0"
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
        </FormField>

        <div className="form-actions">
          <Button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Budget'}
          </Button>
          <Link to="/budgets"><Button type="button" variant="secondary">Cancel</Button></Link>
        </div>
      </form>
    </PageShell>
  )
}

// ---------- Revise modal ----------

function ReviseBudgetModal({ open, onClose, budgetId, currentAmount, onRevised }) {
  const [amount, setAmount] = useState('')
  const [note, setNote] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (open) {
      setAmount(currentAmount ?? '')
      setNote('')
      setError('')
    }
  }, [open, currentAmount])

  async function handleRevise() {
    if (amount === '' || Number.isNaN(Number(amount)) || Number(amount) <= 0) {
      setError('Amount must be greater than 0.')
      return
    }
    setError('')
    setSaving(true)
    try {
      // The backend creates a brand-new linked Budget record here — the
      // frontend never mutates or duplicates the existing one itself.
      const revised = await reviseBudget(budgetId, {
        committed_amount: Number(amount),
        note: note || null,
      })
      onRevised(revised)
    } catch (err) {
      setError(err.message || 'Could not revise this budget.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose}>
      <h3 style={{ marginTop: 0 }}>Revise Budget</h3>
      <p className="card-empty" style={{ marginTop: 0 }}>
        This creates a new budget with the revised amount; the current budget is kept as-is for history.
      </p>
      {error && <div className="form-error-banner">{error}</div>}
      <FormField label="New Amount" htmlFor="revise_amount">
        <input
          id="revise_amount"
          type="number"
          min="0"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
      </FormField>
      <FormField label="Note (optional)" htmlFor="revise_note">
        <input
          id="revise_note"
          type="text"
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
      </FormField>
      <div className="form-actions">
        <Button type="button" onClick={handleRevise} disabled={saving}>
          {saving ? 'Revising...' : 'Revise'}
        </Button>
        <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
      </div>
    </Modal>
  )
}

// ---------- Detail (view) mode ----------

function BudgetDetail({ id }) {
  const navigate = useNavigate()
  const [budget, setBudget] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionError, setActionError] = useState('')
  const [confirming, setConfirming] = useState(false)
  const [cancelling, setCancelling] = useState(false)
  const [reviseModalOpen, setReviseModalOpen] = useState(false)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    getBudget(id)
      .then((result) => { if (!cancelled) setBudget(result) })
      .catch((err) => { if (!cancelled) setError(err.message || 'Could not load this budget.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [id, reloadKey])

  async function handleConfirm() {
    setActionError('')
    setConfirming(true)
    try {
      await confirmBudget(id)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setActionError(err.message || 'Could not confirm this budget.')
    } finally {
      setConfirming(false)
    }
  }

  async function handleCancel() {
    if (!window.confirm('Cancel this budget?')) return
    setActionError('')
    setCancelling(true)
    try {
      await cancelBudget(id)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setActionError(err.message || 'Could not cancel this budget.')
    } finally {
      setCancelling(false)
    }
  }

  if (loading) {
    return (
      <PageShell title="Budget">
        <p className="card-empty">Loading budget...</p>
      </PageShell>
    )
  }

  if (error) {
    return (
      <PageShell title="Budget">
        <div className="form-error-banner">{error}</div>
      </PageShell>
    )
  }

  const status = String(budget?.status ?? 'draft').toLowerCase()
  const responsibleName = budget?.responsible_name ?? budget?.responsible?.name ?? budget?.responsible_id
  const analyticName = budget?.analytic_account_name ?? budget?.analytic_account?.name ?? budget?.analytic_account_id

  // "Amount" per the required field list — the budgeted/committed
  // amount set at creation (or by the most recent revision).
  const amount = budget?.committed_amount ?? budget?.amount

  // Achieved Amount / Achieved % / Amount to Achieve are always
  // backend-calculated — never derived here from other fields — so
  // they simply render whatever the API returns, or "—" until the
  // backend has a value (e.g. before the budget is confirmed).
  const achievedAmount = budget?.achieved_amount
  const achievedPercentage = budget?.achieved_percentage ?? budget?.achieved_percent
  const amountToAchieve = budget?.amount_to_achieve ?? budget?.remaining_amount

  const isExceeded =
    achievedAmount != null && amount != null && Number(achievedAmount) > Number(amount)

  // Optional linkage to the budget this one was revised into/from, if
  // the backend returns it — shown when present, hidden otherwise.
  const revisedIntoId =
    budget?.revised_budget_id ?? budget?.new_budget_id ?? budget?.next_budget_id ?? null
  const revisedFromId =
    budget?.revised_from_id ?? budget?.previous_budget_id ?? budget?.source_budget_id ?? null

  return (
    <PageShell
      title={`Budget ${budget?.name ? `— ${budget.name}` : `#${budget?.id ?? id}`}`}
      actions={<Link to="/budgets"><Button variant="secondary">Back to list</Button></Link>}
    >
      {actionError && <div className="form-error-banner">{actionError}</div>}
      {isExceeded && (
        <div className="form-warning-banner">
          This budget has been exceeded — achieved amount ({formatCurrency(achievedAmount)}) is
          higher than the budgeted amount ({formatCurrency(amount)}).
        </div>
      )}

      <div className="detail-card">
        <div className="detail-grid">
          <div>
            <div className="detail-field-label">Status</div>
            <StatusBadge status={toDisplayLabel(BUDGET_STATUS_MAP, status)} />
          </div>
          <div>
            <div className="detail-field-label">Period</div>
            <div className="detail-field-value">
              {formatDate(budget?.period_start ?? budget?.start_date)} - {formatDate(budget?.period_end ?? budget?.end_date)}
            </div>
          </div>
          <div>
            <div className="detail-field-label">Analytic Account</div>
            <div className="detail-field-value">{analyticName ?? '—'}</div>
          </div>
          <div>
            <div className="detail-field-label">Responsible</div>
            <div className="detail-field-value">{responsibleName ?? '—'}</div>
          </div>
        </div>

        <div className="detail-grid" style={{ marginTop: '1rem' }}>
          <div>
            <div className="detail-field-label">Amount</div>
            <div className="detail-field-value">{formatCurrency(amount)}</div>
          </div>
          <div>
            <div className="detail-field-label">Achieved Amount</div>
            <div className="detail-field-value">
              {achievedAmount != null ? formatCurrency(achievedAmount) : '—'}
            </div>
          </div>
          <div>
            <div className="detail-field-label">Achieved %</div>
            <div className="detail-field-value">{formatPercent(achievedPercentage)}</div>
          </div>
          <div>
            <div className="detail-field-label">Amount to Achieve</div>
            <div className="detail-field-value">
              {amountToAchieve != null ? formatCurrency(amountToAchieve) : '—'}
            </div>
          </div>
        </div>

        {(revisedFromId || revisedIntoId) && (
          <div className="detail-grid" style={{ marginTop: '1rem' }}>
            {revisedFromId && (
              <div>
                <div className="detail-field-label">Revised From</div>
                <Link className="link-action" to={`/budgets/${revisedFromId}`}>#{revisedFromId}</Link>
              </div>
            )}
            {revisedIntoId && (
              <div>
                <div className="detail-field-label">Revised Into</div>
                <Link className="link-action" to={`/budgets/${revisedIntoId}`}>#{revisedIntoId}</Link>
              </div>
            )}
          </div>
        )}

        <div className="form-actions">
          {status === 'draft' && (
            <Button type="button" onClick={handleConfirm} disabled={confirming}>
              {confirming ? 'Confirming...' : 'Confirm'}
            </Button>
          )}
          {status === 'confirmed' && (
            <Button type="button" onClick={() => setReviseModalOpen(true)}>Revise</Button>
          )}
          {(status === 'draft' || status === 'confirmed') && (
            <Button type="button" variant="secondary" onClick={handleCancel} disabled={cancelling}>
              {cancelling ? 'Cancelling...' : 'Cancel'}
            </Button>
          )}
        </div>
      </div>

      <ReviseBudgetModal
        open={reviseModalOpen}
        budgetId={id}
        currentAmount={amount}
        onClose={() => setReviseModalOpen(false)}
        onRevised={(revised) => {
          setReviseModalOpen(false)
          navigate(revised?.id ? `/budgets/${revised.id}` : '/budgets')
        }}
      />
    </PageShell>
  )
}

export default function BudgetForm() {
  const { id } = useParams()
  if (!id) return <BudgetCreateForm />
  return <BudgetDetail id={id} />
}
