from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.account import Account


class DuplicateAccountNameError(Exception):
    pass


class AccountNotFoundError(Exception):
    pass


def list_accounts(db: Session) -> list[Account]:
    return db.query(Account).order_by(Account.id).all()


def get_account(db: Session, account_id: int) -> Account:
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise AccountNotFoundError(f"Account {account_id} not found")
    return account


def create_account(db: Session, data: dict) -> Account:
    existing = db.query(Account).filter(Account.name == data["name"]).first()
    if existing is not None:
        raise DuplicateAccountNameError(f"account '{data['name']}' already exists")

    account = Account(**data)
    db.add(account)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateAccountNameError(f"account '{data['name']}' already exists") from exc
    db.refresh(account)
    return account


def update_account(db: Session, account_id: int, data: dict) -> Account:
    """Also used for the Confirm/Archive status-transition actions from
    the mockup: PUT with just {"status": "archived"} etc."""
    account = get_account(db, account_id)

    new_name = data.get("name")
    if new_name and new_name != account.name:
        existing = db.query(Account).filter(Account.name == new_name).first()
        if existing is not None:
            raise DuplicateAccountNameError(f"account '{new_name}' already exists")

    for field, value in data.items():
        if value is not None:
            setattr(account, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateAccountNameError("account name already exists") from exc
    db.refresh(account)
    return account
