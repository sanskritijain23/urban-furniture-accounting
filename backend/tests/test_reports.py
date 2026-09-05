"""
Report tests: Balance Sheet, Profit & Loss, Budget Report -- all
derived from posted Journal Entries only (never hard-coded totals).
"""
from decimal import Decimal

BASE = "/api/v1"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _run_full_purchase_and_sale(client, token, seeded_accounting, year="2026"):
    vendor_id = seeded_accounting["vendor_id"]
    customer_id = seeded_accounting["customer_id"]
    product_id = seeded_accounting["product_id"]

    po = client.post(
        f"{BASE}/purchase-orders/", headers=_auth(token),
        json={"vendor_id": vendor_id, "po_date": f"{year}-06-01",
              "lines": [{"product_id": product_id, "qty": "3", "unit_price": "1000.00"}]},
    ).json()
    client.post(f"{BASE}/purchase-orders/{po['id']}/confirm", headers=_auth(token))
    bill = client.post(
        f"{BASE}/purchase-orders/{po['id']}/create-bill", headers=_auth(token),
        json={"vendor_id": vendor_id, "bill_date": f"{year}-06-02",
              "lines": [{"product_id": product_id, "qty": "3", "unit_price": "1000.00"}]},
    ).json()
    client.post(f"{BASE}/vendor-bills/{bill['id']}/confirm", headers=_auth(token))

    so = client.post(
        f"{BASE}/sales-orders/", headers=_auth(token),
        json={"customer_id": customer_id, "so_date": f"{year}-06-10",
              "lines": [{"product_id": product_id, "qty": "2", "unit_price": "2500.00"}]},
    ).json()
    client.post(f"{BASE}/sales-orders/{so['id']}/confirm", headers=_auth(token))
    invoice = client.post(
        f"{BASE}/sales-orders/{so['id']}/create-invoice", headers=_auth(token),
        json={"customer_id": customer_id, "invoice_date": f"{year}-06-11",
              "lines": [{"product_id": product_id, "qty": "2", "unit_price": "2500.00"}]},
    ).json()
    client.post(f"{BASE}/customer-invoices/{invoice['id']}/confirm", headers=_auth(token))

    return bill, invoice


def test_profit_and_loss_reflects_posted_entries(client, accountant_token, seeded_accounting):
    token = accountant_token
    _run_full_purchase_and_sale(client, token, seeded_accounting, year="2031")

    resp = client.get(f"{BASE}/reports/profit-loss", headers=_auth(token), params={"year": 2031})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["year"] == 2031

    income_accounts = {item["account_name"]: Decimal(item["amount"]) for item in body["income"]}
    expense_accounts = {item["account_name"]: Decimal(item["amount"]) for item in body["expenses"]}

    assert income_accounts.get("Sales Income A/c") == Decimal("5000.00")
    assert expense_accounts.get("Purchase Expense A/c") == Decimal("3000.00")
    assert Decimal(body["net_income"]) == Decimal("5000.00") - Decimal("3000.00")


def test_balance_sheet_reflects_posted_entries(client, accountant_token, seeded_accounting):
    """
    Balance Sheet is a cumulative snapshot (balances carry forward),
    so this asserts the DELTA this test's own transactions cause,
    rather than an absolute value -- other tests in the same session
    legitimately contribute to the same Debtors/Creditors balances.
    """
    token = accountant_token

    def _balances(year):
        resp = client.get(f"{BASE}/reports/balance-sheet", headers=_auth(token), params={"year": year})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assets = {item["account_name"]: Decimal(item["amount"]) for item in body["assets"]}
        liabilities = {item["account_name"]: Decimal(item["amount"]) for item in body["liabilities"]}
        return assets, liabilities

    before_assets, before_liabilities = _balances(2032)

    bill, invoice = _run_full_purchase_and_sale(client, token, seeded_accounting, year="2032")

    after_assets, after_liabilities = _balances(2032)

    assert after_assets.get("Debtors A/c", Decimal("0")) - before_assets.get("Debtors A/c", Decimal("0")) == Decimal("5000.00")
    assert after_liabilities.get("Creditors A/c", Decimal("0")) - before_liabilities.get("Creditors A/c", Decimal("0")) == Decimal("3000.00")

    # Pay the vendor bill in full -> Creditors balance should drop back down by exactly that amount
    pay = client.post(
        f"{BASE}/vendor-bills/{bill['id']}/pay", headers=_auth(token),
        json={"payment_type": "send", "payment_via": "bank", "date": "2032-06-05",
              "partner_id": seeded_accounting["vendor_id"], "amount": "3000.00",
              "source_type": "vendor_bill", "source_id": bill["id"]},
    ).json()
    client.post(f"{BASE}/payments/{pay['id']}/confirm", headers=_auth(token))

    final_assets, final_liabilities = _balances(2032)
    assert final_liabilities.get("Creditors A/c", Decimal("0")) == before_liabilities.get("Creditors A/c", Decimal("0")), \
        "Creditors balance should return to its pre-test level once the bill is fully paid"


