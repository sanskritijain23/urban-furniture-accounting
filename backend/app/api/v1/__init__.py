"""
Aggregates all v1 API routers into a single `api_router` that
main.py mounts under the /api/v1 prefix.

When adding a new route module, register it here — this is the one
shared file everyone touches, kept deliberately tiny (one line per
module) to minimize merge conflicts.
"""
from fastapi import APIRouter

from app.api.v1 import (
    auth, users, contacts, products, accounts, journals, journal_entries,
    purchase_orders, vendor_bills, sales_orders, customer_invoices,
    payments, analytic_accounts, budgets, reports,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(contacts.router)
api_router.include_router(products.router)
api_router.include_router(accounts.router)
api_router.include_router(journals.router)
api_router.include_router(journal_entries.router)
api_router.include_router(purchase_orders.router)
api_router.include_router(vendor_bills.router)
api_router.include_router(sales_orders.router)
api_router.include_router(customer_invoices.router)
api_router.include_router(payments.router)
api_router.include_router(analytic_accounts.router)
api_router.include_router(budgets.router)
api_router.include_router(reports.router)
