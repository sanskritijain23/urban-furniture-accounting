// Route: /dashboard
// Role allowed: admin, accountant
//
// Pulls together the figures a business owner/accountant actually
// wants to see at a glance: KPI totals, per-module counts, the last
// few accounting transactions, quick links into the create flows, and
// a one-line accounting health check. All computation lives in
// services/dashboard.service.js, which reuses the exact same
// list*/get* functions every other page already calls — this file only
// renders what comes back.
import { useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth.jsx'
import { useFetch } from '../../hooks/useFetch.js'
import { getDashboardSummary } from '../../services/dashboard.service.js'
import PageShell from '../../components/common/PageShell.jsx'
import Button from '../../components/common/Button.jsx'
import Table from '../../components/common/Table.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import { formatCurrency, formatDate } from '../../utils/formatters.js'

const CURRENT_YEAR = new Date().getFullYear()

const QUICK_ACTIONS = [
  { label: 'Create Purchase Order', to: '/purchases/orders/new' },
  { label: 'Create Vendor Bill', to: '/purchases/orders', hint: 'via a confirmed PO' },
  { label: 'Create Sales Order', to: '/sales/orders/new' },
  { label: 'Create Customer Invoice', to: '/sales/orders', hint: 'via a confirmed SO' },
  { label: 'Manual Journal Entry', to: '/journal-entries/new' },
  { label: 'View Reports', to: '/reports/balance-sheet' },
]

function KpiCard({ label, value, tone }) {
  return (
    <div className="card kpi-card">
      <div className="kpi-label">{label}</div>
      <div className={`kpi-value${tone ? ` kpi-value-${tone}` : ''}`}>{formatCurrency(value)}</div>
    </div>
  )
}

function SummaryCard({ label, to, count, total }) {
  return (
    <Link to={to} className="card card-link">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{count}</div>
      <div className="kpi-sub">{formatCurrency(total)} total</div>
    </Link>
  )
}

export default function Dashboard() {
  const { user } = useAuth()

  const fetchSummary = useCallback(() => getDashboardSummary(CURRENT_YEAR), [])
  const { data, loading, error } = useFetch(fetchSummary, [])

  const displayName = user?.name || user?.loginId || 'there'
  const today = formatDate(new Date().toISOString())

  const kpis = data?.kpis
  const businessSummary = data?.businessSummary
  const recentActivity = data?.recentActivity ?? []
  const accountingSummary = data?.accountingSummary

  const activityColumns = [
    { key: 'type', label: 'Type' },
    { key: 'reference', label: 'Reference' },
    { key: 'partner', label: 'Partner' },
    { key: 'date', label: 'Date', render: (row) => formatDate(row.date) },
    {
      key: 'status',
      label: 'Status',
      render: (row) => <StatusBadge status={row.status} />,
    },
    {
      key: 'amount',
      label: 'Amount',
      render: (row) => formatCurrency(row.amount),
    },
  ]

  return (
    <PageShell
      title="Dashboard"
      description={`Welcome back, ${displayName}. Today is ${today}.`}
    >
      {loading && <p className="card-empty">Loading dashboard...</p>}
      {error && !loading && (
        <div className="form-error-banner">Could not load dashboard data: {error.message}</div>
      )}

      {!loading && data && (
        <>
          {data.usingDemoData && (
            <p className="demo-data-note">
              No live transactions found yet — showing sample figures from the standard demo
              scenario (Azure Furniture / Nimesh Pathak) so the layout reflects a working system.
            </p>
          )}
          {!data.usingDemoData && data.partialDemoFallback && (
            <p className="demo-data-note">
              Some figures below (Bank/Cash balance and/or Recent Activity) use sample data
              because that endpoint hasn't returned live results yet.
            </p>
          )}

          {/* KPI Summary */}
          <div className="dashboard-section">
            <h3 className="dashboard-section-title">Key Metrics</h3>
            <div className="dashboard-grid">
              <KpiCard label="Total Sales Revenue" value={kpis.totalSales} />
              <KpiCard label="Total Purchase Expense" value={kpis.totalPurchases} />
              <KpiCard label="Outstanding Receivables" value={kpis.outstandingReceivables} />
              <KpiCard label="Outstanding Payables" value={kpis.outstandingPayables} />
              <KpiCard label="Bank / Cash Balance" value={kpis.bankCashBalance} />
              <KpiCard
                label="Net Profit"
                value={kpis.netProfit}
                tone={kpis.netProfit >= 0 ? 'positive' : 'negative'}
              />
            </div>
          </div>

          {/* Business Summary */}
          <div className="dashboard-section">
            <h3 className="dashboard-section-title">Business Summary</h3>
            <div className="dashboard-grid">
              <SummaryCard
                label="Sales Orders"
                to="/sales/orders"
                count={businessSummary.salesOrders.count}
                total={businessSummary.salesOrders.total}
              />
              <SummaryCard
                label="Customer Invoices"
                to="/sales/invoices"
                count={businessSummary.customerInvoices.count}
                total={businessSummary.customerInvoices.total}
              />
              <SummaryCard
                label="Purchase Orders"
                to="/purchases/orders"
                count={businessSummary.purchaseOrders.count}
                total={businessSummary.purchaseOrders.total}
              />
              <SummaryCard
                label="Vendor Bills"
                to="/purchases/bills"
                count={businessSummary.vendorBills.count}
                total={businessSummary.vendorBills.total}
              />
            </div>
          </div>

          {/* Recent Activity */}
          <div className="dashboard-section">
            <h3 className="dashboard-section-title">Recent Activity</h3>
            <Table columns={activityColumns} rows={recentActivity} emptyMessage="No recent transactions." />
          </div>

          {/* Quick Actions */}
          <div className="dashboard-section">
            <h3 className="dashboard-section-title">Quick Actions</h3>
            <div className="quick-actions-grid">
              {QUICK_ACTIONS.map((action) => (
                <Link key={action.to + action.label} to={action.to}>
                  <Button type="button" variant="secondary" block>
                    {action.label}
                    {action.hint && <span className="quick-action-hint"> ({action.hint})</span>}
                  </Button>
                </Link>
              ))}
            </div>
          </div>

          {/* Accounting Summary */}
          <div className="dashboard-section">
            <h3 className="dashboard-section-title">Accounting Summary</h3>
            <div className="detail-card">
              <div className="detail-grid">
                <div>
                  <div className="detail-field-label">Journal Entries</div>
                  <div className="detail-field-value">{accountingSummary.journalEntriesCount}</div>
                </div>
                <div>
                  <div className="detail-field-label">Balanced Entries</div>
                  <div className="detail-field-value">
                    {accountingSummary.balancedCount} / {accountingSummary.journalEntriesCount}
                  </div>
                </div>
                <div>
                  <div className="detail-field-label">Latest Activity</div>
                  <div className="detail-field-value">{accountingSummary.latestActivity}</div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </PageShell>
  )
}
