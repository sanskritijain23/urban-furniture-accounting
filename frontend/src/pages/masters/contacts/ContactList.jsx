// Route: /contacts
// Role allowed: admin, accountant
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../../../components/common/PageShell.jsx'
import Table from '../../../components/common/Table.jsx'
import StatusBadge from '../../../components/common/StatusBadge.jsx'
import Button from '../../../components/common/Button.jsx'
import { useFetch } from '../../../hooks/useFetch.js'
import { listContacts, deleteContact } from '../../../services/contact.service.js'
import { CONTACT_TYPE_MAP, toDisplayLabel } from '../../../utils/enumMap.js'

export default function ContactList() {
  const [search, setSearch] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const [actionError, setActionError] = useState('')

  const { data, loading, error } = useFetch(listContacts, [reloadKey])
  const contacts = data ?? []

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return contacts
    return contacts.filter((c) =>
      [c.name, c.email].some((field) => String(field ?? '').toLowerCase().includes(term))
    )
  }, [contacts, search])

  async function handleDelete(contact) {
    if (!window.confirm(`Deactivate contact "${contact.name}"?`)) return
    setActionError('')
    try {
      await deleteContact(contact.id)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setActionError(err.message || 'Could not deactivate this contact.')
    }
  }

  const columns = [
    { key: 'name', label: 'Name' },
    {
      key: 'type',
      label: 'Type',
      render: (row) => toDisplayLabel(CONTACT_TYPE_MAP, row.type),
    },
    { key: 'email', label: 'Email' },
    { key: 'mobile', label: 'Phone' },
    {
      // Backend Checkpoint 1's ContactResponse has no status/is_active
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
          <Link className="link-action" to={`/contacts/${row.id}`}>Edit</Link>
          <button
            className="link-action danger"
            onClick={() => handleDelete(row)}
            disabled
            title="Backend Checkpoint 1 does not provide a DELETE /contacts/{id} route yet."
          >
            Deactivate
          </button>
        </div>
      ),
    },
  ]

  return (
    <PageShell
      title="Contacts"
      description="Customers, vendors and other contacts."
      actions={<Link to="/contacts/new"><Button>Add Contact</Button></Link>}
    >
      <div className="list-toolbar">
        <input
          className="search-input"
          type="text"
          placeholder="Search by name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {actionError && <div className="form-error-banner">{actionError}</div>}

      {loading && <p className="card-empty">Loading contacts...</p>}
      {error && !loading && (
        <div className="form-error-banner">
          Could not load contacts: {error.message}
        </div>
      )}
      {!loading && !error && (
        <Table columns={columns} rows={filtered} emptyMessage="No contacts found." />
      )}
    </PageShell>
  )
}
