// Route: /reports/budget
//
// Committed vs Achieved per budget, plus an overall total, for a chosen
// year. Tries the dedicated GET /reports/budget endpoint first (see
// report.service.js, same convention as Balance Sheet / P&L); if that
// isn't available yet, falls back to summarizing the real confirmed/
// revised budgets from services/budget.service.js's listBudgets — never
// fabricated numbers, since a budget's committed/achieved figures are
// meaningful data, not a demo scenario like the Dashboard's KPIs.
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import Button from '../../components/common/Button.jsx'
import YearFilter from '../../components/common/YearFilter.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import BudgetPieChart from '../../components/charts/BudgetPieChart.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { getBudgetReport } from '../../services/report.service.js'
import { listBudgets } from '../../services/budget.service.js'
import { formatCurrency, formatDate, formatPercent } from '../../utils/formatters.js'
import { BUDGET_STATUS_MAP, toDisplayLabel } from '../../utils/enumMap.js'

// Only Confirmed/Revised budgets have meaningful achieved figures — a
// Draft budget hasn't been locked in yet, and a Cancelled one is out of
// scope for a report on progress against plan.
const REPORTABLE_STATUSES = ['confirmed', 'revised']

function rowFromBudget(b) {
  return {
    id: b.id,
    name: b.name,
    period: `${formatDate(b.period_start ?? b.start_date)} - ${formatDate(b.period_end ?? b.end_date)}`,
    analyticName: b.analytic_account_name ?? b.analytic_account?.name ?? b.analytic_account_id ?? '—',
    status: b.status,
    committed: Number(b.committed_amount ?? b.amount ?? 0),
    achieved: Number(b.achieved_amount ?? 0),
    achievedPercentage: b.achieved_percentage ?? b.achieved_percent,
  }
}

export default function BudgetReport() {
  const [year, setYear] = useState(new Date().getFullYear())

  const { data: reportData, loading: reportLoading, error: reportError } = useFetch(() => getBudgetReport(year), [year])

  // Only used as a fallback if the report endpoint above fails or
  // returns no rows — see the comment at the top of this file.
  const needsFallback = !reportLoading && (reportError || !(reportData?.budgets ?? reportData ?? []).length)
  const { data: budgetsData, loading: budgetsLoading, error: budgetsError } = useFetch(
    listBudgets,
    [needsFallback]
  )

  const loading = reportLoading || (needsFallback && budgetsLoading)

  const rows = useMemo(() => {
    if (!needsFallback) {
      const reportRows = reportData?.budgets ?? reportData ?? []
      return reportRows.map(rowFromBudget)
    }
    return (budgetsData ?? [])
      .filter((b) => REPORTABLE_STATUSES.includes(String(b.status ?? '').toLowerCase()))
      .map(rowFromBudget)
  }, [needsFallback, reportData, budgetsData])

  const totals = useMemo(
    () => rows.reduce(
      (acc, r) => ({ committed: acc.committed + r.committed, achieved: acc.achieved + r.achieved }),
      { committed: 0, achieved: 0 }
    ),
    [rows]
  )

  const usingFallback = needsFallback
  const error = usingFallback ? budgetsError : null

  return (
    <PageShell
      title="Budget Report"
      description="Committed vs achieved spend/revenue by budget for the selected year."
      actions={<Button type="button" variant="secondary" onClick={() => window.print()}>Print</Button>}
    >
      <div className="list-toolbar">
        <YearFilter value={year} onChange={setYear} />
      </div>

      {usingFallback && !loading && rows.length > 0 && (
        <p className="demo-data-note">
          The dedicated budget report endpoint isn't returning results yet — showing figures
          summarized from your confirmed/revised budgets instead.
        </p>
      )}

      {loading && <p className="card-empty">Loading budget report...</p>}
      {error && !loading && (
        <div className="form-error-banner">Could not load the budget report: {error.message}</div>
      )}

      {!loading && !error && rows.length === 0 && (
        <p className="card-empty">
          No confirmed budgets for {year} yet. <Link className="link-action" to="/budgets/new">Create a budget</Link> and
          confirm it to see progress here.
        </p>
      )}

      {!loading && !error && rows.length > 0 && (
        <>
          <div className="detail-card" style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <BudgetPieChart committed={totals.committed} achieved={totals.achieved} size={120} />
            <div className="detail-grid" style={{ flex: 1 }}>
              <div>
                <div className="detail-field-label">Total Committed</div>
                <div className="detail-field-value">{formatCurrency(totals.committed)}</div>
              </div>
              <div>
                <div className="detail-field-label">Total Achieved</div>
                <div className="detail-field-value">{formatCurrency(totals.achieved)}</div>
              </div>
              <div>
                <div className="detail-field-label">Overall Achieved %</div>
                <div className="detail-field-value">
                  {formatPercent(totals.committed > 0 ? totals.achieved / totals.committed : 0)}
                </div>
              </div>
            </div>
          </div>

          <table className="line-items-table" style={{ marginTop: '1rem' }}>
            <thead>
              <tr>
                <th>Budget</th>
                <th>Period</th>
                <th>Analytic Account</th>
                <th>Status</th>
                <th className="text-right">Committed</th>
                <th className="text-right">Achieved</th>
                <th className="text-right">Achieved %</th>
                <th>Progress</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>
                    <Link className="link-action" to={`/budgets/${r.id}`}>{r.name}</Link>
                  </td>
                  <td>{r.period}</td>
                  <td>{r.analyticName}</td>
                  <td>
                    <StatusBadge status={toDisplayLabel(BUDGET_STATUS_MAP, String(r.status ?? 'confirmed').toLowerCase())} />
                  </td>
                  <td className="text-right">{formatCurrency(r.committed)}</td>
                  <td className="text-right">{formatCurrency(r.achieved)}</td>
                  <td className="text-right">
                    {formatPercent(r.achievedPercentage ?? (r.committed > 0 ? r.achieved / r.committed : 0))}
                  </td>
                  <td>
                    <BudgetPieChart committed={r.committed} achieved={r.achieved} size={40} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </PageShell>
  )
}
