"""
Checkpoint 2 tests: Master Data CRUD.

Covers, per resource: list/create/get/update(/delete where implemented),
auth requirement, duplicate-field conflicts, and invalid-FK handling.
"""
import uuid

BASE = "/api/v1"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------
# Auth requirement (shared behavior across all master data endpoints)
# ---------------------------------------------------------------------

def test_master_data_endpoints_reject_unauthenticated(client):
    for path in ["/contacts/", "/products/", "/accounts/", "/journals/", "/analytic-accounts/"]:
        resp = client.get(BASE + path)
        assert resp.status_code == 401, f"{path} did not reject unauthenticated request"


# ---------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------

def test_create_contact_auto_provisions_login(client, accountant_token):
    email = f"{_unique('cust')}@example.com"
    resp = client.post(
        f"{BASE}/contacts/",
        headers=_auth(accountant_token),
        json={"name": "Nimesh Pathak", "type": "customer", "email": email},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["email"] == email
    assert body["provisioned_login_id"] is not None
    assert body["temporary_password"] is not None


def test_create_contact_duplicate_email_returns_409(client, accountant_token):
    email = f"{_unique('dup')}@example.com"
    payload = {"name": "Vendor A", "type": "vendor", "email": email}
    first = client.post(f"{BASE}/contacts/", headers=_auth(accountant_token), json=payload)
    assert first.status_code == 201

    second = client.post(f"{BASE}/contacts/", headers=_auth(accountant_token), json=payload)
    assert second.status_code == 409


def test_get_list_update_delete_contact(client, accountant_token):
    email = f"{_unique('flow')}@example.com"
    created = client.post(
        f"{BASE}/contacts/",
        headers=_auth(accountant_token),
        json={"name": "Both Co", "type": "both", "email": email},
    ).json()
    contact_id = created["id"]

    get_resp = client.get(f"{BASE}/contacts/{contact_id}", headers=_auth(accountant_token))
    assert get_resp.status_code == 200
    assert "provisioned_login_id" not in get_resp.json()

    list_resp = client.get(f"{BASE}/contacts/", headers=_auth(accountant_token))
    assert list_resp.status_code == 200
    assert any(c["id"] == contact_id for c in list_resp.json())

    update_resp = client.put(
        f"{BASE}/contacts/{contact_id}",
        headers=_auth(accountant_token),
        json={"name": "Both Co Updated"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Both Co Updated"

    delete_resp = client.delete(f"{BASE}/contacts/{contact_id}", headers=_auth(accountant_token))
    assert delete_resp.status_code == 204

    missing_resp = client.get(f"{BASE}/contacts/{contact_id}", headers=_auth(accountant_token))
    assert missing_resp.status_code == 404


def test_get_nonexistent_contact_returns_404(client, accountant_token):
    resp = client.get(f"{BASE}/contacts/999999", headers=_auth(accountant_token))
    assert resp.status_code == 404


# ---------------------------------------------------------------------
# Products + Product Categories
# ---------------------------------------------------------------------

def test_create_and_list_category(client, accountant_token):
    name = _unique("Category")
    resp = client.post(
        f"{BASE}/products/categories", headers=_auth(accountant_token), json={"name": name}
    )
    assert resp.status_code == 201, resp.text

    list_resp = client.get(f"{BASE}/products/categories", headers=_auth(accountant_token))
    assert list_resp.status_code == 200
    assert any(c["name"] == name for c in list_resp.json())


def test_duplicate_category_returns_409(client, accountant_token):
    name = _unique("DupCat")
    first = client.post(
        f"{BASE}/products/categories", headers=_auth(accountant_token), json={"name": name}
    )
    assert first.status_code == 201
    second = client.post(
        f"{BASE}/products/categories", headers=_auth(accountant_token), json={"name": name}
    )
    assert second.status_code == 409


def test_categories_route_not_shadowed_by_product_id_route(client, accountant_token):
    """Regression test for a routing-order bug: /products/categories must
    not be swallowed by GET /products/{product_id}."""
    resp = client.get(f"{BASE}/products/categories", headers=_auth(accountant_token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_product_crud_flow(client, accountant_token):
    category = client.post(
        f"{BASE}/products/categories",
        headers=_auth(accountant_token),
        json={"name": _unique("Furniture")},
    ).json()

    create_resp = client.post(
        f"{BASE}/products/",
        headers=_auth(accountant_token),
        json={
            "name": "Wooden Chair",
            "type": "goods",
            "sales_price": "1500.00",
            "cost": "900.00",
            "category_id": category["id"],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    product = create_resp.json()

    get_resp = client.get(f"{BASE}/products/{product['id']}", headers=_auth(accountant_token))
    assert get_resp.status_code == 200

    update_resp = client.put(
        f"{BASE}/products/{product['id']}",
        headers=_auth(accountant_token),
        json={"sales_price": "1600.00"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["sales_price"] == "1600.00"

    delete_resp = client.delete(f"{BASE}/products/{product['id']}", headers=_auth(accountant_token))
    assert delete_resp.status_code == 204


def test_product_with_invalid_category_returns_400(client, accountant_token):
    resp = client.post(
        f"{BASE}/products/",
        headers=_auth(accountant_token),
        json={
            "name": "Ghost Product",
            "type": "goods",
            "sales_price": "10.00",
            "cost": "5.00",
            "category_id": 999999,
        },
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------
# Chart of Accounts
# ---------------------------------------------------------------------

def test_account_crud_flow(client, accountant_token):
    name = _unique("Bank Account")
    create_resp = client.post(
        f"{BASE}/accounts/",
        headers=_auth(accountant_token),
        json={"name": name, "type": "bank"},
    )
    assert create_resp.status_code == 201, create_resp.text
    account = create_resp.json()
    assert account["status"] == "confirmed"

    get_resp = client.get(f"{BASE}/accounts/{account['id']}", headers=_auth(accountant_token))
    assert get_resp.status_code == 200

    archive_resp = client.put(
        f"{BASE}/accounts/{account['id']}",
        headers=_auth(accountant_token),
        json={"status": "archived"},
    )
    assert archive_resp.status_code == 200
    assert archive_resp.json()["status"] == "archived"


def test_duplicate_account_name_returns_409(client, accountant_token):
    name = _unique("Cash Account")
    payload = {"name": name, "type": "cash"}
    first = client.post(f"{BASE}/accounts/", headers=_auth(accountant_token), json=payload)
    assert first.status_code == 201
    second = client.post(f"{BASE}/accounts/", headers=_auth(accountant_token), json=payload)
    assert second.status_code == 409


def test_get_nonexistent_account_returns_404(client, accountant_token):
    resp = client.get(f"{BASE}/accounts/999999", headers=_auth(accountant_token))
    assert resp.status_code == 404


# ---------------------------------------------------------------------
# Journals
# ---------------------------------------------------------------------

def test_journal_crud_flow(client, accountant_token):
    account = client.post(
        f"{BASE}/accounts/",
        headers=_auth(accountant_token),
        json={"name": _unique("Sales Income A/c"), "type": "income"},
    ).json()

    create_resp = client.post(
        f"{BASE}/journals/",
        headers=_auth(accountant_token),
        json={
            "name": _unique("Sales Journal"),
            "type": "sales",
            "default_account_id": account["id"],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    journal = create_resp.json()

    get_resp = client.get(f"{BASE}/journals/{journal['id']}", headers=_auth(accountant_token))
    assert get_resp.status_code == 200

    update_resp = client.put(
        f"{BASE}/journals/{journal['id']}",
        headers=_auth(accountant_token),
        json={"name": "Renamed Journal"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Renamed Journal"


def test_journal_with_invalid_default_account_returns_400(client, accountant_token):
    resp = client.post(
        f"{BASE}/journals/",
        headers=_auth(accountant_token),
        json={"name": _unique("Bad Journal"), "type": "cash", "default_account_id": 999999},
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------
# Analytic Accounts
# ---------------------------------------------------------------------

def test_analytic_account_crud_flow(client, accountant_token):
    name = _unique("Project")
    create_resp = client.post(
        f"{BASE}/analytic-accounts/",
        headers=_auth(accountant_token),
        json={"name": name, "type": "income"},
    )
    assert create_resp.status_code == 201, create_resp.text
    account = create_resp.json()

    get_resp = client.get(
        f"{BASE}/analytic-accounts/{account['id']}", headers=_auth(accountant_token)
    )
    assert get_resp.status_code == 200

    update_resp = client.put(
        f"{BASE}/analytic-accounts/{account['id']}",
        headers=_auth(accountant_token),
        json={"type": "expense"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["type"] == "expense"

    delete_resp = client.delete(
        f"{BASE}/analytic-accounts/{account['id']}", headers=_auth(accountant_token)
    )
    assert delete_resp.status_code == 204


def test_duplicate_analytic_account_name_returns_409(client, accountant_token):
    name = _unique("Marketing")
    payload = {"name": name, "type": "expense"}
    first = client.post(f"{BASE}/analytic-accounts/", headers=_auth(accountant_token), json=payload)
    assert first.status_code == 201
    second = client.post(f"{BASE}/analytic-accounts/", headers=_auth(accountant_token), json=payload)
    assert second.status_code == 409


# ---------------------------------------------------------------------
# Admin can also use master data endpoints (not just accountant)
# ---------------------------------------------------------------------

def test_admin_can_use_master_data_endpoints(client, admin_token):
    resp = client.get(f"{BASE}/contacts/", headers=_auth(admin_token))
    assert resp.status_code == 200
