from datetime import datetime, timedelta, timezone

from app.core.security import create_access_token
from app.models import MenuItem, Order, OrderItem, OrderStatus, Round, RoundStatus, User, UserRole


def _make_round(db_session, *, opens_delta_hours: float, closes_delta_hours: float, status=RoundStatus.OPEN, name="Test Round") -> Round:
    now = datetime.now(timezone.utc)
    round_ = Round(
        name=name,
        opens_at=now + timedelta(hours=opens_delta_hours),
        closes_at=now + timedelta(hours=closes_delta_hours),
        status=status,
    )
    db_session.add(round_)
    db_session.commit()
    db_session.refresh(round_)
    return round_


def _make_menu_item(db_session, round_: Round, *, sku="T-1", name="Test Item", price=10) -> MenuItem:
    item = MenuItem(round_id=round_.id, sku=sku, name=name, price=price)
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


def _make_user(db_session, *, line_user_id="test-user") -> User:
    user = User(line_user_id=line_user_id, display_name="Test User", role=UserRole.USER)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _auth_header(user: User) -> dict:
    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


def _make_order(db_session, user: User, round_: Round, item: MenuItem, *, quantity=1, status=OrderStatus.PENDING) -> Order:
    order = Order(user_id=user.id, round_id=round_.id, status=status, total_amount=item.price * quantity)
    db_session.add(order)
    db_session.flush()
    db_session.add(OrderItem(order_id=order.id, menu_item_id=item.id, quantity=quantity, price_snapshot=item.price))
    db_session.commit()
    db_session.refresh(order)
    return order


def test_rounds_endpoints_require_authentication(client, db_session):
    round_ = _make_round(db_session, opens_delta_hours=-1, closes_delta_hours=1)

    assert client.get("/rounds/current").status_code == 401
    assert client.get(f"/rounds/{round_.id}").status_code == 401
    assert client.get(f"/rounds/{round_.id}/summary").status_code == 401


def test_current_round_returns_404_when_none_open(client, db_session):
    user = _make_user(db_session)
    # Only a draft (not yet open) and a closed round exist - neither counts as "current".
    _make_round(db_session, opens_delta_hours=1, closes_delta_hours=2)
    _make_round(db_session, opens_delta_hours=-3, closes_delta_hours=-1)

    res = client.get("/rounds/current", headers=_auth_header(user))
    assert res.status_code == 404


def test_current_round_returns_the_open_round(client, db_session):
    user = _make_user(db_session)
    _make_round(db_session, opens_delta_hours=1, closes_delta_hours=2, name="Future Draft")
    open_round = _make_round(db_session, opens_delta_hours=-1, closes_delta_hours=1, name="Open Round")

    res = client.get("/rounds/current", headers=_auth_header(user))
    assert res.status_code == 200
    body = res.json()["data"]
    assert body["id"] == open_round.id
    assert body["status"] == "open"


def test_current_round_computes_closed_status_even_if_db_status_stale(client, db_session):
    # closes_at already passed, but the stored `status` column was never manually updated -
    # get_effective_status() must still report it as closed and current should 404.
    user = _make_user(db_session)
    _make_round(db_session, opens_delta_hours=-3, closes_delta_hours=-1, status=RoundStatus.OPEN)

    res = client.get("/rounds/current", headers=_auth_header(user))
    assert res.status_code == 404


def test_get_round_by_id_not_found(client, db_session):
    user = _make_user(db_session)
    res = client.get("/rounds/999999", headers=_auth_header(user))
    assert res.status_code == 404


def test_get_round_by_id_returns_round(client, db_session):
    user = _make_user(db_session)
    round_ = _make_round(db_session, opens_delta_hours=-1, closes_delta_hours=1)

    res = client.get(f"/rounds/{round_.id}", headers=_auth_header(user))
    assert res.status_code == 200
    assert res.json()["data"]["name"] == round_.name


def test_round_summary_not_found(client, db_session):
    user = _make_user(db_session)
    res = client.get("/rounds/999999/summary", headers=_auth_header(user))
    assert res.status_code == 404


def test_round_summary_aggregates_orders_and_excludes_cancelled(client, db_session):
    round_ = _make_round(db_session, opens_delta_hours=-1, closes_delta_hours=1)
    item_a = _make_menu_item(db_session, round_, sku="A", name="Item A", price=50)
    item_b = _make_menu_item(db_session, round_, sku="B", name="Item B", price=30)

    user1 = _make_user(db_session, line_user_id="user-1")
    user2 = _make_user(db_session, line_user_id="user-2")
    user3 = _make_user(db_session, line_user_id="user-3")

    _make_order(db_session, user1, round_, item_a, quantity=2)  # 100
    _make_order(db_session, user2, round_, item_b, quantity=1)  # 30
    _make_order(db_session, user3, round_, item_a, quantity=5, status=OrderStatus.CANCELLED)  # excluded

    res = client.get(f"/rounds/{round_.id}/summary", headers=_auth_header(user1))
    assert res.status_code == 200
    body = res.json()["data"]

    assert body["total_orders"] == 2
    assert body["total_amount"] == 130.0

    items_by_name = {i["name"]: i for i in body["items"]}
    assert items_by_name["Item A"]["quantity"] == 2
    assert items_by_name["Item A"]["subtotal"] == 100.0
    assert items_by_name["Item B"]["quantity"] == 1
    assert items_by_name["Item B"]["subtotal"] == 30.0


def test_round_summary_includes_zero_order_menu_items(client, db_session):
    round_ = _make_round(db_session, opens_delta_hours=-1, closes_delta_hours=1)
    _make_menu_item(db_session, round_, sku="Z", name="No Orders Item", price=99)

    user = _make_user(db_session)
    res = client.get(f"/rounds/{round_.id}/summary", headers=_auth_header(user))

    assert res.status_code == 200
    body = res.json()["data"]
    items_by_name = {i["name"]: i for i in body["items"]}
    assert items_by_name["No Orders Item"]["quantity"] == 0
    assert items_by_name["No Orders Item"]["subtotal"] == 0
