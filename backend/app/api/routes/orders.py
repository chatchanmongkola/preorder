from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import MenuItem, Order, OrderItem, Round, RoundStatus, User
from app.schemas.common import APIResponse
from app.schemas.order import OrderCreate, OrderItemIn, OrderItemOut, OrderOut, OrderUpdate
from app.services.round_service import auto_complete_expired_rounds, get_effective_status

router = APIRouter(prefix="/orders", tags=["orders"])


def _to_order_out(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        round_id=order.round_id,
        status=order.status.value,
        note=order.note,
        total_amount=float(order.total_amount),
        items=[
            OrderItemOut(
                id=item.id,
                menu_item_id=item.menu_item_id,
                name=item.menu_item.name,
                quantity=item.quantity,
                price_snapshot=float(item.price_snapshot),
            )
            for item in order.items
        ],
    )


def _price_items(
    db: Session, round_id: int, items_in: list[OrderItemIn]
) -> tuple[list[tuple[MenuItem, int, float]], float]:
    """Validate items belong to the round and compute totals server-side.
    Never trust a price sent by the client."""
    if not items_in:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ต้องมีอย่างน้อย 1 รายการในออเดอร์")

    menu_item_ids = [i.menu_item_id for i in items_in]
    menu_by_id = {m.id: m for m in db.query(MenuItem).filter(MenuItem.id.in_(menu_item_ids)).all()}

    priced_items: list[tuple[MenuItem, int, float]] = []
    total = 0.0
    for item_in in items_in:
        menu_item = menu_by_id.get(item_in.menu_item_id)
        if menu_item is None or menu_item.round_id != round_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"เมนู id={item_in.menu_item_id} ไม่ได้อยู่ในรอบนี้",
            )
        price = float(menu_item.price)
        total += price * item_in.quantity
        priced_items.append((menu_item, item_in.quantity, price))

    return priced_items, total


def _get_open_round_or_400(db: Session, round_id: int) -> Round:
    round_ = db.get(Round, round_id)
    if round_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบรอบนี้")
    if get_effective_status(round_) != RoundStatus.OPEN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="รอบนี้ปิดรับออเดอร์แล้ว")
    return round_


def _get_own_order_or_404(db: Session, order_id: int, user: User) -> Order:
    order = db.get(Order, order_id)
    if order is None or order.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบออเดอร์นี้")
    return order


@router.post("", response_model=APIResponse[OrderOut], status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    round_ = _get_open_round_or_400(db, payload.round_id)

    existing = (
        db.query(Order)
        .filter(Order.user_id == current_user.id, Order.round_id == round_.id)
        .one_or_none()
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="คุณสั่งออเดอร์ในรอบนี้ไปแล้ว")

    priced_items, total = _price_items(db, round_.id, payload.items)

    order = Order(user_id=current_user.id, round_id=round_.id, note=payload.note, total_amount=total)
    db.add(order)
    db.flush()

    for menu_item, quantity, price in priced_items:
        db.add(OrderItem(order_id=order.id, menu_item_id=menu_item.id, quantity=quantity, price_snapshot=price))

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="คุณสั่งออเดอร์ในรอบนี้ไปแล้ว") from exc

    db.refresh(order)
    return APIResponse(data=_to_order_out(order), message="สั่งออเดอร์สำเร็จ")


@router.get("/my", response_model=APIResponse[list[OrderOut]])
def list_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    auto_complete_expired_rounds(db)
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return APIResponse(data=[_to_order_out(o) for o in orders], message="ok")


@router.patch("/{order_id}", response_model=APIResponse[OrderOut])
def update_order(
    order_id: int,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = _get_own_order_or_404(db, order_id, current_user)
    _get_open_round_or_400(db, order.round_id)  # only editable while round open

    priced_items, total = _price_items(db, order.round_id, payload.items)

    for existing_item in list(order.items):
        db.delete(existing_item)
    db.flush()

    for menu_item, quantity, price in priced_items:
        db.add(OrderItem(order_id=order.id, menu_item_id=menu_item.id, quantity=quantity, price_snapshot=price))

    order.note = payload.note
    order.total_amount = total
    db.commit()
    db.refresh(order)
    return APIResponse(data=_to_order_out(order), message="แก้ไขออเดอร์สำเร็จ")


@router.delete("/{order_id}", response_model=APIResponse[None])
def delete_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = _get_own_order_or_404(db, order_id, current_user)
    _get_open_round_or_400(db, order.round_id)  # only cancellable while round open

    db.delete(order)
    db.commit()
    return APIResponse(data=None, message="ยกเลิกออเดอร์สำเร็จ")
