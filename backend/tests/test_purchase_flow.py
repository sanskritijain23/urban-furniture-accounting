"""
Purchase workflow tests: PO (no JE) -> Vendor Bill confirm (exactly one
balanced JE, Dr Purchase Expense / Cr Creditors) -> Payment (a
SEPARATE balanced JE, Dr Creditors / Cr Bank).
"""
from decimal import Decimal

BASE = "/api/v1"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _journal_entries_for_source(client, token, source_type: str, source_id: int):
    resp = client.get(f"{BASE}/journal-entries/", headers=_auth(token))
    assert resp.status_code == 200
    return [
        e for e in resp.json()
        if e["source_type"] == source_type and e["source_id"] == source_id
    ]


def _assert_balanced(entry: dict):
    total_debit = sum(Decimal(l["debit"]) for l in entry["lines"])
    total_credit = sum(Decimal(l["credit"]) for l in entry["lines"])
    assert total_debit == total_credit, f"Unbalanced entry: debit={total_debit} credit={total_credit}"
    assert total_debit > 0, "Entry has zero-value lines"


def test_full_purchase_workflow_azure_furniture(client, accountant_token, seeded_accounting):
    token = accountant_token
    vendor_id = seeded_accounting["vendor_id"]
    product_id = seeded_accounting["product_id"]

    po_resp = client.post(
        f"{BASE}/purchase-orders/",
        headers=_auth(token),
        json={
            "vendor_id": vendor_id,
            "po_date": "2026-01-10",
            "lines": [{"product_id": product_id, "qty": "5", "unit_price": "1500.00"}],
        },
    )
    assert po_resp.status_code == 201, po_resp.text
    po = po_resp.json()
    assert po["po_no"].startswith("PO")
    assert po["status"] == "draft"

    confirm_po_resp = client.post(f"{BASE}/purchase-orders/{po['id']}/confirm", headers=_auth(token))
    assert confirm_po_resp.status_code == 200, confirm_po_resp.text
    assert confirm_po_resp.json()["status"] == "confirmed"
    assert confirm_po_resp.json()["budget_warnings"] == []

    all_entries_before_bill = client.get(f"{BASE}/journal-entries/", headers=_auth(token)).json()
    entries_referencing_po = [
        e for e in all_entries_before_bill if e.get("reference_no") == po["po_no"]
    ]
    assert entries_referencing_po == [], "PO confirmation must not create a Journal Entry"

    bill_resp = client.post(
        f"{BASE}/purchase-orders/{po['id']}/create-bill",
        headers=_auth(token),
        json={
            "vendor_id": vendor_id,
            "bill_date": "2026-01-12",
            "reference": "PO from Azure Furniture",
            "lines": [{"product_id": product_id, "qty": "5", "unit_price": "1500.00"}],
        },
    )
    assert bill_resp.status_code == 201, bill_resp.text
    bill = bill_resp.json()
    assert bill["bill_no"].startswith("Bill/2026/")
    assert bill["status"] == "draft"
    assert bill["reference"] == "PO from Azure Furniture"
    assert bill["reference"] != bill["bill_no"], "bill_no and reference must be distinct fields"

    confirm_bill_resp = client.post(f"{BASE}/vendor-bills/{bill['id']}/confirm", headers=_auth(token))
    assert confirm_bill_resp.status_code == 200, confirm_bill_resp.text
    confirmed_bill = confirm_bill_resp.json()
    assert confirmed_bill["status"] == "confirmed"

    entries = _journal_entries_for_source(client, token, "vendor_bill", bill["id"])
    assert len(entries) == 1, f"Expected exactly one JE, found {len(entries)}"
    _assert_balanced(entries[0])

    account_names = set()
    for line in entries[0]["lines"]:
        acc_resp = client.get(f"{BASE}/accounts/{line['account_id']}", headers=_auth(token))
        account_names.add(acc_resp.json()["name"])
    assert "Purchase Expense A/c" in account_names
    assert "Creditors A/c" in account_names

    amount_due = confirmed_bill["amount_due"]
    assert Decimal(amount_due) == Decimal("7500.00")

    pay_resp = client.post(
        f"{BASE}/vendor-bills/{bill['id']}/pay",
        headers=_auth(token),
        json={
            "payment_type": "send", "payment_via": "bank", "date": "2026-01-15",
            "partner_id": vendor_id, "amount": amount_due,
            "source_type": "vendor_bill", "source_id": bill["id"],
        },
    )
    assert pay_resp.status_code == 201, pay_resp.text
    payment = pay_resp.json()
    assert payment["status"] == "draft"

    confirm_pay_resp = client.post(f"{BASE}/payments/{payment['id']}/confirm", headers=_auth(token))
    assert confirm_pay_resp.status_code == 200, confirm_pay_resp.text
    assert confirm_pay_resp.json()["status"] == "confirmed"

    payment_entries = _journal_entries_for_source(client, token, "payment", payment["id"])
    assert len(payment_entries) == 1
    _assert_balanced(payment_entries[0])
    assert payment_entries[0]["id"] != entries[0]["id"], "Payment JE must be separate from the Bill JE"

    final_bill = client.get(f"{BASE}/vendor-bills/{bill['id']}", headers=_auth(token)).json()
    assert final_bill["payment_status"] == "paid"
    assert Decimal(final_bill["amount_due"]) == Decimal("0.00")


