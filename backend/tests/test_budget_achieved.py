"""
Budget tests: lifecycle (Draft -> Confirmed -> Revised -> Cancelled),
computed achieved amount/percentage, and the non-blocking
budget-exceeded warning on PO/Bill confirmation.
"""
from decimal import Decimal

BASE = "/api/v1"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _unique_analytic_account(client, token, name: str, acc_type: str = "expense") -> dict:
    resp = client.post(
        f"{BASE}/analytic-accounts/", headers=_auth(token), json={"name": name, "type": acc_type}
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_budget_lifecycle_and_achieved_amount(client, accountant_token, seeded_accounting):
    token = accountant_token
    vendor_id = seeded_accounting["vendor_id"]
    product_id = seeded_accounting["product_id"]

    analytic = _unique_analytic_account(client, token, "Project Alpha", "expense")

    budget_resp = client.post(
        f"{BASE}/budgets/", headers=_auth(token),
        json={
            "name": "Project Alpha Budget", "period_start": "2026-01-01", "period_end": "2026-12-31",
            "analytic_account_id": analytic["id"], "committed_amount": "10000.00",
        },
    )
    assert budget_resp.status_code == 201, budget_resp.text
    budget = budget_resp.json()
    assert budget["status"] == "draft"
    assert budget["achieved_amount"] is None, "Achieved fields must not be visible before confirmation"

    confirm_resp = client.post(f"{BASE}/budgets/{budget['id']}/confirm", headers=_auth(token))
    assert confirm_resp.status_code == 200
    confirmed = confirm_resp.json()
    assert confirmed["status"] == "confirmed"
    assert Decimal(confirmed["achieved_amount"]) == Decimal("0.00")
    assert Decimal(confirmed["achieved_percentage"]) == Decimal("0")

    # Confirm a PO + Bill tagged with this analytic account -> achieved should update
    po = client.post(
        f"{BASE}/purchase-orders/", headers=_auth(token),
        json={"vendor_id": vendor_id, "po_date": "2026-04-01",
              "lines": [{"product_id": product_id, "qty": "2", "unit_price": "2000.00",
                         "analytic_account_id": analytic["id"]}]},
    ).json()
    client.post(f"{BASE}/purchase-orders/{po['id']}/confirm", headers=_auth(token))
    bill = client.post(
        f"{BASE}/purchase-orders/{po['id']}/create-bill", headers=_auth(token),
        json={"vendor_id": vendor_id, "bill_date": "2026-04-02",
              "lines": [{"product_id": product_id, "qty": "2", "unit_price": "2000.00",
                         "analytic_account_id": analytic["id"]}]},
    ).json()
    client.post(f"{BASE}/vendor-bills/{bill['id']}/confirm", headers=_auth(token))

    updated_budget = client.get(f"{BASE}/budgets/{budget['id']}", headers=_auth(token)).json()
    assert Decimal(updated_budget["achieved_amount"]) == Decimal("4000.00")
    assert Decimal(updated_budget["achieved_percentage"]) == Decimal("40")
    assert Decimal(updated_budget["amount_to_achieve"]) == Decimal("6000.00")


def test_budget_revision_preserves_history(client, accountant_token):
    token = accountant_token
    analytic = _unique_analytic_account(client, token, "Project Beta", "expense")

    original = client.post(
        f"{BASE}/budgets/", headers=_auth(token),
        json={"name": "Beta Budget", "period_start": "2026-01-01", "period_end": "2026-12-31",
              "analytic_account_id": analytic["id"], "committed_amount": "5000.00"},
    ).json()
    client.post(f"{BASE}/budgets/{original['id']}/confirm", headers=_auth(token))

    revise_resp = client.post(
        f"{BASE}/budgets/{original['id']}/revise", headers=_auth(token),
        json={"new_committed_amount": "8000.00"},
    )
    assert revise_resp.status_code == 200, revise_resp.text
    revised = revise_resp.json()
    assert revised["id"] != original["id"]
    assert revised["revision_of_id"] == original["id"]
    assert revised["status"] == "confirmed"
    assert Decimal(revised["committed_amount"]) == Decimal("8000.00")

    original_after = client.get(f"{BASE}/budgets/{original['id']}", headers=_auth(token)).json()
    assert original_after["status"] == "revised"
    assert Decimal(original_after["committed_amount"]) == Decimal("5000.00"), \
        "Original committed_amount must never be mutated in place"


def test_cannot_revise_a_draft_budget(client, accountant_token):
    token = accountant_token
    analytic = _unique_analytic_account(client, token, "Project Gamma", "expense")
    budget = client.post(
        f"{BASE}/budgets/", headers=_auth(token),
        json={"name": "Gamma Budget", "period_start": "2026-01-01", "period_end": "2026-12-31",
              "analytic_account_id": analytic["id"], "committed_amount": "1000.00"},
    ).json()

    resp = client.post(
        f"{BASE}/budgets/{budget['id']}/revise", headers=_auth(token),
        json={"new_committed_amount": "2000.00"},
    )
    assert resp.status_code == 400


def test_budget_cancel(client, accountant_token):
    token = accountant_token
    analytic = _unique_analytic_account(client, token, "Project Delta", "expense")
    budget = client.post(
        f"{BASE}/budgets/", headers=_auth(token),
        json={"name": "Delta Budget", "period_start": "2026-01-01", "period_end": "2026-12-31",
              "analytic_account_id": analytic["id"], "committed_amount": "1000.00"},
    ).json()

    resp = client.post(f"{BASE}/budgets/{budget['id']}/cancel", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


def test_budget_exceeded_warning_does_not_block_confirmation(client, accountant_token, seeded_accounting):
    """A tiny budget, then a PO that blows past it -- confirmation must
    still succeed, with a warning surfaced, never a blocking error."""
    token = accountant_token
    vendor_id = seeded_accounting["vendor_id"]
    product_id = seeded_accounting["product_id"]

    analytic = _unique_analytic_account(client, token, "Tiny Budget Project", "expense")
    budget = client.post(
        f"{BASE}/budgets/", headers=_auth(token),
        json={"name": "Tiny Budget", "period_start": "2026-01-01", "period_end": "2026-12-31",
              "analytic_account_id": analytic["id"], "committed_amount": "100.00"},
    ).json()
    client.post(f"{BASE}/budgets/{budget['id']}/confirm", headers=_auth(token))

    po = client.post(
        f"{BASE}/purchase-orders/", headers=_auth(token),
        json={"vendor_id": vendor_id, "po_date": "2026-05-01",
              "lines": [{"product_id": product_id, "qty": "10", "unit_price": "1000.00",
                         "analytic_account_id": analytic["id"]}]},
    ).json()

    confirm_resp = client.post(f"{BASE}/purchase-orders/{po['id']}/confirm", headers=_auth(token))
    assert confirm_resp.status_code == 200, "Budget-exceeded must NOT block PO confirmation"
    assert confirm_resp.json()["status"] == "confirmed"
    assert len(confirm_resp.json()["budget_warnings"]) == 1
    assert "exceeded" in confirm_resp.json()["budget_warnings"][0].lower()


def test_budgets_require_authentication(client):
    resp = client.get(f"{BASE}/budgets/")
    assert resp.status_code == 401
