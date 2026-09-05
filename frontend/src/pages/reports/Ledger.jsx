// Route: /reports/ledger
// General Ledger for a chosen account/year. All balances (opening,
// running, closing) are displayed exactly as returned by
// GET /reports/ledger — nothing here recomputes an accounting balance.
import { useMemo, useState } from 'react'
import PageShell from '../../components/common/PageShell.jsx'
import Button from '../../components/common/Button.jsx'
import YearFilter from '../../components/common/YearFilter.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { listAccounts } from '../../services/account.service.js'
import { getLedger } from '../../services/report.service.js'
import { formatCurrency, formatDate } from '../../utils/formatters.js'

export default function Ledger() {
  const { data: accountsData, loading: accountsLoading, error: accountsError } = useFetch(listAccounts, [])
  const accounts = accountsData ?? []

  const [accountId, setAccountId] = useState('')
  const [year, setYear] = useState(new Date().getFullYear())

  const [ledger, setLedger] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function loadLedger(nextAccountId, nextYear) {
    if (!nextAccountId) {
      setLedger(null)
      return
    }
    setLoading(true)
    setError('')
    getLedger(nextAccountId, nextYear)
      .then((result) => setLedger(result))
      .catch((err) => setError(err.message || 'Could not load the ledger for this account.'))
      .finally(() => setLoading(false))
  }

  function handleAccountChange(value) {
    setAccountId(value)
    loadLedger(value, year)
  }

  function handleYearChange(value) {
    setYear(value)
    loadLedger(accountId, value)
  }

  // Backend response shape isn't confirmed yet — accept either a bare
  // array of lines, or an object with lines/entries plus opening/closing
  // balance fields. Nothing here is computed; every value shown is read
  // straight off whichever field the backend supplied.
  const lines = useMemo(() => {
    if (!ledger) return []
    if (Array.isArray(ledger)) return ledger
    return ledger.lines ?? ledger.entries ?? []
  }, [ledger])

  const openingBalance = Array.isArray(ledger) ? null : ledger?.opening_balance
  const closingBalance = Array.isArray(ledger) ? null : ledger?.closing_balance

  const selectedAccount = accounts.find((a) => String(a.id) === String(accountId))

  return (
    <PageShell
      title="Ledger"
      description="Account-wise transaction history as recorded by the backend."
      actions={<Button type="button" variant="secondary" onClick={() => window.print()}>Print</Button>}
    >
      <div className="list-toolbar">
        <div className="form-field">
          <label htmlFor="ledger-account">Account</label>
          <select
            id="ledger-account"
            value={accountId}
            onChange={(e) => handleAccountChange(e.target.value)}
          >
            <option value="">Select an account...</option>
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>{a.code ? `${a.code} — ` : ''}{a.name}</option>
            ))}
          </select>
        </div>
        <YearFilter value={year} onChange={handleYearChange} />
      </div>

      {accountsLoading && <p className="card-empty">Loading accounts...</p>}
      {accountsError && !accountsLoading && (
        <div className="form-error-banner">Could not load accounts: {accountsError.message}</div>
      )}

      {!accountId && !accountsLoading && (
        <p className="card-empty">Select an account above to view its ledger.</p>
      )}

      {accountId && loading && <p className="card-empty">Loading ledger...</p>}
      {accountId && error && !loading && (
        <div className="form-error-banner">{error}</div>
      )}

      {accountId && !loading && !error && ledger && (
        <div className="detail-card">
          <div className="detail-grid">
            <div>
              <div className="detail-field-label">Account</div>
              <div className="detail-field-value">{selectedAccount?.name ?? accountId}</div>
            </div>
            <div>
              <div className="detail-field-label">Opening Balance</div>
              <div className="detail-field-value">{openingBalance != null ? formatCurrency(openingBalance) : '—'}</div>
            </div>
            <div>
              <div className="detail-field-label">Closing Balance</div>
              <div className="detail-field-value">{closingBalance != null ? formatCurrency(closingBalance) : '—'}</div>
            </div>
          </div>

          <table className="line-items-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Journal</th>
                <th>Reference</th>
                <th className="text-right">Debit</th>
                <th className="text-right">Credit</th>
                <th className="text-right">Balance</th>
              </tr>
            </thead>
            <tbody>
              {lines.length === 0 && (
                <tr><td colSpan={6} className="card-empty">No transactions found for this account/year.</td></tr>
              )}
              {lines.map((l, i) => (
                <tr key={l.id ?? i}>
                  <td>{formatDate(l.date ?? l.entry_date)}</td>
                  <td>{l.journal_name ?? l.journal?.name ?? l.journal_id ?? '—'}</td>
                  <td>{l.reference || '—'}</td>
                  <td className="text-right">{l.debit ? formatCurrency(l.debit) : '—'}</td>
                  <td className="text-right">{l.credit ? formatCurrency(l.credit) : '—'}</td>
                  <td className="text-right">{l.balance != null ? formatCurrency(l.balance) : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </PageShell>
  )
}