def test_budget_report_lists_confirmed_budgets(client, accountant_token, seeded_accounting):
    token = accountant_token
    analytic = client.post(
        f"{BASE}/analytic-accounts/", headers=_auth(token),
        json={"name": "Report Test Project", "type": "expense"},
    ).json()
    budget = client.post(
        f"{BASE}/budgets/", headers=_auth(token),
        json={"name": "Report Test Budget", "period_start": "2033-01-01", "period_end": "2033-12-31",
              "analytic_account_id": analytic["id"], "committed_amount": "1000.00"},
    ).json()
    client.post(f"{BASE}/budgets/{budget['id']}/confirm", headers=_auth(token))

    resp = client.get(f"{BASE}/reports/budget", headers=_auth(token), params={"year": 2033})
    assert resp.status_code == 200, resp.text
    rows = resp.json()["rows"]
    assert any(r["budget_id"] == budget["id"] for r in rows)


def test_manual_journal_entry_must_balance_before_posting(client, accountant_token, seeded_accounting):
    token = accountant_token
    accounts_resp = client.get(f"{BASE}/accounts/", headers=_auth(token)).json()
    bank = next(a for a in accounts_resp if a["name"] == "Bank")
    capital = next(a for a in accounts_resp if a["name"] == "Capital A/c")
    journals_resp = client.get(f"{BASE}/journals/", headers=_auth(token)).json()
    bank_journal = next(j for j in journals_resp if j["name"] == "Bank")

    # Balanced manual entry: Dr Bank / Cr Capital (owner investment)
    je_resp = client.post(
        f"{BASE}/journal-entries/", headers=_auth(token),
        json={
            "journal_id": bank_journal["id"], "accounting_date": "2026-01-01",
            "reference_no": "Owner investment",
            "lines": [
                {"account_id": bank["id"], "debit": "50000.00", "credit": "0"},
                {"account_id": capital["id"], "debit": "0", "credit": "50000.00"},
            ],
        },
    )
    assert je_resp.status_code == 201, je_resp.text
    entry = je_resp.json()
    assert entry["status"] == "draft"

    post_resp = client.post(f"{BASE}/journal-entries/{entry['id']}/post", headers=_auth(token))
    assert post_resp.status_code == 200
    assert post_resp.json()["status"] == "posted"

    # Unbalanced manual entry must be rejected at POST time
    unbalanced_resp = client.post(
        f"{BASE}/journal-entries/", headers=_auth(token),
        json={
            "journal_id": bank_journal["id"], "accounting_date": "2026-01-02",
            "lines": [
                {"account_id": bank["id"], "debit": "100.00", "credit": "0"},
                {"account_id": capital["id"], "debit": "0", "credit": "999.00"},
            ],
        },
    ).json()
    reject_resp = client.post(
        f"{BASE}/journal-entries/{unbalanced_resp['id']}/post", headers=_auth(token)
    )
    assert reject_resp.status_code == 400


def test_reports_require_authentication(client):
    resp = client.get(f"{BASE}/reports/profit-loss", params={"year": 2026})
    assert resp.status_code == 401
