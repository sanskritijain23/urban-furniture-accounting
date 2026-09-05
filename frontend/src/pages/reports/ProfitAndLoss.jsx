// Route: /reports/profit-loss
// Income vs Expenses with Net Income, year filter, Print button. Every
// figure — including Net Income — comes straight from
// GET /reports/profit-loss; nothing is recalculated in the frontend.
import { useState } from 'react'
import PageShell from '../../components/common/PageShell.jsx'
import Button from '../../components/common/Button.jsx'
import YearFilter from '../../components/common/YearFilter.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { getProfitAndLoss } from '../../services/report.service.js'
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

export default function ProfitAndLoss() {
  const [year, setYear] = useState(new Date().getFullYear())
  const { data, loading, error } = useFetch(() => getProfitAndLoss(year), [year])

  return (
    <PageShell
      title="Profit & Loss Report"
      description="Income and expenses as reported by the backend."
      actions={<Button type="button" variant="secondary" onClick={() => window.print()}>Print</Button>}
    >
      <div className="list-toolbar">
        <YearFilter value={year} onChange={setYear} />
      </div>

      {loading && <p className="card-empty">Loading profit &amp; loss report...</p>}
      {error && !loading && (
        <div className="form-error-banner">Could not load the profit &amp; loss report: {error.message}</div>
      )}

      {!loading && !error && data && (
        <>
          <ReportSection
            title="Income"
            rows={data.income}
            total={data.total_income}
          />
          <ReportSection
            title="Expenses"
            rows={data.expenses}
            total={data.total_expenses}
          />
          <div className="detail-card">
            <div className="detail-field-label">Net Income</div>
            <div className="detail-field-value" style={{ fontSize: '18px' }}>
              {data.net_income != null ? formatCurrency(data.net_income) : '—'}
            </div>
          </div>
        </>
      )}
    </PageShell>
  )
}
