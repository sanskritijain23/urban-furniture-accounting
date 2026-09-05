"""
TODO: end-to-end test for SO -> Customer Invoice -> Payment, asserting:
  - SO confirmation creates NO journal entry
  - Customer Invoice confirmation creates exactly ONE journal entry
    (Debit Debtors / Credit Sales Income)
  - Payment confirmation creates a SEPARATE journal entry
    (Debit Bank or Cash / Credit Debtors)
"""
def test_placeholder():
    assert True
