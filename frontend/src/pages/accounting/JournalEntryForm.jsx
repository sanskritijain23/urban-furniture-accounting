// Route: /journal-entries/new
// MUST HAVE (manual Journal Entry screen).
//
// Accounting Date + Journal selection + an Account/Partner/Debit/Credit
// line grid. Save is blocked client-side (in addition to whatever the
// backend checks) unless there are at least two lines and
// SUM(debit) === SUM(credit) — the same balance rule
// JournalEntryDetail.jsx already enforces before allowing Post.
// Posting itself happens on that existing detail page once this entry
// exists as a draft, so this screen only needs to create it and hand
// off — it does not duplicate the Post action.
import { useEffect, useMemo, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import FormField from '../../components/forms/FormField.jsx'
import Button from '../../components/common/Button.jsx'
import { createManualJournalEntry } from '../../services/journalEntry.service.js'
import { listJournals } from '../../services/journal.service.js'
import { listAccounts } from '../../services/account.service.js'
import { listContacts } from '../../services/contact.service.js'
import { formatCurrency } from '../../utils/formatters.js'

function emptyLine() {
  return { account_id: '', partner_id: '', debit: '', credit: '' }
}

export default function JournalEntryForm() {
  const navigate = useNavigate()

  const [journals, setJournals] = useState([])
  const [accounts, setAccounts] = useState([])
  const [contacts, setContacts] = useState([])

  const [journalId, setJournalId] = useState('')
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [reference, setReference] = useState('')
  const [lines, setLines] = useState([emptyLine(), emptyLine()])

  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    listJournals().then((result) => setJournals(result ?? [])).catch(() => setJournals([]))
    listAccounts().then((result) => setAccounts(result ?? [])).catch(() => setAccounts([]))
    listContacts().then((result) => setContacts(result ?? [])).catch(() => setContacts([]))
  }, [])

  const totals = useMemo(() => {
    return lines.reduce(
      (acc, l) => ({
        debit: acc.debit + (Number(l.debit) || 0),
        credit: acc.credit + (Number(l.credit) || 0),
      }),
      { debit: 0, credit: 0 }
    )
  }, [lines])

  const balanced = Math.abs(totals.debit - totals.credit) < 0.01 && totals.debit > 0

  function updateLine(index, field, value) {
    setLines((prev) => {
      const next = [...prev]
      const line = { ...next[index], [field]: value }
      // A single line is either a debit or a credit, never both —
      // clear the other side as soon as one is typed into, same as a
      // real journal-entry grid.
      if (field === 'debit' && value !== '') line.credit = ''
      if (field === 'credit' && value !== '') line.debit = ''
      next[index] = line
      return next
    })
  }

  function addLine() {
    setLines((prev) => [...prev, emptyLine()])
  }

  function removeLine(index) {
    setLines((prev) => (prev.length <= 2 ? prev : prev.filter((_, i) => i !== index)))
  }

  function validate() {
    if (!journalId) return 'Journal is required.'
    if (!date) return 'Accounting date is required.'
    const filledLines = lines.filter((l) => l.account_id)
    if (filledLines.length < 2) return 'A journal entry needs at least two lines with an account selected.'
    for (const l of filledLines) {
      const debit = Number(l.debit) || 0
      const credit = Number(l.credit) || 0
      if (debit === 0 && credit === 0) return 'Every line needs a debit or a credit amount.'
      if (debit !== 0 && credit !== 0) return 'A line cannot have both a debit and a credit amount.'
    }
    if (!balanced) return 'Total debits must equal total credits before this entry can be saved.'
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
      journal_id: journalId,
      date,
      reference: reference || null,
      lines: lines
        .filter((l) => l.account_id)
        .map((l) => ({
          account_id: l.account_id,
          partner_id: l.partner_id || null,
          debit: Number(l.debit) || 0,
          credit: Number(l.credit) || 0,
        })),
    }
    try {
      const created = await createManualJournalEntry(payload)
      navigate(created?.id ? `/journal-entries/${created.id}` : '/journal-entries')
    } catch (err) {
      setError(err.message || 'Could not save this journal entry.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <PageShell
      title="Manual Journal Entry"
      description="Record a manual accounting entry. Debits and credits must balance before it can be saved; posting happens from the entry's detail page afterwards."
    >
      <form className="detail-card" onSubmit={handleSubmit} style={{ maxWidth: 860 }}>
        {error && <div className="form-error-banner">{error}</div>}

        <div className="form-row">
          <FormField label="Journal" htmlFor="je_journal">
            <select id="je_journal" value={journalId} onChange={(e) => setJournalId(e.target.value)}>
              <option value="">Select a journal...</option>
              {journals.map((j) => (
                <option key={j.id} value={j.id}>{j.name}</option>
              ))}
            </select>
          </FormField>
          <FormField label="Accounting Date" htmlFor="je_date">
            <input id="je_date" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </FormField>
        </div>

        <FormField label="Reference (optional)" htmlFor="je_reference">
          <input
            id="je_reference"
            type="text"
            value={reference}
            onChange={(e) => setReference(e.target.value)}
          />
        </FormField>

        <table className="line-items-table">
          <thead>
            <tr>
              <th>Account</th>
              <th>Partner (optional)</th>
              <th className="text-right">Debit</th>
              <th className="text-right">Credit</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {lines.map((line, i) => (
              <tr key={i}>
                <td>
                  <select
                    value={line.account_id}
                    onChange={(e) => updateLine(i, 'account_id', e.target.value)}
                  >
                    <option value="">Select account...</option>
                    {accounts.map((a) => (
                      <option key={a.id} value={a.id}>{a.name}</option>
                    ))}
                  </select>
                </td>
                <td>
                  <select
                    value={line.partner_id}
                    onChange={(e) => updateLine(i, 'partner_id', e.target.value)}
                  >
                    <option value="">None</option>
                    {contacts.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </td>
                <td>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={line.debit}
                    onChange={(e) => updateLine(i, 'debit', e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={line.credit}
                    onChange={(e) => updateLine(i, 'credit', e.target.value)}
                  />
                </td>
                <td>
                  {lines.length > 2 && (
                    <button type="button" className="link-action danger" onClick={() => removeLine(i)}>
                      Remove
                    </button>
                  )}
                </td>
              </tr>
            ))}
            <tr className="line-items-total-row">
              <td colSpan={2}>
                <button type="button" className="link-action" onClick={addLine}>+ Add line</button>
              </td>
              <td className="text-right">{formatCurrency(totals.debit)}</td>
              <td className="text-right">{formatCurrency(totals.credit)}</td>
              <td></td>
            </tr>
          </tbody>
        </table>

        {!balanced && (totals.debit > 0 || totals.credit > 0) && (
          <p className="card-empty" style={{ margin: '0.5rem 0 0' }}>
            Debits and credits must be equal before this entry can be saved.
          </p>
        )}

        <div className="form-actions">
          <Button type="submit" disabled={saving || !balanced}>
            {saving ? 'Saving...' : 'Save Entry'}
          </Button>
          <Link to="/journal-entries"><Button type="button" variant="secondary">Cancel</Button></Link>
        </div>
      </form>
    </PageShell>
  )
}
