"""
JournalEntry + JournalEntryLine — the centralized accounting record.

CRITICAL RULE (see app/services/accounting_engine.py):
Only accounting_engine.py is permitted to create or post rows in
these two tables. No other service (purchase, sales, payment, report)
may write to JournalEntry / JournalEntryLine directly.

A JournalEntry may optionally reference the business transaction that
triggered it via (source_type, source_id) — a lightweight polymorphic
reference rather than a formal DB foreign key, since source_type can
point to different tables (vendor_bills, customer_invoices, payments)
or be manual with no source at all.

Constraint (enforced in accounting_engine.py, not at the DB layer,
since it spans multiple rows):
    SUM(line.debit for line in entry.lines) == SUM(line.credit for line in entry.lines)
A JournalEntry cannot transition to POSTED unless this holds.

Owned by: Database Developer.
"""
from sqlalchemy import (
    Column, Integer, String, Numeric, Enum, ForeignKey, Date, DateTime, func
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import JournalEntryStatus, JournalEntrySourceType


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)

    journal_id = Column(Integer, ForeignKey("journals.id"), nullable=False)
    accounting_date = Column(Date, nullable=False)

    status = Column(Enum(JournalEntryStatus), nullable=False, default=JournalEntryStatus.DRAFT)

    # Polymorphic reference back to the originating transaction.
    # source_type = "manual" means there is no originating transaction.
    source_type = Column(Enum(JournalEntrySourceType), nullable=False,
                          default=JournalEntrySourceType.MANUAL)
    source_id = Column(Integer, nullable=True)

    reference_no = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    journal = relationship("Journal", back_populates="journal_entries")
    lines = relationship("JournalEntryLine", back_populates="journal_entry",
                          cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<JournalEntry id={self.id} status={self.status} source={self.source_type}>"


class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"

    id = Column(Integer, primary_key=True, index=True)

    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)

    # Exactly one of debit/credit should be non-zero per line
    # (enforced in accounting_engine.py).
    debit = Column(Numeric(12, 2), nullable=False, default=0)
    credit = Column(Numeric(12, 2), nullable=False, default=0)

    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account")
    partner = relationship("Contact")

    def __repr__(self) -> str:
        return f"<JournalEntryLine id={self.id} account_id={self.account_id} debit={self.debit} credit={self.credit}>"
