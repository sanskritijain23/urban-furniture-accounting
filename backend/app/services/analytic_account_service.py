from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.analytic_account import AnalyticAccount


class DuplicateAnalyticAccountNameError(Exception):
    pass


class AnalyticAccountNotFoundError(Exception):
    pass


class AnalyticAccountInUseError(Exception):
    pass


def list_analytic_accounts(db: Session) -> list[AnalyticAccount]:
    return db.query(AnalyticAccount).order_by(AnalyticAccount.id).all()


def get_analytic_account(db: Session, analytic_account_id: int) -> AnalyticAccount:
    account = db.query(AnalyticAccount).filter(AnalyticAccount.id == analytic_account_id).first()
    if account is None:
        raise AnalyticAccountNotFoundError(f"Analytic account {analytic_account_id} not found")
    return account


def create_analytic_account(db: Session, data: dict) -> AnalyticAccount:
    existing = db.query(AnalyticAccount).filter(AnalyticAccount.name == data["name"]).first()
    if existing is not None:
        raise DuplicateAnalyticAccountNameError(f"analytic account '{data['name']}' already exists")

    account = AnalyticAccount(**data)
    db.add(account)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateAnalyticAccountNameError(
            f"analytic account '{data['name']}' already exists"
        ) from exc
    db.refresh(account)
    return account


def update_analytic_account(db: Session, analytic_account_id: int, data: dict) -> AnalyticAccount:
    account = get_analytic_account(db, analytic_account_id)

    new_name = data.get("name")
    if new_name and new_name != account.name:
        existing = db.query(AnalyticAccount).filter(AnalyticAccount.name == new_name).first()
        if existing is not None:
            raise DuplicateAnalyticAccountNameError(f"analytic account '{new_name}' already exists")

    for field, value in data.items():
        if value is not None:
            setattr(account, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateAnalyticAccountNameError("analytic account name already exists") from exc
    db.refresh(account)
    return account


def delete_analytic_account(db: Session, analytic_account_id: int) -> None:
    account = get_analytic_account(db, analytic_account_id)

    if account.budgets:
        raise AnalyticAccountInUseError(
            f"analytic account {analytic_account_id} is used by existing budgets"
        )

    db.delete(account)
    db.commit()
