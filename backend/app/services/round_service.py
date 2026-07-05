from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import MenuItem, Order, OrderItem, OrderStatus, Round, RoundStatus
from app.schemas.round import RoundSummaryItem, RoundSummaryOut


def _as_utc(dt: datetime) -> datetime:
    """Postgres (DateTime(timezone=True)) returns tz-aware datetimes, but
    SQLite (used in tests) silently drops tzinfo and returns naive ones.
    Normalize to UTC-aware so comparisons never blow up regardless of DB."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def get_effective_status(round_: Round) -> RoundStatus:
    """Compute the real-time status of a round.

    The stored `status` column is the source of truth once an admin manually
    closes a round (via Telegram `/close`), but a round whose `closes_at` has
    already passed is treated as closed even if nobody closed it yet, and a
    round whose `opens_at` is still in the future is treated as draft.
    """
    if round_.status == RoundStatus.CLOSED:
        return RoundStatus.CLOSED

    now = datetime.now(timezone.utc)
    if now < _as_utc(round_.opens_at):
        return RoundStatus.DRAFT
    if now >= _as_utc(round_.closes_at):
        return RoundStatus.CLOSED
    return RoundStatus.OPEN


def build_round_summary(db: Session, round_: Round) -> RoundSummaryOut:
    """Aggregate orders/order_items for a round. Shared by the REST API and the
    Telegram bot (/summary, /close) so both surfaces always agree on totals."""
    orders = db.query(Order).filter(Order.round_id == round_.id, Order.status != OrderStatus.CANCELLED).all()
    total_amount = sum(float(o.total_amount) for o in orders)

    item_rows = (
        db.query(
            MenuItem.id.label("menu_item_id"),
            MenuItem.name.label("name"),
            func.coalesce(func.sum(OrderItem.quantity), 0).label("quantity"),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.price_snapshot), 0).label("subtotal"),
        )
        .outerjoin(OrderItem, OrderItem.menu_item_id == MenuItem.id)
        .outerjoin(Order, Order.id == OrderItem.order_id)
        .filter(
            MenuItem.round_id == round_.id,
            (Order.id.is_(None)) | (Order.status != OrderStatus.CANCELLED),
        )
        .group_by(MenuItem.id, MenuItem.name)
        .order_by(MenuItem.id)
        .all()
    )
    items = [
        RoundSummaryItem(
            menu_item_id=row.menu_item_id,
            name=row.name,
            quantity=int(row.quantity),
            subtotal=float(row.subtotal),
        )
        for row in item_rows
    ]

    return RoundSummaryOut(
        round_id=round_.id,
        round_name=round_.name,
        status=get_effective_status(round_).value,
        total_orders=len(orders),
        total_amount=total_amount,
        items=items,
    )

