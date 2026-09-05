// Route: /budgets
// List of Budgets with All/Draft/Confirmed/Revised/Cancelled filters and
// New/Confirm/Revise/Cancel actions (Confirm/Revise/Cancel happen from the
// detail page — see BudgetForm.jsx — this list links out to it).
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../../components/common/PageShell.jsx'
import Table from '../../components/common/Table.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import Button from '../../components/common/Button.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { listBudgets } from '../../services/budget.service.js'
import { formatCurrency, formatDate, formatPercent } from '../../utils/formatters.js'
import { BUDGET_STATUS_MAP, toDisplayLabel } from '../../utils/enumMap.js'

const FILTERS = ['All', 'Draft', 'Confirmed', 'Revised', 'Cancelled']

export default function BudgetList() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('All')

  const { data, loading, error } = useFetch(listBudgets, [])
  const budgets = data ?? []

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    return budgets.filter((b) => {
      const status = String(b.status ?? 'draft').toLowerCase()
      const matchesFilter = filter === 'All' || status === filter.toLowerCase()
      if (!matchesFilter) return false
      if (!term) return true
      const responsibleName = b.responsible_name ?? b.responsible?.name ?? ''
      const analyticName = b.analytic_account_name ?? b.analytic_account?.name ?? ''
      return [b.name, responsibleName, analyticName].some((field) =>
        String(field ?? '').toLowerCase().includes(term)
      )
    })
  }, [budgets, search, filter])

  const columns = [
    {
      key: 'name',
      label: 'Budget',
      render: (row) => (
        <Link className="link-action" to={`/budgets/${row.id}`}>
          {row.name || `#${row.id}`}
        </Link>
      ),
    },
    {
      key: 'period',
      label: 'Period',
      render: (row) => {
        const start = formatDate(row.period_start ?? row.start_date)
        const end = formatDate(row.period_end ?? row.end_date)
        if (!start && !end) return '—'
        return `${start} - ${end}`
      },
    },
    {
      key: 'analytic_account',
      label: 'Analytic Account',
      render: (row) => row.analytic_account_name ?? row.analytic_account?.name ?? row.analytic_account_id ?? '—',
    },
    {
      key: 'responsible',
      label: 'Responsible',
      render: (row) => row.responsible_name ?? row.responsible?.name ?? row.responsible_id ?? '—',
    },
    {
      key: 'amount',
      label: 'Amount',
      render: (row) => formatCurrency(row.committed_amount ?? row.amount),
    },
    {
      key: 'achieved_percentage',
      label: 'Achieved %',
      render: (row) => formatPercent(row.achieved_percentage ?? row.achieved_percent),
    },
    {
      key: 'status',
      label: 'Status',
      render: (row) => <StatusBadge status={toDisplayLabel(BUDGET_STATUS_MAP, String(row.status ?? 'draft').toLowerCase())} />,
    },
  ]

  return (
    <PageShell
      title="Budgets"
      description="Planned spend/revenue by analytic account, tracked against actuals once confirmed."
      actions={<Link to="/budgets/new"><Button>New Budget</Button></Link>}
    >
      <div className="list-toolbar">
        <input
          className="search-input"
          type="text"
          placeholder="Search by name, responsible, or analytic account..."
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

      {loading && <p className="card-empty">Loading budgets...</p>}
      {error && !loading && (
        <div className="form-error-banner">Could not load budgets: {error.message}</div>
      )}
      {!loading && !error && (
        <Table columns={columns} rows={filtered} emptyMessage="No budgets found." />
      )}
    </PageShell>
  )
}
