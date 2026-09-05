"""
Sales workflow tests: SO (no JE) -> Customer Invoice confirm (exactly
one balanced JE, Dr Debtors / Cr Sales Income) -> Payment (a SEPARATE
balanced JE, Dr Bank / Cr Debtors).
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
    assert total_debit > 0


def test_full_sales_workflow_nimesh_pathak(client, accountant_token, seeded_accounting):
    token = accountant_token
    customer_id = seeded_accounting["customer_id"]
    product_id = seeded_accounting["product_id"]

    so_resp = client.post(
        f"{BASE}/sales-orders/",
        headers=_auth(token),
        json={
            "customer_id": customer_id,
            "so_date": "2026-01-20",
            "lines": [{"product_id": product_id, "qty": "5", "unit_price": "2500.00"}],
        },
    )
    assert so_resp.status_code == 201, so_resp.text
    so = so_resp.json()
    assert so["so_no"].startswith("SO")
    assert so["status"] == "draft"

    confirm_so_resp = client.post(f"{BASE}/sales-orders/{so['id']}/confirm", headers=_auth(token))
    assert confirm_so_resp.status_code == 200
    assert confirm_so_resp.json()["status"] == "confirmed"

    all_entries = client.get(f"{BASE}/journal-entries/", headers=_auth(token)).json()
    entries_referencing_so = [e for e in all_entries if e.get("reference_no") == so["so_no"]]
    assert entries_referencing_so == [], "SO confirmation must not create a Journal Entry"

    invoice_resp = client.post(
        f"{BASE}/sales-orders/{so['id']}/create-invoice",
        headers=_auth(token),
        json={
            "customer_id": customer_id,
            "invoice_date": "2026-01-22",
            "lines": [{"product_id": product_id, "qty": "5", "unit_price": "2500.00"}],
        },
    )
    assert invoice_resp.status_code == 201, invoice_resp.text
    invoice = invoice_resp.json()
    assert invoice["invoice_no"].startswith("INV/2026/")
    assert invoice["status"] == "draft"

    confirm_invoice_resp = client.post(
        f"{BASE}/customer-invoices/{invoice['id']}/confirm", headers=_auth(token)
    )
    assert confirm_invoice_resp.status_code == 200, confirm_invoice_resp.text
    confirmed_invoice = confirm_invoice_resp.json()
    assert confirmed_invoice["status"] == "confirmed"

    entries = _journal_entries_for_source(client, token, "customer_invoice", invoice["id"])
    assert len(entries) == 1, f"Expected exactly one JE, found {len(entries)}"
    _assert_balanced(entries[0])

    account_names = set()
    for line in entries[0]["lines"]:
        acc_resp = client.get(f"{BASE}/accounts/{line['account_id']}", headers=_auth(token))
        account_names.add(acc_resp.json()["name"])
    assert "Debtors A/c" in account_names
    assert "Sales Income A/c" in account_names

    amount_due = confirmed_invoice["amount_due"]
    assert Decimal(amount_due) == Decimal("12500.00")

    pay_resp = client.post(
        f"{BASE}/customer-invoices/{invoice['id']}/pay",
        headers=_auth(token),
        json={
            "payment_type": "receive", "payment_via": "cash", "date": "2026-01-25",
            "partner_id": customer_id, "amount": amount_due,
            "source_type": "customer_invoice", "source_id": invoice["id"],
        },
    )
    assert pay_resp.status_code == 201, pay_resp.text
    payment = pay_resp.json()

    confirm_pay_resp = client.post(f"{BASE}/payments/{payment['id']}/confirm", headers=_auth(token))
    assert confirm_pay_resp.status_code == 200, confirm_pay_resp.text

    payment_entries = _journal_entries_for_source(client, token, "payment", payment["id"])
    assert len(payment_entries) == 1
    _assert_balanced(payment_entries[0])
    assert payment_entries[0]["id"] != entries[0]["id"]

    final_invoice = client.get(f"{BASE}/customer-invoices/{invoice['id']}", headers=_auth(token)).json()
    assert final_invoice["payment_status"] == "paid"
    assert Decimal(final_invoice["amount_due"]) == Decimal("0.00")


def test_partial_payment_leaves_invoice_partial(client, accountant_token, seeded_accounting):
    token = accountant_token
    customer_id = seeded_accounting["customer_id"]
    product_id = seeded_accounting["product_id"]

    so = client.post(
        f"{BASE}/sales-orders/", headers=_auth(token),
        json={"customer_id": customer_id, "so_date": "2026-02-01",
              "lines": [{"product_id": product_id, "qty": "2", "unit_price": "1000.00"}]},
    ).json()
    client.post(f"{BASE}/sales-orders/{so['id']}/confirm", headers=_auth(token))
    invoice = client.post(
        f"{BASE}/sales-orders/{so['id']}/create-invoice", headers=_auth(token),
        json={"customer_id": customer_id, "invoice_date": "2026-02-02",
              "lines": [{"product_id": product_id, "qty": "2", "unit_price": "1000.00"}]},
    ).json()
    client.post(f"{BASE}/customer-invoices/{invoice['id']}/confirm", headers=_auth(token))

    partial_payment = client.post(
        f"{BASE}/customer-invoices/{invoice['id']}/pay", headers=_auth(token),
        json={"payment_type": "receive", "payment_via": "bank", "date": "2026-02-05",
              "partner_id": customer_id, "amount": "1000.00",
              "source_type": "customer_invoice", "source_id": invoice["id"]},
    ).json()
    client.post(f"{BASE}/payments/{partial_payment['id']}/confirm", headers=_auth(token))

    updated_invoice = client.get(f"{BASE}/customer-invoices/{invoice['id']}", headers=_auth(token)).json()
    assert updated_invoice["payment_status"] == "partial"
    assert Decimal(updated_invoice["amount_due"]) == Decimal("1000.00")


def test_overpayment_is_rejected(client, accountant_token, seeded_accounting):
    token = accountant_token
    customer_id = seeded_accounting["customer_id"]
    product_id = seeded_accounting["product_id"]

    so = client.post(
        f"{BASE}/sales-orders/", headers=_auth(token),
        json={"customer_id": customer_id, "so_date": "2026-02-10",
              "lines": [{"product_id": product_id, "qty": "1", "unit_price": "500.00"}]},
    ).json()
    client.post(f"{BASE}/sales-orders/{so['id']}/confirm", headers=_auth(token))
    invoice = client.post(
        f"{BASE}/sales-orders/{so['id']}/create-invoice", headers=_auth(token),
        json={"customer_id": customer_id, "invoice_date": "2026-02-11",
              "lines": [{"product_id": product_id, "qty": "1", "unit_price": "500.00"}]},
    ).json()
    client.post(f"{BASE}/customer-invoices/{invoice['id']}/confirm", headers=_auth(token))

    resp = client.post(
        f"{BASE}/customer-invoices/{invoice['id']}/pay", headers=_auth(token),
        json={"payment_type": "receive", "payment_via": "bank", "date": "2026-02-12",
              "partner_id": customer_id, "amount": "999999.00",
              "source_type": "customer_invoice", "source_id": invoice["id"]},
    )
    assert resp.status_code == 400


def test_cannot_pay_unconfirmed_invoice(client, accountant_token, seeded_accounting):
    token = accountant_token
    customer_id = seeded_accounting["customer_id"]
    product_id = seeded_accounting["product_id"]

    so = client.post(
        f"{BASE}/sales-orders/", headers=_auth(token),
        json={"customer_id": customer_id, "so_date": "2026-02-15",
              "lines": [{"product_id": product_id, "qty": "1", "unit_price": "500.00"}]},
    ).json()
    client.post(f"{BASE}/sales-orders/{so['id']}/confirm", headers=_auth(token))
    invoice = client.post(
        f"{BASE}/sales-orders/{so['id']}/create-invoice", headers=_auth(token),
        json={"customer_id": customer_id, "invoice_date": "2026-02-16",
              "lines": [{"product_id": product_id, "qty": "1", "unit_price": "500.00"}]},
    ).json()

    resp = client.post(
        f"{BASE}/customer-invoices/{invoice['id']}/pay", headers=_auth(token),
        json={"payment_type": "receive", "payment_via": "bank", "date": "2026-02-17",
              "partner_id": customer_id, "amount": "500.00",
              "source_type": "customer_invoice", "source_id": invoice["id"]},
    )
    assert resp.status_code == 400


def test_customer_contact_can_view_only_own_invoice(client, accountant_token, db_session, seeded_accounting):
    from app.auth.password import hash_password
    from app.models.enums import UserRole
    from app.models.user import User
    from tests.conftest import VALID_PASSWORD, _random_login_id

    token = accountant_token
    customer_id = seeded_accounting["customer_id"]
    product_id = seeded_accounting["product_id"]

    so = client.post(
        f"{BASE}/sales-orders/", headers=_auth(token),
        json={"customer_id": customer_id, "so_date": "2026-03-01",
              "lines": [{"product_id": product_id, "qty": "1", "unit_price": "500.00"}]},
    ).json()
    client.post(f"{BASE}/sales-orders/{so['id']}/confirm", headers=_auth(token))
    invoice = client.post(
        f"{BASE}/sales-orders/{so['id']}/create-invoice", headers=_auth(token),
        json={"customer_id": customer_id, "invoice_date": "2026-03-02",
              "lines": [{"product_id": product_id, "qty": "1", "unit_price": "500.00"}]},
    ).json()

    login_id = _random_login_id()
    contact_user = User(
        login_id=login_id, email=f"{login_id}@example.com",
        password_hash=hash_password(VALID_PASSWORD), role=UserRole.CONTACT,
        contact_id=customer_id,
    )
    db_session.add(contact_user)
    db_session.commit()
    contact_token = client.post(
        f"{BASE}/auth/login", json={"login_id": login_id, "password": VALID_PASSWORD}
    ).json()["access_token"]

    own_resp = client.get(f"{BASE}/customer-invoices/{invoice['id']}", headers=_auth(contact_token))
    assert own_resp.status_code == 200

    # A contact tied to the vendor (not this customer) cannot see it
    other_login_id = _random_login_id()
    other_contact = User(
        login_id=other_login_id, email=f"{other_login_id}@example.com",
        password_hash=hash_password(VALID_PASSWORD), role=UserRole.CONTACT,
        contact_id=seeded_accounting["vendor_id"],
    )
    db_session.add(other_contact)
    db_session.commit()
    other_token = client.post(
        f"{BASE}/auth/login", json={"login_id": other_login_id, "password": VALID_PASSWORD}
    ).json()["access_token"]

    other_resp = client.get(f"{BASE}/customer-invoices/{invoice['id']}", headers=_auth(other_token))
    assert other_resp.status_code == 404
