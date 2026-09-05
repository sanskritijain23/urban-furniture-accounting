"""
Checkpoint 1 tests: authentication + FastAPI foundation.

Covers exactly the "Test" checklist from the checkpoint brief:
  - application starts / /health / /docs
  - signup works (+ validation + duplicate checks)
  - login works / wrong password fails
  - protected endpoint rejects unauthenticated request
  - valid JWT allows protected endpoint
  - (bonus) role-based access control on an admin-only endpoint
"""
from app.auth.password import hash_password
from app.models.enums import UserRole
from app.models.user import User
from tests.conftest import VALID_PASSWORD


# ---------------------------------------------------------------------
# App foundation
# ---------------------------------------------------------------------

def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_docs_available(client):
    resp = client.get("/docs")
    assert resp.status_code == 200


def test_openapi_schema_available(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200


# ---------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------

def test_signup_success_creates_accountant(client, unique_login_id, unique_email):
    resp = client.post(
        "/api/v1/auth/signup",
        json={
            "login_id": unique_login_id,
            "email": unique_email,
            "password": VALID_PASSWORD,
            "name": "New Accountant",
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["login_id"] == unique_login_id
    assert body["email"] == unique_email
    assert body["role"] == UserRole.ACCOUNTANT.value


def test_signup_duplicate_login_id_returns_409(client, unique_login_id, unique_email):
    payload = {
        "login_id": unique_login_id,
        "email": unique_email,
        "password": VALID_PASSWORD,
    }
    first = client.post("/api/v1/auth/signup", json=payload)
    assert first.status_code == 201

    payload["email"] = "different-" + unique_email
    second = client.post("/api/v1/auth/signup", json=payload)
    assert second.status_code == 409
    assert "login_id" in second.json()["detail"]


def test_signup_duplicate_email_returns_409(client, unique_login_id, unique_email):
    payload = {
        "login_id": unique_login_id,
        "email": unique_email,
        "password": VALID_PASSWORD,
    }
    first = client.post("/api/v1/auth/signup", json=payload)
    assert first.status_code == 201

    payload["login_id"] = "other" + unique_login_id[-4:]
    second = client.post("/api/v1/auth/signup", json=payload)
    assert second.status_code == 409
    assert "email" in second.json()["detail"]


def test_signup_rejects_short_login_id(client, unique_email):
    resp = client.post(
        "/api/v1/auth/signup",
        json={"login_id": "abc", "email": unique_email, "password": VALID_PASSWORD},
    )
    assert resp.status_code == 422


def test_signup_rejects_long_login_id(client, unique_email):
    resp = client.post(
        "/api/v1/auth/signup",
        json={
            "login_id": "a" * 13,
            "email": unique_email,
            "password": VALID_PASSWORD,
        },
    )
    assert resp.status_code == 422


def test_signup_rejects_weak_password_missing_special_char(client, unique_login_id, unique_email):
    resp = client.post(
        "/api/v1/auth/signup",
        json={"login_id": unique_login_id, "email": unique_email, "password": "NoSpecial1"},
    )
    assert resp.status_code == 422


def test_signup_rejects_weak_password_too_short(client, unique_login_id, unique_email):
    resp = client.post(
        "/api/v1/auth/signup",
        json={"login_id": unique_login_id, "email": unique_email, "password": "Sh0rt!"},
    )
    assert resp.status_code == 422


def test_signup_rejects_invalid_email(client, unique_login_id):
    resp = client.post(
        "/api/v1/auth/signup",
        json={"login_id": unique_login_id, "email": "not-an-email", "password": VALID_PASSWORD},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------

def _signup(client, login_id, email, password=VALID_PASSWORD):
    resp = client.post(
        "/api/v1/auth/signup",
        json={"login_id": login_id, "email": email, "password": password},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_login_success_returns_jwt(client, unique_login_id, unique_email):
    _signup(client, unique_login_id, unique_email)

    resp = client.post(
        "/api/v1/auth/login",
        json={"login_id": unique_login_id, "password": VALID_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and len(body["access_token"]) > 0


def test_login_wrong_password_returns_401(client, unique_login_id, unique_email):
    _signup(client, unique_login_id, unique_email)

    resp = client.post(
        "/api/v1/auth/login",
        json={"login_id": unique_login_id, "password": "WrongPass!1"},
    )
    assert resp.status_code == 401


def test_login_nonexistent_user_returns_401(client, unique_login_id):
    resp = client.post(
        "/api/v1/auth/login",
        json={"login_id": unique_login_id, "password": VALID_PASSWORD},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------
# JWT-protected endpoint (current-user dependency)
# ---------------------------------------------------------------------

def test_protected_endpoint_rejects_unauthenticated_request(client):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401


def test_protected_endpoint_rejects_garbage_token(client):
    resp = client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert resp.status_code == 401


def test_valid_jwt_allows_protected_endpoint(client, unique_login_id, unique_email):
    _signup(client, unique_login_id, unique_email)
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"login_id": unique_login_id, "password": VALID_PASSWORD},
    )
    token = login_resp.json()["access_token"]

    resp = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["login_id"] == unique_login_id


# ---------------------------------------------------------------------
# Role-based access control (admin-only endpoint)
# ---------------------------------------------------------------------

def test_admin_only_endpoint_forbidden_for_accountant(client, unique_login_id, unique_email):
    _signup(client, unique_login_id, unique_email)
    token = client.post(
        "/api/v1/auth/login",
        json={"login_id": unique_login_id, "password": VALID_PASSWORD},
    ).json()["access_token"]

    resp = client.get("/api/v1/users/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_admin_only_endpoint_allows_admin(client, db_session, unique_login_id, unique_email):
    # Admin accounts aren't created via public signup (by design -- see
    # docs/workflows.md); seed one directly, the way seed_data.py / the
    # admin-only Create User form would in real usage.
    admin = User(
        login_id=unique_login_id,
        email=unique_email,
        password_hash=hash_password(VALID_PASSWORD),
        name="Seed Admin",
        role=UserRole.ADMIN,
    )
    db_session.add(admin)
    db_session.commit()

    token = client.post(
        "/api/v1/auth/login",
        json={"login_id": unique_login_id, "password": VALID_PASSWORD},
    ).json()["access_token"]

    resp = client.get("/api/v1/users/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)


def test_admin_can_create_accountant_user(client, db_session, unique_login_id, unique_email):
    admin_login = "admin" + unique_login_id[-5:]
    admin = User(
        login_id=admin_login,
        email="admin-" + unique_email,
        password_hash=hash_password(VALID_PASSWORD),
        role=UserRole.ADMIN,
    )
    db_session.add(admin)
    db_session.commit()

    token = client.post(
        "/api/v1/auth/login",
        json={"login_id": admin_login, "password": VALID_PASSWORD},
    ).json()["access_token"]

    resp = client.post(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "login_id": unique_login_id,
            "email": unique_email,
            "password": VALID_PASSWORD,
            "role": "accountant",
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["role"] == "accountant"


def test_admin_create_user_rejects_contact_role(client, db_session):
    resp_payload = {
        "login_id": "contact1",
        "email": "contact1@example.com",
        "password": VALID_PASSWORD,
        "role": "contact",
    }
    # Even without auth, schema validation (422) should fire before the
    # 401/403 auth dependency would -- but to specifically prove the
    # *role* restriction (not just "no token"), authenticate as admin.
    admin = User(
        login_id="roleadmin1",
        email="roleadmin1@example.com",
        password_hash=hash_password(VALID_PASSWORD),
        role=UserRole.ADMIN,
    )
    db_session.add(admin)
    db_session.commit()

    token = client.post(
        "/api/v1/auth/login",
        json={"login_id": "roleadmin1", "password": VALID_PASSWORD},
    ).json()["access_token"]

    resp = client.post(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {token}"},
        json=resp_payload,
    )
    assert resp.status_code == 422