def test_confirming_po_twice_is_rejected(client, accountant_token, seeded_accounting):
    token = accountant_token
    po = client.post(
        f"{BASE}/purchase-orders/",
        headers=_auth(token),
        json={
            "vendor_id": seeded_accounting["vendor_id"],
            "po_date": "2026-02-01",
            "lines": [{"product_id": seeded_accounting["product_id"], "qty": "1", "unit_price": "100.00"}],
        },
    ).json()

    first = client.post(f"{BASE}/purchase-orders/{po['id']}/confirm", headers=_auth(token))
    assert first.status_code == 200

    second = client.post(f"{BASE}/purchase-orders/{po['id']}/confirm", headers=_auth(token))
    assert second.status_code == 400


def test_cannot_create_bill_from_unconfirmed_po(client, accountant_token, seeded_accounting):
    token = accountant_token
    po = client.post(
        f"{BASE}/purchase-orders/",
        headers=_auth(token),
        json={
            "vendor_id": seeded_accounting["vendor_id"],
            "po_date": "2026-02-01",
            "lines": [{"product_id": seeded_accounting["product_id"], "qty": "1", "unit_price": "100.00"}],
        },
    ).json()

    resp = client.post(
        f"{BASE}/purchase-orders/{po['id']}/create-bill",
        headers=_auth(token),
        json={
            "vendor_id": seeded_accounting["vendor_id"],
            "bill_date": "2026-02-02",
            "lines": [{"product_id": seeded_accounting["product_id"], "qty": "1", "unit_price": "100.00"}],
        },
    )
    assert resp.status_code == 400


def test_purchase_orders_require_authentication(client):
    resp = client.get(f"{BASE}/purchase-orders/")
    assert resp.status_code == 401


def test_contact_cannot_access_purchase_orders(client, db_session, seeded_accounting):
    """Purchase Orders are internal -- never exposed to Contact-role users."""
    from app.auth.password import hash_password
    from app.models.enums import UserRole
    from app.models.user import User
    from tests.conftest import VALID_PASSWORD, _random_login_id

    login_id = _random_login_id()
    contact_user = User(
        login_id=login_id, email=f"{login_id}@example.com",
        password_hash=hash_password(VALID_PASSWORD), role=UserRole.CONTACT,
        contact_id=seeded_accounting["vendor_id"],
    )
    db_session.add(contact_user)
    db_session.commit()

    token = client.post(
        f"{BASE}/auth/login", json={"login_id": login_id, "password": VALID_PASSWORD}
    ).json()["access_token"]

    resp = client.get(f"{BASE}/purchase-orders/", headers=_auth(token))
    assert resp.status_code == 403


def test_vendor_contact_can_view_only_own_bill(client, accountant_token, db_session, seeded_accounting):
    """Contact Portal: a contact sees only bills for their own vendor record."""
    from app.auth.password import hash_password
    from app.models.enums import UserRole
    from app.models.user import User
    from tests.conftest import VALID_PASSWORD, _random_login_id

    token = accountant_token
    vendor_id = seeded_accounting["vendor_id"]
    product_id = seeded_accounting["product_id"]

    po = client.post(
        f"{BASE}/purchase-orders/", headers=_auth(token),
        json={"vendor_id": vendor_id, "po_date": "2026-03-01",
              "lines": [{"product_id": product_id, "qty": "1", "unit_price": "500.00"}]},
    ).json()
    client.post(f"{BASE}/purchase-orders/{po['id']}/confirm", headers=_auth(token))
    bill = client.post(
        f"{BASE}/purchase-orders/{po['id']}/create-bill", headers=_auth(token),
        json={"vendor_id": vendor_id, "bill_date": "2026-03-02",
              "lines": [{"product_id": product_id, "qty": "1", "unit_price": "500.00"}]},
    ).json()

    login_id = _random_login_id()
    contact_user = User(
        login_id=login_id, email=f"{login_id}@example.com",
        password_hash=hash_password(VALID_PASSWORD), role=UserRole.CONTACT,
        contact_id=vendor_id,
    )
    db_session.add(contact_user)
    db_session.commit()
    contact_token = client.post(
        f"{BASE}/auth/login", json={"login_id": login_id, "password": VALID_PASSWORD}
    ).json()["access_token"]

    own_bill_resp = client.get(f"{BASE}/vendor-bills/{bill['id']}", headers=_auth(contact_token))
    assert own_bill_resp.status_code == 200

    other_login_id = _random_login_id()
    other_contact = User(
        login_id=other_login_id, email=f"{other_login_id}@example.com",
        password_hash=hash_password(VALID_PASSWORD), role=UserRole.CONTACT,
        contact_id=seeded_accounting["customer_id"],
    )
    db_session.add(other_contact)
    db_session.commit()
    other_token = client.post(
        f"{BASE}/auth/login", json={"login_id": other_login_id, "password": VALID_PASSWORD}
    ).json()["access_token"]

    other_bill_resp = client.get(f"{BASE}/vendor-bills/{bill['id']}", headers=_auth(other_token))
    assert other_bill_resp.status_code == 404

    forbidden_resp = client.post(
        f"{BASE}/vendor-bills/{bill['id']}/confirm", headers=_auth(contact_token)
    )
    assert forbidden_resp.status_code == 403
