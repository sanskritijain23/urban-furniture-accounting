"""
Chart of Accounts (CoA) — the master list of ledger accounts used by
the centralized Accounting Engine.

IMPORTANT: `type` must use the approved AccountType enum exactly as
audited from the MVP mockup (Asset / Liability / Bank / Cash / Capital
/ Income / Expenses / Other Expenses). Do not collapse back to a
generic 5-value enum.

Owned by: Database Developer. This table should be pre-seeded (see
database/seed/seed_data.py) with the standard accounts: Cash, Bank,
Debtors, Creditors, Sales Income, Purchase Expense, Capital.
"""
from sqlalchemy import Column, Integer, String, Enum, DateTime, func

from app.core.database import Base
from app.models.enums import AccountType, AccountStatus


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), unique=True, nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.CONFIRMED)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Account id={self.id} name={self.name} type={self.type}>"
