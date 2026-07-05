from datetime import datetime, timedelta, timezone

from app.core.security import create_access_token
from app.models import MenuItem, Round, RoundStatus, User, UserRole


def _make_round(db_session, *, opens_delta_hours: float, closes_delta_hours: float) -> tuple[Round, MenuItem]:
    now = datetime.now(timezone.utc)
    round_ = Round(
        name="Test Round",
        opens_at=now + timedelta(hours=opens_delta_hours),
        closes_at=now + timedelta(hours=closes_delta_hours),
        status=RoundStatus.OPEN,
    )
    db_session.add(round_)
    db_session.flush()

    item = MenuItem(round_id=round_.id, sku="T-1", name="Test Item", price=10)
    db_session.add(item)
    db_session.commit()
    db_session.refresh(round_)
    db_session.refresh(item)
    return round_, item


def _make_user(db_session) -> User:
    user = User(line_user_id="test-user", display_name="Test User", role=UserRole.USER)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _auth_header(user: User) -> dict:
    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


def test_create_order_computes_total_server_side(client, db_session):
    round_, item = _make_round(db_session, opens_delta_hours=-1, closes_delta_hours=1)
    user = _make_user(db_session)

    res = client.post(
        "/orders",
        # client sends a bogus higher quantity but price must come from the server's menu item, not the client
        json={"round_id": round_.id, "items": [{"menu_item_id": item.id, "quantity": 2}]},
        headers=_auth_header(user),
    )

    assert res.status_code == 201
    body = res.json()["data"]
    assert body["total_amount"] == 20.0
    assert body["items"][0]["price_snapshot"] == 10.0


def test_duplicate_order_in_same_round_rejected(client, db_session):
    round_, item = _make_round(db_session, opens_delta_hours=-1, closes_delta_hours=1)
    user = _make_user(db_session)
    headers = _auth_header(user)
    payload = {"round_id": round_.id, "items": [{"menu_item_id": item.id, "quantity": 1}]}

    first = client.post("/orders", json=payload, headers=headers)
    assert first.status_code == 201

    second = client.post("/orders", json=payload, headers=headers)
    assert second.status_code == 409


def test_order_rejected_when_round_closed(client, db_session):
    round_, item = _make_round(db_session, opens_delta_hours=-2, closes_delta_hours=-1)
    user = _make_user(db_session)

    res = client.post(
        "/orders",
        json={"round_id": round_.id, "items": [{"menu_item_id": item.id, "quantity": 1}]},
        headers=_auth_header(user),
    )

    assert res.status_code == 400


def test_edit_order_rejected_after_round_closed(client, db_session):
    round_, item = _make_round(db_session, opens_delta_hours=-2, closes_delta_hours=1)
    user = _make_user(db_session)
    headers = _auth_header(user)

    create_res = client.post(
        "/orders",
        json={"round_id": round_.id, "items": [{"menu_item_id": item.id, "quantity": 1}]},
        headers=headers,
    )
    order_id = create_res.json()["data"]["id"]

    # Simulate the round closing after the order was placed.
    round_.closes_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    res = client.patch(
        f"/orders/{order_id}",
        json={"items": [{"menu_item_id": item.id, "quantity": 3}]},
        headers=headers,
    )
    assert res.status_code == 400


def test_order_item_must_belong_to_the_round(client, db_session):
    round_, _item = _make_round(db_session, opens_delta_hours=-1, closes_delta_hours=1)
    other_round, other_item = _make_round(db_session, opens_delta_hours=-1, closes_delta_hours=1)
    user = _make_user(db_session)

    res = client.post(
        "/orders",
        json={"round_id": round_.id, "items": [{"menu_item_id": other_item.id, "quantity": 1}]},
        headers=_auth_header(user),
    )
    assert res.status_code == 400
