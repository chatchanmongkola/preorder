"""Seed the dev database with sample data.

Run inside the backend container:
    docker compose exec backend python -m app.seed
"""
from datetime import datetime, timedelta, timezone

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import MenuItem, Order, OrderItem, Round, RoundStatus, User, UserRole


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Seed data already present, skipping.")
            return

        now = datetime.now(timezone.utc)

        admin = User(line_user_id="dev-admin-line-id", display_name="แอดมิน (dev)", role=UserRole.ADMIN)
        customer = User(line_user_id="dev-user-line-id", display_name="ลูกค้า (dev)", role=UserRole.USER)
        db.add_all([admin, customer])
        db.flush()

        round_ = Round(
            name="รอบที่ 1",
            opens_at=now - timedelta(hours=1),
            closes_at=now + timedelta(days=1),
            status=RoundStatus.OPEN,
        )
        db.add(round_)
        db.flush()

        menu_items = [
            MenuItem(round_id=round_.id, sku="SKU-001", name="ข้าวกะเพราหมู", price=50),
            MenuItem(round_id=round_.id, sku="SKU-002", name="ข้าวผัดกุ้ง", price=60),
            MenuItem(round_id=round_.id, sku="SKU-003", name="ต้มยำกุ้ง", price=80),
            MenuItem(round_id=round_.id, sku="SKU-004", name="ส้มตำไทย", price=45),
            MenuItem(round_id=round_.id, sku="SKU-005", name="ชาไทยเย็น", price=25),
        ]
        db.add_all(menu_items)
        db.flush()

        order = Order(user_id=customer.id, round_id=round_.id, total_amount=120)
        db.add(order)
        db.flush()

        db.add_all(
            [
                OrderItem(order_id=order.id, menu_item_id=menu_items[0].id, quantity=1, price_snapshot=50),
                OrderItem(order_id=order.id, menu_item_id=menu_items[4].id, quantity=1, price_snapshot=25),
                OrderItem(order_id=order.id, menu_item_id=menu_items[3].id, quantity=1, price_snapshot=45),
            ]
        )

        db.commit()
        print("Seed data created: 2 users, 1 open round, 5 menu items, 1 sample order.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
