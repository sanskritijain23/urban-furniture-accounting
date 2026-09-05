// Route: /analytics
// Fields: Analytic Account name, Code/reference, Type (Income/Expenses).
// List/Kanban toggle (Kanban is lower priority than working CRUD, but
// simple enough to include: one column per type).
// No separate /analytics/new route was requested, so create/edit happens
// in a modal on this list page (same pattern as the existing PaymentModal).
//
// NOTE: Backend Checkpoint 1 only implements GET /analytic-accounts/ and
// POST /analytic-accounts/ — there is no PUT or DELETE route yet. The
// Edit and Deactivate actions below will surface a real API error until
// those routes exist; this is left as-is rather than faking success.
import { useMemo, useState } from 'react'
import PageShell from '../../components/common/PageShell.jsx'
import Table from '../../components/common/Table.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import Button from '../../components/common/Button.jsx'
import Modal from '../../components/common/Modal.jsx'
import FormField from '../../components/forms/FormField.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import {
  listAnalyticAccounts,
  createAnalyticAccount,
  updateAnalyticAccount,
  deleteAnalyticAccount,
} from '../../services/analyticAccount.service.js'
import { ANALYTIC_TYPE_MAP, ANALYTIC_TYPE_OPTIONS, toBackendEnum, toDisplayLabel } from '../../utils/enumMap.js'

const ANALYTIC_TYPES = ANALYTIC_TYPE_OPTIONS

// `code` is kept as a local/UI-only field: Backend Checkpoint 1's
// AnalyticAccount has no `code` column, so it is never sent to or read
// from the API.
const EMPTY_FORM = { name: '', code: '', analytic_type: 'Income' }

// Backend AnalyticAccountCreate payload: { name, type } only. Note the
// backend enum value is singular "expense", not "expenses".
function toBackendPayload(form) {
  return {
    name: form.name,
    type: toBackendEnum(ANALYTIC_TYPE_MAP, form.analytic_type),
  }
}

