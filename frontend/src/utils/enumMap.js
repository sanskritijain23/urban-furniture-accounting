// Shared UI-label <-> backend-enum-value conversion.
//
// The Chart of Accounts mockup (and the rest of the forms built from it)
// show Title Case labels like "Customer" or "Other Expenses", but the
// FastAPI backend's Pydantic enums expect lower snake_case values such
// as "customer" or "other_expenses". This file is the single place that
// knows both sides of each mapping so individual pages/forms don't have
// to duplicate (and risk drifting on) the conversion logic.
//
// Usage:
//   import { toBackendEnum, toDisplayLabel, CONTACT_TYPE_OPTIONS } from '.../utils/enumMap.js'
//   toBackendEnum(CONTACT_TYPE_MAP, 'Customer') -> 'customer'
//   toDisplayLabel(CONTACT_TYPE_MAP, 'customer') -> 'Customer'

export const CONTACT_TYPE_MAP = {
  Customer: 'customer',
  Vendor: 'vendor',
  Both: 'both',
}

export const PRODUCT_TYPE_MAP = {
  Goods: 'goods',
  Service: 'service',
  Combo: 'combo',
}

export const ACCOUNT_TYPE_MAP = {
  Asset: 'asset',
  Liability: 'liability',
  Bank: 'bank',
  Cash: 'cash',
  Capital: 'capital',
  Income: 'income',
  Expenses: 'expenses',
  'Other Expenses': 'other_expenses',
}

export const JOURNAL_TYPE_MAP = {
  Sales: 'sales',
  Purchase: 'purchase',
  Bank: 'bank',
  Cash: 'cash',
}

// User role, set by an admin on the Create User screen (see
// pages/auth/AdminCreateUser.jsx) and read back from GET /users/me by
// hooks/useAuth.jsx to drive role-based route protection. Signup.jsx
// always creates 'accountant' users server-side; only an admin can
// create an 'admin' or 'contact' login here.
export const USER_ROLE_MAP = {
  Admin: 'admin',
  Accountant: 'accountant',
  Contact: 'contact',
}

// Backend AnalyticAccountType is singular ("expense"), not "expenses".
export const ANALYTIC_TYPE_MAP = {
  Income: 'income',
  Expenses: 'expense',
}

// Draft/Confirmed/etc. status shown on Purchase Orders, Vendor Bills,
// Sales Orders and Customer Invoices. Assumed lower-case backend
// values, consistent with every other enum in this file — adjust if
// the API returns something else.
export const DOC_STATUS_MAP = {
  Draft: 'draft',
  Confirmed: 'confirmed',
  Paid: 'paid',
  Cancelled: 'cancelled',
}

// Journal Entry status. Assumed lower-case backend values (draft while
// the line grid is editable, posted once /journal-entries/{id}/post has
// been called, cancelled otherwise), consistent with every other enum
// in this file — adjust if the API returns something else.
export const JOURNAL_ENTRY_STATUS_MAP = {
  Draft: 'draft',
  Posted: 'posted',
  Cancelled: 'cancelled',
}

// Budget status. Draft while still editable/unconfirmed, Confirmed once
// locked in and tracked against actuals, Revised once a newer linked
// budget has replaced it (see budget.service.js reviseBudget), Cancelled
// otherwise. Assumed lower-case backend values, consistent with every
// other enum in this file — adjust if the API returns something else.
export const BUDGET_STATUS_MAP = {
  Draft: 'draft',
  Confirmed: 'confirmed',
  Revised: 'revised',
  Cancelled: 'cancelled',
}

export const CONTACT_TYPE_OPTIONS = Object.keys(CONTACT_TYPE_MAP)
export const PRODUCT_TYPE_OPTIONS = Object.keys(PRODUCT_TYPE_MAP)
export const ACCOUNT_TYPE_OPTIONS = Object.keys(ACCOUNT_TYPE_MAP)
export const JOURNAL_TYPE_OPTIONS = Object.keys(JOURNAL_TYPE_MAP)
export const USER_ROLE_OPTIONS = Object.keys(USER_ROLE_MAP)
export const ANALYTIC_TYPE_OPTIONS = Object.keys(ANALYTIC_TYPE_MAP)
export const DOC_STATUS_OPTIONS = Object.keys(DOC_STATUS_MAP)
export const BUDGET_STATUS_OPTIONS = Object.keys(BUDGET_STATUS_MAP)
export const JOURNAL_ENTRY_STATUS_OPTIONS = Object.keys(JOURNAL_ENTRY_STATUS_MAP)

/** UI label ("Customer") -> backend enum value ("customer"). */
export function toBackendEnum(map, label) {
  return map[label] ?? label
}

/** backend enum value ("customer") -> UI label ("Customer").
 * Falls back to the raw value if it isn't recognised, so unexpected
 * backend data still renders instead of disappearing. */
export function toDisplayLabel(map, value) {
  const entry = Object.entries(map).find(([, v]) => v === value)
  return entry ? entry[0] : value
}
