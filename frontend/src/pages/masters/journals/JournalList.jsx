// Route: /journals
// Journal Type must be one of: Sales, Purchase, Bank, Cash.
// Default Account is selected from Chart of Accounts (many-to-one).
// No separate /journals/new route was requested, so create/edit happens
// in a modal on this list page (same pattern as the existing PaymentModal).
//
// NOTE: Backend Checkpoint 1 only implements GET /journals/ and
// POST /journals/ — there is no PUT or DELETE route yet. The Edit and
// Deactivate actions below will surface a real API error until those
// routes exist; this is left as-is rather than faking success.
import { useState } from 'react'
import PageShell from '../../../components/common/PageShell.jsx'
import Table from '../../../components/common/Table.jsx'
import StatusBadge from '../../../components/common/StatusBadge.jsx'
import Button from '../../../components/common/Button.jsx'
import Modal from '../../../components/common/Modal.jsx'
import FormField from '../../../components/forms/FormField.jsx'
import { useFetch } from '../../../hooks/useFetch.js'
import {
  listJournals,
  createJournal,
  updateJournal,
  deleteJournal,
} from '../../../services/journal.service.js'
import { listAccounts } from '../../../services/account.service.js'
import { JOURNAL_TYPE_MAP, JOURNAL_TYPE_OPTIONS, toBackendEnum, toDisplayLabel } from '../../../utils/enumMap.js'

const JOURNAL_TYPES = JOURNAL_TYPE_OPTIONS

const EMPTY_FORM = { name: '', journal_type: 'Sales', default_account_id: '' }

// Backend JournalCreate payload uses `type`, not `journal_type`.
function toBackendPayload(form) {
  return {
    name: form.name,
    type: toBackendEnum(JOURNAL_TYPE_MAP, form.journal_type),
    default_account_id: form.default_account_id,
  }
}

export default function JournalList() {
  const [reloadKey, setReloadKey] = useState(0)
  const [actionError, setActionError] = useState('')

  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [formError, setFormError] = useState('')
  const [saving, setSaving] = useState(false)

  const { data, loading, error } = useFetch(listJournals, [reloadKey])
  const journals = data ?? []

  // Accounts are only needed to populate the Default Account dropdown, so
  // a failure here shouldn't block the journal list itself from rendering.
  const { data: accountsData } = useFetch(listAccounts, [])
  const accounts = accountsData ?? []

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

  function openEdit(journal) {
    setEditingId(journal.id)
    setForm({
      name: journal.name ?? '',
      journal_type: toDisplayLabel(JOURNAL_TYPE_MAP, journal.type) ?? 'Sales',
      default_account_id: journal.default_account_id ?? '',
    })
    setFormError('')
    setModalOpen(true)
  }

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  async function handleDelete(journal) {
    if (!window.confirm(`Deactivate journal "${journal.name}"?`)) return
    setActionError('')
    try {
      await deleteJournal(journal.id)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setActionError(err.message || 'Could not deactivate this journal.')
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.name.trim()) return setFormError('Journal name is required.')
    if (!form.journal_type) return setFormError('Journal type is required.')
    setFormError('')
    setSaving(true)
    const payload = toBackendPayload(form)
    try {
      if (editingId) {
        await updateJournal(editingId, payload)
      } else {
        await createJournal(payload)
      }
      setModalOpen(false)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setFormError(err.message || 'Could not save this journal.')
    } finally {
      setSaving(false)
    }
  }

  const columns = [
    { key: 'name', label: 'Name' },
    {
      key: 'type',
      label: 'Type',
      render: (row) => toDisplayLabel(JOURNAL_TYPE_MAP, row.type),
    },
    {
      key: 'default_account_id',
      label: 'Default Account',
      render: (row) => (row.default_account_id ? accountName(row.default_account_id) : '—'),
    },
    {
      // Backend Checkpoint 1's JournalResponse has no status/is_active
      // field at all, so there is nothing real to show here yet.
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
            title="Backend Checkpoint 1 does not provide a PUT /journals/{id} route yet."
          >
            Edit
          </button>
          <button
            className="link-action danger"
            onClick={() => handleDelete(row)}
            disabled
            title="Backend Checkpoint 1 does not provide a DELETE /journals/{id} route yet."
          >
            Deactivate
          </button>
        </div>
      ),
    },
  ]

  return (
    <PageShell
      title="Journals"
      description="Sales, Purchase, Bank and Cash journals used for transactions."
      actions={<Button onClick={openCreate}>Add Journal</Button>}
    >
      <p className="card-empty" style={{ marginBottom: '0.5rem' }}>
        Editing and deactivating journals is not yet available — Backend Checkpoint 1
        only implements creating and listing journals.
      </p>

      {actionError && <div className="form-error-banner">{actionError}</div>}

      {loading && <p className="card-empty">Loading journals...</p>}
      {error && !loading && (
        <div className="form-error-banner">
          Could not load journals: {error.message}
        </div>
      )}
      {!loading && !error && (
        <Table columns={columns} rows={journals} emptyMessage="No journals found." />
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <h3>{editingId ? 'Edit Journal' : 'Add Journal'}</h3>
        <form onSubmit={handleSubmit}>
          {formError && <div className="form-error-banner">{formError}</div>}

          <FormField label="Name" htmlFor="journal-name">
            <input
              id="journal-name"
              type="text"
              value={form.name}
              onChange={(e) => updateField('name', e.target.value)}
            />
          </FormField>

          <FormField label="Type" htmlFor="journal-type">
            <select
              id="journal-type"
              value={form.journal_type}
              onChange={(e) => updateField('journal_type', e.target.value)}
            >
              {JOURNAL_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </FormField>

          <FormField label="Default Account" htmlFor="journal-account">
            <select
              id="journal-account"
              value={form.default_account_id}
              onChange={(e) => updateField('default_account_id', e.target.value)}
            >
              <option value="">No default account</option>
              {accounts.map((a) => (
                <option key={a.id} value={a.id}>{a.code} — {a.name}</option>
              ))}
            </select>
          </FormField>

          <div className="form-actions">
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save Journal'}
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
