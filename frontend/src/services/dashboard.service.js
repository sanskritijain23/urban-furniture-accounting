// Aggregates data for the /dashboard screen. This is the ONLY new
// "service"-shaped module added for the dashboard — it does no fetching
// of its own; it just calls the exact same functions every other page
// already uses (sales.service, purchase.service, journalEntry.service,
// report.service) and reduces the results into the shapes Dashboard.jsx
// renders.
//
// Each of the four document lists (Sales Orders / Customer Invoices /
// Purchase Orders / Vendor Bills) plus Journal Entries and the two
// report endpoints are fetched in parallel and tolerated independently
// via Promise.allSettled — one slow/broken endpoint should never blank
// out the whole dashboard.
//
// If, taken together, there's no real transaction data yet (nothing
// fetched successfully, or everything came back empty — e.g. a fresh/
// unseeded backend), the whole dashboard falls back to the fixed demo
// scenario in dashboardDemoData.js instead of rendering an all-zero,
// "No data available" screen. `usingDemoData` is returned so the UI can
// show a small, honest "sample data" note instead of silently passing
// fabricated numbers off as live figures.
import { listSalesOrders, listCustomerInvoices } from './sales.service.js'
import { listPurchaseOrders, listVendorBills } from './purchase.service.js'
import { listJournalEntries } from './journalEntry.service.js'
import { getBalanceSheet, getProfitAndLoss } from './report.service.js'
import { JOURNAL_ENTRY_STATUS_MAP, toDisplayLabel } from '../utils/enumMap.js'
import {
  DEMO_KPIS,
  DEMO_BUSINESS_SUMMARY,
  DEMO_RECENT_ACTIVITY,
  DEMO_ACCOUNTING_SUMMARY,
} from './dashboardDemoData.js'

function settledValue(result, fallback) {
  return result.status === 'fulfilled' && result.value != null ? result.value : fallback
}

function docTotal(doc) {
  return Number(doc.total_amount ?? 0)
}

// Outstanding balance for one Vendor Bill / Customer Invoice: use the
// backend's own due/balance field when present, otherwise assume a
// confirmed-but-not-paid doc is fully outstanding and anything else
// (draft, paid, cancelled) contributes nothing.
function docAmountDue(doc) {
  const explicitDue = doc.amount_due ?? doc.balance_due
  if (explicitDue != null) return Number(explicitDue)
  const status = String(doc.status ?? 'draft').toLowerCase()
  return status === 'confirmed' ? docTotal(doc) : 0
}

function summarize(list) {
  return {
    count: list.length,
    total: list.reduce((sum, doc) => sum + docTotal(doc), 0),
  }
}

// Same "explicit totals, fall back to summing lines" convention used by
// JournalEntryList.jsx / JournalEntryDetail.jsx.
function entryTotals(entry) {
  const lines = entry.lines ?? []
  const debit = entry.total_debit ?? entry.debit_total
    ?? lines.reduce((sum, l) => sum + Number(l.debit ?? 0), 0)
  const credit = entry.total_credit ?? entry.credit_total
    ?? lines.reduce((sum, l) => sum + Number(l.credit ?? 0), 0)
  return { debit: Number(debit) || 0, credit: Number(credit) || 0 }
}

function entryToActivityRow(entry) {
  const { debit, credit } = entryTotals(entry)
  return {
    type: entry.journal_name ?? entry.journal?.name ?? 'Journal Entry',
    reference: entry.entry_number ?? `#${entry.id}`,
    partner: entry.partner_name ?? entry.partner?.name ?? '—',
    date: entry.date ?? entry.entry_date,
    status: toDisplayLabel(JOURNAL_ENTRY_STATUS_MAP, String(entry.status ?? 'draft').toLowerCase()),
    amount: Math.max(debit, credit),
  }
}

// Bank/Cash balance isn't its own endpoint — reuse the Balance Sheet's
// Assets section (already fetched for the KPI's net-profit figure) and
// sum whichever rows look like a bank/cash account, the same way every
// other page in this app matches on the field names it's given rather
// than assuming an exact backend contract.
function bankCashFromBalanceSheet(balanceSheet) {
  const assets = balanceSheet?.assets ?? []
  const matches = assets.filter((row) =>
    /bank|cash/i.test(row.account_name ?? row.name ?? '')
  )
  if (matches.length === 0) return null
  return matches.reduce((sum, row) => sum + Number(row.balance ?? row.amount ?? 0), 0)
}

