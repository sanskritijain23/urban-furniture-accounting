"""
Budget business logic -- lifecycle management (Draft -> Confirmed ->
Revised -> Cancelled) and the computed achieved-amount fields.

IMPORTANT: this module never writes to JournalEntry/JournalEntryLine.
It reads actuals via ledger_service.get_actuals_for_analytic_account.
"""
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.enums import BudgetStatus
from app.services import ledger_service


class BudgetNotFoundError(Exception):
    pass


class InvalidBudgetTransitionError(Exception):
    pass


def _get_budget(db: Session, budget_id: int) -> Budget:
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if budget is None:
        raise BudgetNotFoundError(f"Budget {budget_id} not found")
    return budget


def list_budgets(db: Session) -> list[Budget]:
    return db.query(Budget).order_by(Budget.id).all()


def get_budget(db: Session, budget_id: int) -> Budget:
    return _get_budget(db, budget_id)


def create_budget(db: Session, payload) -> Budget:
    budget = Budget(
        name=payload.name,
        period_start=payload.period_start,
        period_end=payload.period_end,
        responsible_id=payload.responsible_id,
        analytic_account_id=payload.analytic_account_id,
        committed_amount=payload.committed_amount,
        status=BudgetStatus.DRAFT,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def confirm_budget(db: Session, budget_id: int) -> Budget:
    budget = _get_budget(db, budget_id)
    if budget.status != BudgetStatus.DRAFT:
        raise InvalidBudgetTransitionError(
            f"Only DRAFT budgets can be confirmed (current status: {budget.status.value})"
        )
    budget.status = BudgetStatus.CONFIRMED
    db.commit()
    db.refresh(budget)
    return budget


def revise_budget(db: Session, budget_id: int, new_committed_amount: Decimal) -> Budget:
    """
    Creates a NEW Budget row with revision_of_id pointing back to the
    original, status=CONFIRMED, carrying the revised amount. The
    ORIGINAL budget is marked status=REVISED (not deleted/mutated) so
    both remain visible/linked for audit purposes.
    """
    original = _get_budget(db, budget_id)
    if original.status != BudgetStatus.CONFIRMED:
        raise InvalidBudgetTransitionError(
            f"Only CONFIRMED budgets can be revised (current status: {original.status.value})"
        )

    revised = Budget(
        name=original.name,
        period_start=original.period_start,
        period_end=original.period_end,
        responsible_id=original.responsible_id,
        analytic_account_id=original.analytic_account_id,
        committed_amount=new_committed_amount,
        status=BudgetStatus.CONFIRMED,
        revision_of_id=original.id,
    )
    original.status = BudgetStatus.REVISED
    db.add(revised)
    db.commit()
    db.refresh(revised)
    return revised


def cancel_budget(db: Session, budget_id: int) -> Budget:
    budget = _get_budget(db, budget_id)
    if budget.status == BudgetStatus.CANCELLED:
        raise InvalidBudgetTransitionError("Budget is already cancelled")
    budget.status = BudgetStatus.CANCELLED
    db.commit()
    db.refresh(budget)
    return budget


def compute_achieved(db: Session, budget_id: int) -> dict:
    """
    achieved_amount     = actuals for this budget's analytic account + period
    achieved_percentage = achieved_amount / committed_amount * 100
    amount_to_achieve   = committed_amount - achieved_amount
    Returns a dict merged into BudgetResponse -- these are NEVER stored columns.
    """
    budget = _get_budget(db, budget_id)

    achieved_amount = ledger_service.get_actuals_for_analytic_account(
        db, budget.analytic_account_id, budget.period_start, budget.period_end
    )
    if budget.committed_amount and budget.committed_amount != 0:
        achieved_percentage = (achieved_amount / budget.committed_amount) * Decimal("100")
    else:
        achieved_percentage = Decimal("0")
    amount_to_achieve = budget.committed_amount - achieved_amount

    return {
        "achieved_amount": achieved_amount,
        "achieved_percentage": achieved_percentage,
        "amount_to_achieve": amount_to_achieve,
    }


def check_budget_warning(db: Session, analytic_account_id: int, additional_amount: Decimal) -> Optional[str]:
    """
    NON-BLOCKING warning check. If adding `additional_amount` to the
    current actuals for this analytic account would exceed the active
    (CONFIRMED) Budget's committed_amount, return a warning message
    string; otherwise return None. The "active" budget is the one
    whose period covers the current date. Never raises/blocks.
    """
    from datetime import date

    if analytic_account_id is None:
        return None

    today = date.today()
    active_budget = (
        db.query(Budget)
        .filter(
            Budget.analytic_account_id == analytic_account_id,
            Budget.status == BudgetStatus.CONFIRMED,
            Budget.period_start <= today,
            Budget.period_end >= today,
        )
        .order_by(Budget.id.desc())
        .first()
    )
    if active_budget is None:
        return None

    current_actual = ledger_service.get_actuals_for_analytic_account(
        db, analytic_account_id, active_budget.period_start, active_budget.period_end
    )
    projected = current_actual + additional_amount

    if projected > active_budget.committed_amount:
        return (
            f"Budget '{active_budget.name}' exceeded: committed "
            f"{active_budget.committed_amount}, projected usage {projected}."
        )
    return None
