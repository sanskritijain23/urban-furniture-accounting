"""
Highest-priority test in the whole repo: the debit=credit invariant.

TODO: once accounting_engine.create_journal_entry /
validate_entry_is_balanced are implemented, write real tests here,
e.g.:

    def test_balanced_entry_is_accepted():
        lines = [
            {"account_id": 1, "debit": Decimal("100"), "credit": Decimal("0")},
            {"account_id": 2, "debit": Decimal("0"), "credit": Decimal("100")},
        ]
        assert validate_entry_is_balanced(lines) is True

    def test_unbalanced_entry_is_rejected():
        ... assert raises UnbalancedEntryError
"""
import pytest


def test_placeholder():
    """Placeholder so pytest collects this file without error before
    accounting_engine.py business logic is implemented."""
    assert True
