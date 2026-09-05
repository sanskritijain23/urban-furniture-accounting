// Route: /journal-entries/:id
// Read-only detail view of one journal entry (manual or auto-generated)
// plus its Post action for entries still in draft. Debit/Credit totals
// and the balanced check are the same line-sum shown in the list — no
// backend accounting balance is recomputed here.
import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import Button from '../../components/common/Button.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import { getJournalEntry, postJournalEntry } from '../../services/journalEntry.service.js'
import { formatCurrency, formatDate } from '../../utils/formatters.js'
import { JOURNAL_ENTRY_STATUS_MAP, toDisplayLabel } from '../../utils/enumMap.js'

export default function JournalEntryDetail() {
  const { id } = useParams()

  const [entry, setEntry] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')

  const [posting, setPosting] = useState(false)
  const [postError, setPostError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    getJournalEntry(id)
      .then((result) => { if (!cancelled) setEntry(result) })
      .catch((err) => { if (!cancelled) setLoadError(err.message || 'Could not load this journal entry.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [id, reloadKey])

  async function handlePost() {
    setPostError('')
    setPosting(true)
    try {
      await postJournalEntry(id)
      setReloadKey((k) => k + 1)
    } catch (err) {
      setPostError(err.message || 'Could not post this journal entry.')
    } finally {
      setPosting(false)
    }
  }

  if (loading) {
    return (
      <PageShell title="Journal Entry">
        <p className="card-empty">Loading journal entry...</p>
      </PageShell>
    )
  }

  if (loadError) {
    return (
      <PageShell title="Journal Entry">
        <div className="form-error-banner">{loadError}</div>
      </PageShell>
    )
  }

  const status = String(entry?.status ?? 'draft').toLowerCase()
  const lines = entry?.lines ?? []
  const totalDebit = entry?.total_debit ?? entry?.debit_total
    ?? lines.reduce((sum, l) => sum + Number(l.debit ?? 0), 0)
  const totalCredit = entry?.total_credit ?? entry?.credit_total
    ?? lines.reduce((sum, l) => sum + Number(l.credit ?? 0), 0)
  const balanced = Math.abs(Number(totalDebit) - Number(totalCredit)) < 0.01

  return (
    <PageShell
      title={`Journal Entry ${entry?.entry_number ? `— ${entry.entry_number}` : `#${entry?.id ?? id}`}`}
      actions={<Link to="/journal-entries"><Button variant="secondary">Back to list</Button></Link>}
    >
      {postError && <div className="form-error-banner">{postError}</div>}
      {status === 'posted' && !postError && (
        <div className="form-success-banner">Journal entry posted.</div>
      )}

      <div className="detail-card">
        <div className="detail-grid">
          <div>
            <div className="detail-field-label">Status</div>
            <StatusBadge status={toDisplayLabel(JOURNAL_ENTRY_STATUS_MAP, status)} />
          </div>
          <div>
            <div className="detail-field-label">Date</div>
            <div className="detail-field-value">{formatDate(entry?.date ?? entry?.entry_date)}</div>
          </div>
          <div>
            <div className="detail-field-label">Journal</div>
            <div className="detail-field-value">{entry?.journal_name ?? entry?.journal?.name ?? entry?.journal_id ?? '—'}</div>
          </div>
          <div>
            <div className="detail-field-label">Reference</div>
            <div className="detail-field-value">{entry?.reference || '—'}</div>
          </div>
          <div>
            <div className="detail-field-label">Balanced</div>
            <span className={`status-badge ${balanced ? 'status-balanced' : 'status-unbalanced'}`}>
              {balanced ? 'Balanced' : 'Unbalanced'}
            </span>
          </div>
        </div>

        <table className="line-items-table">
          <thead>
            <tr>
              <th>Account</th>
              <th>Partner</th>
              <th className="text-right">Debit</th>
              <th className="text-right">Credit</th>
            </tr>
          </thead>
          <tbody>
            {lines.length === 0 && (
              <tr><td colSpan={4} className="card-empty">No lines on this entry.</td></tr>
            )}
            {lines.map((l, i) => (
              <tr key={l.id ?? i}>
                <td>{l.account_name ?? l.account?.name ?? l.account_id}</td>
                <td>{l.partner_name ?? l.partner?.name ?? l.partner_id ?? '—'}</td>
                <td className="text-right">{l.debit ? formatCurrency(l.debit) : '—'}</td>
                <td className="text-right">{l.credit ? formatCurrency(l.credit) : '—'}</td>
              </tr>
            ))}
            <tr className="line-items-total-row">
              <td colSpan={2}>Total</td>
              <td className="text-right">{formatCurrency(totalDebit)}</td>
              <td className="text-right">{formatCurrency(totalCredit)}</td>
            </tr>
          </tbody>
        </table>

        {status === 'draft' && (
          <div className="form-actions">
            <Button type="button" onClick={handlePost} disabled={posting || !balanced}>
              {posting ? 'Posting...' : 'Post'}
            </Button>
            {!balanced && (
              <p className="card-empty" style={{ margin: 0, alignSelf: 'center' }}>
                Debits and credits must be equal before this entry can be posted.
              </p>
            )}
          </div>
        )}
      </div>
    </PageShell>
  )
}
