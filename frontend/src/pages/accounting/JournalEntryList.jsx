// Route: /journal-entries
// Lists all journal entries (manual + auto-generated from Sales/Purchase
// documents). Date/Journal/Reference/Status/Total Debit/Total Credit/
// Balanced columns per Checkpoint 6A.
//
// "Balanced" is a plain equality check on the debit/credit totals the
// backend already returned for this entry (mirrors the check
// JournalEntryForm blocks Post on) — it is not a recomputed accounting
// balance, so it's fine to do client-side.
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import Table from '../../components/common/Table.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import Button from '../../components/common/Button.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { listJournalEntries } from '../../services/journalEntry.service.js'
import { formatCurrency, formatDate } from '../../utils/formatters.js'
import { JOURNAL_ENTRY_STATUS_MAP, JOURNAL_ENTRY_STATUS_OPTIONS, toDisplayLabel } from '../../utils/enumMap.js'

const FILTERS = ['All', ...JOURNAL_ENTRY_STATUS_OPTIONS]

// Backend may return per-entry totals directly (total_debit/total_credit,
// or debit_total/credit_total), or only the line grid (lines: [{debit,
// credit}]). Try the explicit totals first and only sum lines as a
// fallback — same defensive convention used for document totals
// elsewhere in this app (see VendorBillForm's `total` calc).
function totals(entry) {
  const lines = entry.lines ?? []
  const debit = entry.total_debit ?? entry.debit_total
    ?? lines.reduce((sum, l) => sum + Number(l.debit ?? 0), 0)
  const credit = entry.total_credit ?? entry.credit_total
    ?? lines.reduce((sum, l) => sum + Number(l.credit ?? 0), 0)
  return { debit: Number(debit) || 0, credit: Number(credit) || 0 }
}

export default function JournalEntryList() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('All')

  const { data, loading, error } = useFetch(listJournalEntries, [])
  const entries = data ?? []

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    return entries.filter((entry) => {
      const status = String(entry.status ?? 'draft').toLowerCase()
      const matchesFilter = filter === 'All' || status === filter.toLowerCase()
      if (!matchesFilter) return false
      if (!term) return true
      const journalName = entry.journal_name ?? entry.journal?.name ?? ''
      return [entry.entry_number, entry.reference, journalName].some((field) =>
        String(field ?? '').toLowerCase().includes(term)
      )
    })
  }, [entries, search, filter])

  const columns = [
    {
      key: 'entry_number',
      label: 'Entry #',
      render: (row) => (
        <Link className="link-action" to={`/journal-entries/${row.id}`}>
          {row.entry_number ?? `#${row.id}`}
        </Link>
      ),
    },
    {
      key: 'date',
      label: 'Date',
      render: (row) => formatDate(row.date ?? row.entry_date),
    },
    {
      key: 'journal',
      label: 'Journal',
      render: (row) => row.journal_name ?? row.journal?.name ?? row.journal_id ?? '—',
    },
    {
      key: 'reference',
      label: 'Reference',
      render: (row) => row.reference || '—',
    },
    {
      key: 'status',
      label: 'Status',
      render: (row) => (
        <StatusBadge status={toDisplayLabel(JOURNAL_ENTRY_STATUS_MAP, String(row.status ?? 'draft').toLowerCase())} />
      ),
    },
    {
      key: 'total_debit',
      label: 'Total Debit',
      render: (row) => formatCurrency(totals(row).debit),
    },
    {
      key: 'total_credit',
      label: 'Total Credit',
      render: (row) => formatCurrency(totals(row).credit),
    },
    {
      key: 'balanced',
      label: 'Balanced',
      render: (row) => {
        const { debit, credit } = totals(row)
        const balanced = Math.abs(debit - credit) < 0.01
        return (
          <span className={`status-badge ${balanced ? 'status-balanced' : 'status-unbalanced'}`}>
            {balanced ? 'Balanced' : 'Unbalanced'}
          </span>
        )
      },
    },
  ]

  return (
    <PageShell
      title="Journal Entries List"
      description="All manual and auto-generated journal entries."
      actions={<Link to="/journal-entries/new"><Button>New Entry</Button></Link>}
    >
      <div className="list-toolbar">
        <input
          className="search-input"
          type="text"
          placeholder="Search by entry #, reference or journal..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="view-toggle">
          {FILTERS.map((f) => (
            <Button
              key={f}
              type="button"
              variant={filter === f ? 'primary' : 'secondary'}
              onClick={() => setFilter(f)}
            >
              {f}
            </Button>
          ))}
        </div>
      </div>

      {loading && <p className="card-empty">Loading journal entries...</p>}
      {error && !loading && (
        <div className="form-error-banner">Could not load journal entries: {error.message}</div>
      )}
      {!loading && !error && (
        <Table columns={columns} rows={filtered} emptyMessage="No journal entries found." />
      )}
    </PageShell>
  )
}
