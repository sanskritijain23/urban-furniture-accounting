from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.journal import Journal


class JournalNotFoundError(Exception):
    pass


class InvalidDefaultAccountError(Exception):
    pass


def _validate_default_account(db: Session, account_id: int) -> None:
    if db.query(Account).filter(Account.id == account_id).first() is None:
        raise InvalidDefaultAccountError(f"default_account_id {account_id} does not exist")


def list_journals(db: Session) -> list[Journal]:
    return db.query(Journal).order_by(Journal.id).all()


def get_journal(db: Session, journal_id: int) -> Journal:
    journal = db.query(Journal).filter(Journal.id == journal_id).first()
    if journal is None:
        raise JournalNotFoundError(f"Journal {journal_id} not found")
    return journal


def create_journal(db: Session, data: dict) -> Journal:
    _validate_default_account(db, data["default_account_id"])

    journal = Journal(**data)
    db.add(journal)
    db.commit()
    db.refresh(journal)
    return journal


def update_journal(db: Session, journal_id: int, data: dict) -> Journal:
    journal = get_journal(db, journal_id)

    if "default_account_id" in data and data["default_account_id"] is not None:
        _validate_default_account(db, data["default_account_id"])

    for field, value in data.items():
        if value is not None:
            setattr(journal, field, value)

    db.commit()
    db.refresh(journal)
    return journal