export default function AnalyticAccountList() {
  const [view, setView] = useState('list')
  const [reloadKey, setReloadKey] = useState(0)
  const [actionError, setActionError] = useState('')

  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [formError, setFormError] = useState('')
  const [saving, setSaving] = useState(false)

  const { data, loading, error } = useFetch(listAnalyticAccounts, [reloadKey])
  const accounts = data ?? []

  const byType = useMemo(() => {
    const groups = { Income: [], Expenses: [] }
    accounts.forEach((a) => {
      const type = a.type === 'expense' ? 'Expenses' : 'Income'
      groups[type].push(a)
    })
    return groups
  }, [accounts])

  function openCreate() {
    setEditingId(null)
    setForm(EMPTY_FORM)
    setFormError('')
    setModalOpen(true)
  }

  function openEdit(account) {
    setEditingId(account.id)
    setForm({
      name: account.name ?? '',
      // Not returned by the backend yet; nothing to restore.
      code: '',
      analytic_type: toDisplayLabel(ANALYTIC_TYPE_MAP, account.type) ?? 'Income',
    })
    setFormError('')
    setModalOpen(true)
  }

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  async function handleDelete(account) {
    if (!window.confirm(`Deactivate analytic account "${account.name}"?`)) return
    setActionError('')
    try {
      await deleteAnalyticAccount(account.id)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setActionError(err.message || 'Could not deactivate this analytic account.')
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.name.trim()) return setFormError('Analytic account name is required.')
    setFormError('')
    setSaving(true)
    const payload = toBackendPayload(form)
    try {
      if (editingId) {
        await updateAnalyticAccount(editingId, payload)
      } else {
        await createAnalyticAccount(payload)
      }
      setModalOpen(false)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setFormError(err.message || 'Could not save this analytic account.')
    } finally {
      setSaving(false)
    }
  }

  const columns = [
    { key: 'name', label: 'Name' },
    {
      // Backend Checkpoint 1's AnalyticAccount has no `code` column yet.
      key: 'code',
      label: 'Code',
      render: (row) => row.code ?? '—',
    },
    {
      key: 'type',
      label: 'Type',
      render: (row) => toDisplayLabel(ANALYTIC_TYPE_MAP, row.type),
    },
    {
      // Backend Checkpoint 1's AnalyticAccountResponse has no
      // status/is_active field at all, so there is nothing real to
      // show here yet.
      key: 'status',
      label: 'Status',
      render: () => <StatusBadge status="Backend pending" />,
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (row) => (
        <div className="table-actions">
          <button
            className="link-action"
            onClick={() => openEdit(row)}
            disabled
            title="Backend Checkpoint 1 does not provide a PUT /analytic-accounts/{id} route yet."
          >
            Edit
          </button>
          <button
            className="link-action danger"
            onClick={() => handleDelete(row)}
            disabled
            title="Backend Checkpoint 1 does not provide a DELETE /analytic-accounts/{id} route yet."
          >
            Deactivate
          </button>
        </div>
      ),
    },
  ]

  return (
    <PageShell
      title="Analytic Accounts"
      description="Cost/revenue tags used for budget tracking."
      actions={<Button onClick={openCreate}>Add Analytic Account</Button>}
    >
      <p className="card-empty" style={{ marginBottom: '0.5rem' }}>
        Editing and deactivating analytic accounts is not yet available — Backend
        Checkpoint 1 only implements creating and listing analytic accounts.
      </p>

      <div className="list-toolbar">
        <div className="view-toggle">
          <Button
            variant={view === 'list' ? 'primary' : 'secondary'}
            onClick={() => setView('list')}
          >
            List
          </Button>
          <Button
            variant={view === 'kanban' ? 'primary' : 'secondary'}
            onClick={() => setView('kanban')}
          >
            Kanban
          </Button>
        </div>
      </div>

      {actionError && <div className="form-error-banner">{actionError}</div>}

      {loading && <p className="card-empty">Loading analytic accounts...</p>}
      {error && !loading && (
        <div className="form-error-banner">
          Could not load analytic accounts: {error.message}
        </div>
      )}

      {!loading && !error && view === 'list' && (
        <Table columns={columns} rows={accounts} emptyMessage="No analytic accounts found." />
      )}

      {!loading && !error && view === 'kanban' && (
        <div className="kanban-board">
          {ANALYTIC_TYPES.map((type) => (
            <div className="kanban-column" key={type}>
              <h3>{type}</h3>
              {byType[type].length === 0 && <p className="card-empty">No records</p>}
              {byType[type].map((a) => (
                <div className="kanban-card" key={a.id}>
                  <div className="kanban-card-name">{a.name}</div>
                  {a.code && <div>{a.code}</div>}
                  <div className="table-actions">
                    <button
                      className="link-action"
                      onClick={() => openEdit(a)}
                      disabled
                      title="Backend Checkpoint 1 does not provide a PUT /analytic-accounts/{id} route yet."
                    >
                      Edit
                    </button>
                    <button
                      className="link-action danger"
                      onClick={() => handleDelete(a)}
                      disabled
                      title="Backend Checkpoint 1 does not provide a DELETE /analytic-accounts/{id} route yet."
                    >
                      Deactivate
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <h3>{editingId ? 'Edit Analytic Account' : 'Add Analytic Account'}</h3>
        <form onSubmit={handleSubmit}>
          {formError && <div className="form-error-banner">{formError}</div>}

          <FormField label="Name" htmlFor="analytic-name">
            <input
              id="analytic-name"
              type="text"
              value={form.name}
              onChange={(e) => updateField('name', e.target.value)}
            />
          </FormField>

          <FormField label="Code / Reference (local only — not saved by backend yet)" htmlFor="analytic-code">
            <input
              id="analytic-code"
              type="text"
              value={form.code}
              onChange={(e) => updateField('code', e.target.value)}
            />
          </FormField>

          <FormField label="Type" htmlFor="analytic-type">
            <select
              id="analytic-type"
              value={form.analytic_type}
              onChange={(e) => updateField('analytic_type', e.target.value)}
            >
              {ANALYTIC_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </FormField>

          <div className="form-actions">
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save Analytic Account'}
            </Button>
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </PageShell>
  )
}
