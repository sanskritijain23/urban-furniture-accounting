// Route: /accounts
// Account Type must match the approved enum exactly: Asset, Liability,
// Bank, Cash, Capital, Income, Expenses, Other Expenses.
// No separate /accounts/new route was requested, so create/edit happens
// in a modal on this list page (same pattern as the existing PaymentModal).
import { useMemo, useState } from 'react'
import PageShell from '../../../components/common/PageShell.jsx'
import Table from '../../../components/common/Table.jsx'
import StatusBadge from '../../../components/common/StatusBadge.jsx'
import Button from '../../../components/common/Button.jsx'
import Modal from '../../../components/common/Modal.jsx'
import FormField from '../../../components/forms/FormField.jsx'
import { useFetch } from '../../../hooks/useFetch.js'
import {
  listAccounts,
  createAccount,
  updateAccount,
  deleteAccount,
} from '../../../services/account.service.js'
import { ACCOUNT_TYPE_MAP, ACCOUNT_TYPE_OPTIONS, toBackendEnum, toDisplayLabel } from '../../../utils/enumMap.js'

const ACCOUNT_TYPES = ACCOUNT_TYPE_OPTIONS

// `code` and `parent_account_id` are kept as local/UI-only fields:
// Backend Checkpoint 1's Account model has neither column, so they are
// never sent to or read from the API. They remain backend-dependent
// until those columns exist.
const EMPTY_FORM = { code: '', name: '', account_type: 'Asset', parent_account_id: '' }

// Backend AccountCreate/AccountUpdate payload only supports name + type.
function toBackendPayload(form) {
  return {
    name: form.name,
    type: toBackendEnum(ACCOUNT_TYPE_MAP, form.account_type),
  }
}

export default function AccountList() {
  const [search, setSearch] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const [actionError, setActionError] = useState('')

  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [formError, setFormError] = useState('')
  const [saving, setSaving] = useState(false)

  const { data, loading, error } = useFetch(listAccounts, [reloadKey])
  const accounts = data ?? []

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return accounts
    return accounts.filter((a) =>
      [a.name, a.code].some((field) => String(field ?? '').toLowerCase().includes(term))
    )
  }, [accounts, search])

  function accountName(accountId) {
    const match = accounts.find((a) => String(a.id) === String(accountId))
    return match ? match.name : '—'
  }

  function openCreate() {
    setEditingId(null)
    setForm(EMPTY_FORM)
    setFormError('')
    setModalOpen(true)
  }

  function openEdit(account) {
    setEditingId(account.id)
    setForm({
      // code/parent_account_id are never returned by the backend yet
      // (see notes above), so there is nothing to restore here.
      code: '',
      name: account.name ?? '',
      account_type: toDisplayLabel(ACCOUNT_TYPE_MAP, account.type) ?? 'Asset',
      parent_account_id: '',
    })
    setFormError('')
    setModalOpen(true)
  }

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  async function handleDelete(account) {
    if (!window.confirm(`Deactivate account "${account.name}"?`)) return
    setActionError('')
    try {
      await deleteAccount(account.id)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setActionError(err.message || 'Could not deactivate this account.')
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.name.trim()) return setFormError('Account name is required.')
    setFormError('')
    setSaving(true)
    const payload = toBackendPayload(form)
    try {
      if (editingId) {
        await updateAccount(editingId, payload)
      } else {
        await createAccount(payload)
      }
      setModalOpen(false)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setFormError(err.message || 'Could not save this account.')
    } finally {
      setSaving(false)
    }
  }

  const columns = [
    {
      // Backend Checkpoint 1's Account has no `code` column yet.
      key: 'code',
      label: 'Code',
      render: (row) => row.code ?? '—',
    },
    { key: 'name', label: 'Name' },
    {
      key: 'type',
      label: 'Type',
      render: (row) => toDisplayLabel(ACCOUNT_TYPE_MAP, row.type),
    },
    {
      // Backend Checkpoint 1's Account has no `parent_account_id`
      // column yet.
      key: 'parent_account_id',
      label: 'Parent Account',
      render: (row) => (row.parent_account_id ? accountName(row.parent_account_id) : '—'),
    },
    {
      // Real backend status: draft / confirmed / archived (not a
      // boolean is_active flag).
      key: 'status',
      label: 'Status',
      render: (row) => <StatusBadge status={row.status ?? 'Backend pending'} />,
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (row) => (
        <div className="table-actions">
          <button className="link-action" onClick={() => openEdit(row)}>Edit</button>
          <button
            className="link-action danger"
            onClick={() => handleDelete(row)}
            disabled
            title="Backend Checkpoint 1 does not provide a DELETE /accounts/{id} route yet."
          >
            Deactivate
          </button>
        </div>
      ),
    },
  ]

  return (
    <PageShell
      title="Chart of Accounts"
      description="Ledger accounts used across journals and transactions."
      actions={<Button onClick={openCreate}>Add Account</Button>}
    >
      <div className="list-toolbar">
        <input
          className="search-input"
          type="text"
          placeholder="Search by name or code..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {actionError && <div className="form-error-banner">{actionError}</div>}

      {loading && <p className="card-empty">Loading accounts...</p>}
      {error && !loading && (
        <div className="form-error-banner">
          Could not load accounts: {error.message}
        </div>
      )}
      {!loading && !error && (
        <Table columns={columns} rows={filtered} emptyMessage="No accounts found." />
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <h3>{editingId ? 'Edit Account' : 'Add Account'}</h3>
        <form onSubmit={handleSubmit}>
          {formError && <div className="form-error-banner">{formError}</div>}

          <FormField label="Code (local only — not saved by backend yet)" htmlFor="acc-code">
            <input
              id="acc-code"
              type="text"
              value={form.code}
              onChange={(e) => updateField('code', e.target.value)}
            />
          </FormField>

          <FormField label="Name" htmlFor="acc-name">
            <input
              id="acc-name"
              type="text"
              value={form.name}
              onChange={(e) => updateField('name', e.target.value)}
            />
          </FormField>

          <FormField label="Type" htmlFor="acc-type">
            <select
              id="acc-type"
              value={form.account_type}
              onChange={(e) => updateField('account_type', e.target.value)}
            >
              {ACCOUNT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </FormField>

          <FormField label="Parent Account (local only — not saved by backend yet)" htmlFor="acc-parent">
            <select
              id="acc-parent"
              value={form.parent_account_id}
              onChange={(e) => updateField('parent_account_id', e.target.value)}
            >
              <option value="">No parent</option>
              {accounts.filter((a) => a.id !== editingId).map((a) => (
                <option key={a.id} value={a.id}>{a.code} — {a.name}</option>
              ))}
            </select>
          </FormField>

          <div className="form-actions">
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save Account'}
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
