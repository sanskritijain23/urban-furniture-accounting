// Route: /reports/balance-sheet
// Assets vs Liabilities (and Equity/Capital, if the backend returns a
// section for it), with a year filter and a Print button. Every figure
// shown — section totals and the grand total — is read directly from
// GET /reports/balance-sheet; none of it is summed or recalculated
// client-side.
import { useState } from 'react'
import PageShell from '../../components/common/PageShell.jsx'
import Button from '../../components/common/Button.jsx'
import YearFilter from '../../components/common/YearFilter.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { getBalanceSheet } from '../../services/report.service.js'
import { formatCurrency } from '../../utils/formatters.js'

function ReportSection({ title, rows, total }) {
  return (
    <table className="line-items-table">
      <thead>
        <tr>
          <th colSpan={2}>{title}</th>
        </tr>
      </thead>
      <tbody>
        {(!rows || rows.length === 0) && (
          <tr><td colSpan={2} className="card-empty">No accounts in this section.</td></tr>
        )}
        {(rows ?? []).map((row, i) => (
          <tr key={row.account_id ?? i}>
            <td>{row.account_name ?? row.name ?? row.account_id}</td>
            <td className="text-right">{formatCurrency(row.balance ?? row.amount)}</td>
          </tr>
        ))}
        <tr className="line-items-total-row">
          <td>Total {title}</td>
          <td className="text-right">{total != null ? formatCurrency(total) : '—'}</td>
        </tr>
      </tbody>
    </table>
  )
}

export default function BalanceSheet() {
  const [year, setYear] = useState(new Date().getFullYear())
  const { data, loading, error } = useFetch(() => getBalanceSheet(year), [year])

  return (
    <PageShell
      title="Balance Sheet"
      description="Assets, liabilities and equity as reported by the backend."
      actions={<Button type="button" variant="secondary" onClick={() => window.print()}>Print</Button>}
    >
      <div className="list-toolbar">
        <YearFilter value={year} onChange={setYear} />
      </div>

      {loading && <p className="card-empty">Loading balance sheet...</p>}
      {error && !loading && (
        <div className="form-error-banner">Could not load the balance sheet: {error.message}</div>
      )}

      {!loading && !error && data && (
        <>
          <ReportSection
            title="Assets"
            rows={data.assets}
            total={data.total_assets}
          />
          <ReportSection
            title="Liabilities"
            rows={data.liabilities}
            total={data.total_liabilities}
          />
          {(data.equity || data.total_equity != null) && (
            <ReportSection
              title="Equity"
              rows={data.equity}
              total={data.total_equity}
            />
          )}
        </>
      )}
    </PageShell>
  )
}