export async function getDashboardSummary(year = new Date().getFullYear()) {
  const [soRes, ciRes, poRes, vbRes, jeRes, bsRes, plRes] = await Promise.allSettled([
    listSalesOrders(),
    listCustomerInvoices(),
    listPurchaseOrders(),
    listVendorBills(),
    listJournalEntries(),
    getBalanceSheet(year),
    getProfitAndLoss(year),
  ])

  const salesOrders = settledValue(soRes, [])
  const customerInvoices = settledValue(ciRes, [])
  const purchaseOrders = settledValue(poRes, [])
  const vendorBills = settledValue(vbRes, [])
  const journalEntries = settledValue(jeRes, [])
  const balanceSheet = settledValue(bsRes, null)
  const profitAndLoss = settledValue(plRes, null)

  const hasRealTransactions =
    salesOrders.length > 0 ||
    customerInvoices.length > 0 ||
    purchaseOrders.length > 0 ||
    vendorBills.length > 0

  if (!hasRealTransactions) {
    return {
      usingDemoData: true,
      kpis: DEMO_KPIS,
      businessSummary: DEMO_BUSINESS_SUMMARY,
      recentActivity: DEMO_RECENT_ACTIVITY,
      accountingSummary: DEMO_ACCOUNTING_SUMMARY,
    }
  }

  const businessSummary = {
    salesOrders: summarize(salesOrders),
    customerInvoices: summarize(customerInvoices),
    purchaseOrders: summarize(purchaseOrders),
    vendorBills: summarize(vendorBills),
  }

  const recognizedStatuses = ['confirmed', 'paid']
  const totalSales = customerInvoices
    .filter((inv) => recognizedStatuses.includes(String(inv.status ?? '').toLowerCase()))
    .reduce((sum, inv) => sum + docTotal(inv), 0)
  const totalPurchases = vendorBills
    .filter((bill) => recognizedStatuses.includes(String(bill.status ?? '').toLowerCase()))
    .reduce((sum, bill) => sum + docTotal(bill), 0)

  const outstandingReceivables = customerInvoices.reduce((sum, inv) => sum + docAmountDue(inv), 0)
  const outstandingPayables = vendorBills.reduce((sum, bill) => sum + docAmountDue(bill), 0)

  const bankCashBalance = bankCashFromBalanceSheet(balanceSheet) ?? DEMO_KPIS.bankCashBalance
  const netProfit = profitAndLoss?.net_income != null
    ? Number(profitAndLoss.net_income)
    : totalSales - totalPurchases

  const kpis = {
    totalSales,
    totalPurchases,
    outstandingReceivables,
    outstandingPayables,
    bankCashBalance,
    netProfit,
  }

  const recentActivity = journalEntries.length > 0
    ? [...journalEntries]
      .sort((a, b) => new Date(b.date ?? b.entry_date ?? 0) - new Date(a.date ?? a.entry_date ?? 0))
      .slice(0, 5)
      .map(entryToActivityRow)
    : DEMO_RECENT_ACTIVITY

  const accountingSummary = journalEntries.length > 0
    ? {
      journalEntriesCount: journalEntries.length,
      balancedCount: journalEntries.filter((entry) => {
        const { debit, credit } = entryTotals(entry)
        return Math.abs(debit - credit) < 0.01
      }).length,
      latestActivity: recentActivity[0]
        ? `${recentActivity[0].type} — ${recentActivity[0].reference}`
        : DEMO_ACCOUNTING_SUMMARY.latestActivity,
    }
    : DEMO_ACCOUNTING_SUMMARY

  return {
    // Only the pieces that couldn't be computed from real transactions
    // (bank balance and/or the activity feed) may still be demo values
    // even though hasRealTransactions is true — surfaced so the UI can
    // caveat those specific cards rather than the whole page.
    usingDemoData: false,
    partialDemoFallback: bankCashFromBalanceSheet(balanceSheet) == null || journalEntries.length === 0,
    kpis,
    businessSummary,
    recentActivity,
    accountingSummary,
  }
}
