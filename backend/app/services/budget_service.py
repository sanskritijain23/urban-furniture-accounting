"""
Budget business logic — lifecycle management (Draft -> Confirmed ->
Revised -> Cancelled) and the computed achieved-amount fields.

IMPORTANT: this module never writes to JournalEntry/JournalEntryLine.
It reads actuals via ledger_service.get_actuals_for_analytic_account.
"""
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session


def create_budget(db: Session, payload):
    """TODO: persist a new Budget with status=DRAFT."""
    raise NotImplementedError


def confirm_budget(db: Session, budget_id: int):
    """TODO: set status -> CONFIRMED. Achieved fields become visible
    only once confirmed (per the audited mockup rule)."""
    raise NotImplementedError


def revise_budget(db: Session, budget_id: int, new_committed_amount: Decimal):
    """
    TODO (MUST HAVE — audited requirement): creates a NEW Budget row
    with revision_of_id pointing back to the original, status=REVISED
    on... actually per the mockup: the OLD budget is marked/linked and
    a NEW confirmed budget is created carrying the revised amount.
    Both records remain visible/linked for audit purposes. Do not
    mutate the original committed_amount in place.
    """
    raise NotImplementedError


def cancel_budget(db: Session, budget_id: int):
    """TODO: set status -> CANCELLED. Archives the budget."""
    raise NotImplementedError


def compute_achieved(db: Session, budget_id: int) -> dict:
    """
    TODO: use ledger_service.get_actuals_for_analytic_account() to
    compute:
        achieved_amount      = actuals for this budget's analytic
                                account + period
        achieved_percentage  = achieved_amount / committed_amount * 100
        amount_to_achieve    = committed_amount - achieved_amount
    Returns a dict merged into BudgetResponse — these are NEVER stored
    columns.
    """
    raise NotImplementedError


def check_budget_warning(db: Session, analytic_account_id: int, additional_amount: Decimal) -> Optional[str]:
    """
    TODO (NON-BLOCKING warning, not a hard validation error): if
    adding `additional_amount` to the current actuals for this
    analytic account would exceed the relevant Budget's
    committed_amount, return a warning message string; otherwise
    return None. Called from purchase_service.py at PO/Bill confirm
    time. Must never raise/block the transaction.
    """
    raise NotImplementedError
