from app.api.routes import auth as auth_routes
from app.core.security import create_access_token, decode_access_token
from app.models import User, UserRole
from app.services.line_service import LineAuthError


def test_dev_login_issues_valid_jwt_for_user_and_admin(client):
    user_res = client.post("/auth/dev-login", json={"as_admin": False})
    admin_res = client.post("/auth/dev-login", json={"as_admin": True})

    assert user_res.status_code == 200
    assert admin_res.status_code == 200

    user_payload = decode_access_token(user_res.json()["data"]["access_token"])
    admin_payload = decode_access_token(admin_res.json()["data"]["access_token"])
    assert user_payload is not None and admin_payload is not None
    assert user_payload["sub"] != admin_payload["sub"]


def test_dev_login_reuses_same_seeded_user_on_repeat_calls(client):
    first = client.post("/auth/dev-login", json={"as_admin": False})
    second = client.post("/auth/dev-login", json={"as_admin": False})

    first_sub = decode_access_token(first.json()["data"]["access_token"])["sub"]
    second_sub = decode_access_token(second.json()["data"]["access_token"])["sub"]
    assert first_sub == second_sub


def test_dev_login_disabled_in_production(client, monkeypatch):
    monkeypatch.setattr(auth_routes.settings, "ENVIRONMENT", "production")

    res = client.post("/auth/dev-login", json={"as_admin": False})
    assert res.status_code == 404


def test_me_requires_authentication(client):
    res = client.get("/auth/me")
    assert res.status_code == 401


def test_me_rejects_invalid_token(client):
    res = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401


def test_me_rejects_token_for_deleted_user(client):
    # A structurally valid JWT whose subject no longer exists in the DB must not authenticate.
    token = create_access_token(subject="999999")
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401


def test_me_returns_current_user_profile(client, db_session):
    user = User(line_user_id="line-123", display_name="Somchai", role=UserRole.USER)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(subject=str(user.id))
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 200
    body = res.json()["data"]
    assert body["display_name"] == "Somchai"
    assert body["line_user_id"] == "line-123"


def test_line_callback_success_creates_new_user(client, monkeypatch):
    async def fake_exchange(code, redirect_uri):
        return {"sub": "line-abc", "name": "New User", "picture": "http://example.com/pic.jpg"}

    monkeypatch.setattr(auth_routes, "exchange_code_for_profile", fake_exchange)

    res = client.post("/auth/line/callback", json={"code": "auth-code-123"})
    assert res.status_code == 200
    assert "access_token" in res.json()["data"]


def test_line_callback_reuses_existing_user_by_line_id(client, monkeypatch, db_session):
    existing = User(line_user_id="line-existing", display_name="Old Name", role=UserRole.USER)
    db_session.add(existing)
    db_session.commit()
    db_session.refresh(existing)

    async def fake_exchange(code, redirect_uri):
        return {"sub": "line-existing", "name": "Updated Name", "picture": None}

    monkeypatch.setattr(auth_routes, "exchange_code_for_profile", fake_exchange)

    res = client.post("/auth/line/callback", json={"code": "auth-code-456"})
    assert res.status_code == 200

    token = res.json()["data"]["access_token"]
    payload = decode_access_token(token)
    assert payload["sub"] == str(existing.id)

    db_session.refresh(existing)
    assert existing.display_name == "Updated Name"


def test_line_callback_returns_400_on_line_auth_error(client, monkeypatch):
    async def fake_exchange(code, redirect_uri):
        raise LineAuthError("bad code")

    monkeypatch.setattr(auth_routes, "exchange_code_for_profile", fake_exchange)

    res = client.post("/auth/line/callback", json={"code": "bad-code"})
    assert res.status_code == 400
