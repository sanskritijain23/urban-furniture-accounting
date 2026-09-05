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

// Backend AnalyticAccountType is singular ("expense"), not "expenses".
export const ANALYTIC_TYPE_MAP = {
  Income: 'income',
  Expenses: 'expense',
}

export const CONTACT_TYPE_OPTIONS = Object.keys(CONTACT_TYPE_MAP)
export const PRODUCT_TYPE_OPTIONS = Object.keys(PRODUCT_TYPE_MAP)
export const ACCOUNT_TYPE_OPTIONS = Object.keys(ACCOUNT_TYPE_MAP)
export const JOURNAL_TYPE_OPTIONS = Object.keys(JOURNAL_TYPE_MAP)
export const ANALYTIC_TYPE_OPTIONS = Object.keys(ANALYTIC_TYPE_MAP)

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
