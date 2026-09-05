"""
TODO: end-to-end test for PO -> Vendor Bill -> Payment, asserting:
  - PO confirmation creates NO journal entry
  - Vendor Bill confirmation creates exactly ONE journal entry
    (Debit Purchase Expense / Credit Creditors)
  - Payment confirmation creates a SEPARATE journal entry
    (Debit Creditors / Credit Bank or Cash)
"""
def test_placeholder():
    assert True
