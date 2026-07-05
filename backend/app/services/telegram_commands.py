"""Parses and executes Telegram admin bot commands (/status /open /close
/summary /addmenu /listorders). Kept separate from the webhook route so the
command logic can be unit-tested without going through HTTP.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import MenuItem, Order, OrderStatus, Round, RoundStatus
from app.services import telegram_service
from app.services.round_service import auto_complete_expired_rounds, build_round_summary, get_effective_status


def _cmd_status(db: Session) -> str:
    rounds = db.query(Round).order_by(Round.opens_at.desc()).limit(5).all()
    if not rounds:
        return "ยังไม่มีรอบใดๆ ในระบบ"
    lines = ["📊 สถานะรอบล่าสุด:"]
    for r in rounds:
        lines.append(f"- {r.name}: {get_effective_status(r).value}")
    return "\n".join(lines)


def _cmd_open(db: Session, args: list[str]) -> str:
    if len(args) < 2:
        return "รูปแบบคำสั่งไม่ถูกต้อง: /open [ชื่อรอบ] [YYYY-MM-DD HH:MM]"

    name = args[0]
    date_str = " ".join(args[1:])
    try:
        closes_at = datetime.strptime(date_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    except ValueError:
        return "รูปแบบวันที่ไม่ถูกต้อง ใช้ YYYY-MM-DD HH:MM"

    round_ = Round(
        name=name,
        opens_at=datetime.now(timezone.utc),
        closes_at=closes_at,
        status=RoundStatus.OPEN,
    )
    db.add(round_)
    db.commit()
    return f"เปิดรอบใหม่แล้ว: {name} (ปิดรับ {closes_at:%Y-%m-%d %H:%M})"


def _find_latest_active_round(db: Session) -> Round | None:
    rounds = db.query(Round).filter(Round.status != RoundStatus.CLOSED).order_by(Round.opens_at.desc()).all()
    for r in rounds:
        if get_effective_status(r) == RoundStatus.OPEN:
            return r
    return None


async def _cmd_close(db: Session) -> str:
    auto_complete_expired_rounds(db)
    round_ = _find_latest_active_round(db)
    if round_ is None:
        return "ไม่มีรอบที่เปิดอยู่ให้ปิด"

    round_.status = RoundStatus.CLOSED
    db.commit()
    db.refresh(round_)

    summary = build_round_summary(db, round_)
    await telegram_service.send_message(telegram_service.format_round_summary(summary))
    return f"ปิดรอบ {round_.name} แล้ว และส่งสรุปยอดเรียบร้อย"


def _cmd_summary(db: Session) -> str:
    round_ = db.query(Round).order_by(Round.opens_at.desc()).first()
    if round_ is None:
        return "ยังไม่มีรอบใดๆ ในระบบ"
    summary = build_round_summary(db, round_)
    return telegram_service.format_round_summary(summary)


def _cmd_addmenu(db: Session, args: list[str]) -> str:
    if len(args) < 2:
        return "รูปแบบคำสั่งไม่ถูกต้อง: /addmenu [ชื่อเมนู] [ราคา]"

    *name_parts, price_str = args
    name = " ".join(name_parts)
    try:
        price = float(price_str)
    except ValueError:
        return "ราคาต้องเป็นตัวเลข"

    round_ = _find_latest_active_round(db)
    if round_ is None:
        return "ไม่มีรอบที่เปิดอยู่ ไม่สามารถเพิ่มเมนูได้"

    existing_count = db.query(MenuItem).filter(MenuItem.round_id == round_.id).count()
    sku = f"SKU-{round_.id}-{existing_count + 1:03d}"
    db.add(MenuItem(round_id=round_.id, sku=sku, name=name, price=price))
    db.commit()
    return f"เพิ่มเมนู {name} ราคา {price:,.2f} บาท ในรอบ {round_.name} แล้ว"


def _cmd_listorders(db: Session) -> str:
    round_ = db.query(Round).order_by(Round.opens_at.desc()).first()
    if round_ is None:
        return "ยังไม่มีรอบใดๆ ในระบบ"

    orders = (
        db.query(Order)
        .filter(Order.round_id == round_.id, Order.status != OrderStatus.CANCELLED)
        .all()
    )
    if not orders:
        return f"รอบ {round_.name} ยังไม่มีออเดอร์"

    lines = [f"📦 ออเดอร์ในรอบ {round_.name} ({len(orders)} รายการ):"]
    for o in orders:
        lines.append(f"- ออเดอร์ #{o.id} โดย {o.user.display_name}: {o.total_amount:,.2f} บาท")
    return "\n".join(lines)


async def handle_command(db: Session, text: str) -> str:
    parts = text.strip().split()
    if not parts:
        return "คำสั่งไม่ถูกต้อง"

    command, *args = parts

    if command == "/status":
        return _cmd_status(db)
    if command == "/open":
        return _cmd_open(db, args)
    if command == "/close":
        return await _cmd_close(db)
    if command == "/summary":
        return _cmd_summary(db)
    if command == "/addmenu":
        return _cmd_addmenu(db, args)
    if command == "/listorders":
        return _cmd_listorders(db)

    return f"ไม่รู้จักคำสั่ง: {command}"
