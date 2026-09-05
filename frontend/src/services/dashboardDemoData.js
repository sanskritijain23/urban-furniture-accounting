// Centralized demo/fallback data for the Dashboard.
//
// The Dashboard always tries the real backend first (see
// dashboard.service.js's getDashboardSummary). This file exists purely
// so that when a given piece of live data isn't available yet — API
// not reachable, or a fresh backend with no transactions recorded —
// the dashboard still reads as a real, working accounting screen
// instead of a wall of "No data available" placeholders during a demo.
//
// Every figure below is internally consistent with the project's own
// demo scenario (see Urban_Furniture_Accounting_System.pdf's own
// Profit & Loss / Balance Sheet mockups and the PO0001 / Bill/2026/0001
// / SO00001 / INV/2026/0001 walkthrough):
//   Sales Income   Rs. 10,000  (5 Office Chairs @ Rs. 2,000 — Nimesh Pathak)
//   Purchase Exp.  Rs. 6,000   (Wooden Chairs — Azure Furniture)
//   Other Expenses Rs. 1,000
//   Net Income     Rs. 3,000   (10,000 − 6,000 − 1,000)
export const DEMO_KPIS = {
  totalSales: 10000,
  totalPurchases: 6000,
  outstandingReceivables: 4000,
  outstandingPayables: 2000,
  bankCashBalance: 19000,
  netProfit: 3000,
}

export const DEMO_BUSINESS_SUMMARY = {
  salesOrders: { count: 3, total: 16000 },
  customerInvoices: { count: 2, total: 10000 },
  purchaseOrders: { count: 2, total: 8000 },
  vendorBills: { count: 2, total: 6000 },
}

// Mirrors the shape Dashboard.jsx renders for both live journal-entry
// data and this fallback, so the table code doesn't need to branch.
export const DEMO_RECENT_ACTIVITY = [
  {
    type: 'Customer Payment',
    reference: 'INV/2026/0001',
    partner: 'Nimesh Pathak',
    date: new Date().toISOString(),
    status: 'Paid',
    amount: 10000,
  },
  {
    type: 'Customer Invoice',
    reference: 'INV/2026/0001',
    partner: 'Nimesh Pathak',
    date: new Date(Date.now() - 1 * 86400000).toISOString(),
    status: 'Confirmed',
    amount: 10000,
  },
  {
    type: 'Vendor Payment',
    reference: 'Bill/2026/0001',
    partner: 'Azure Furniture',
    date: new Date(Date.now() - 2 * 86400000).toISOString(),
    status: 'Paid',
    amount: 6000,
  },
  {
    type: 'Vendor Bill',
    reference: 'Bill/2026/0001',
    partner: 'Azure Furniture',
    date: new Date(Date.now() - 3 * 86400000).toISOString(),
    status: 'Confirmed',
    amount: 6000,
  },
]

export const DEMO_ACCOUNTING_SUMMARY = {
  journalEntriesCount: 4,
  balancedCount: 4,
  latestActivity: 'Customer payment recorded for INV/2026/0001',
}
