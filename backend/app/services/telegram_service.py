import logging

import httpx

from app.core.config import get_settings
from app.schemas.round import RoundSummaryOut

logger = logging.getLogger(__name__)
settings = get_settings()

TELEGRAM_API_BASE = "https://api.telegram.org"


async def send_message(text: str, chat_id: str | None = None) -> None:
    """ส่งข้อความไปยัง Telegram group ผ่าน Bot API.

    No-ops quietly if the bot isn't configured yet (dev convenience) instead of
    raising, so local flows that don't care about Telegram still work.
    """
    target_chat_id = chat_id or settings.TELEGRAM_CHAT_ID
    if not settings.TELEGRAM_BOT_TOKEN or not target_chat_id:
        return

    url = f"{TELEGRAM_API_BASE}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json={"chat_id": target_chat_id, "text": text})
        if not resp.is_success:
            logger.error(
                "Telegram sendMessage failed: %s %s — chat_id=%s text=%.100s",
                resp.status_code,
                resp.text,
                target_chat_id,
                text,
            )


async def send_message_with_keyboard(
    text: str,
    keyboard: list[list[dict]],
    chat_id: str | None = None,
) -> dict | None:
    """Send message with inline keyboard markup. Returns the API result dict (contains ``message_id``)."""
    target_chat_id = chat_id or settings.TELEGRAM_CHAT_ID
    if not settings.TELEGRAM_BOT_TOKEN or not target_chat_id:
        return None

    url = f"{TELEGRAM_API_BASE}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": target_chat_id,
        "text": text,
        "reply_markup": {"inline_keyboard": keyboard},
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload)
        if not resp.is_success:
            logger.error(
                "Telegram sendMessage (keyboard) failed: %s %s — chat_id=%s",
                resp.status_code,
                resp.text,
                target_chat_id,
            )
            return None
        return resp.json().get("result")


async def edit_message_text(text: str, chat_id: str, message_id: int) -> None:
    url = f"{TELEGRAM_API_BASE}/bot{settings.TELEGRAM_BOT_TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload)
        if not resp.is_success:
            logger.error(
                "Telegram editMessageText failed: %s %s — chat_id=%s msg=%s",
                resp.status_code,
                resp.text,
                chat_id,
                message_id,
            )


async def answer_callback_query(callback_query_id: str) -> None:
    url = f"{TELEGRAM_API_BASE}/bot{settings.TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json=payload)


def format_individual_order(order, round_name: str, confirmed: bool = False) -> str:
    header_name = f"{order.user.display_name} - ออเดอร์ #{order.id}"
    if confirmed:
        header_name += " ✅"
    lines = [f"🧑 {header_name}", ""]
    for item in order.items:
        lines.append(f"📋 {item.menu_item.name} x{item.quantity} ({item.price_snapshot:,.0f} บาท)")
    if order.note:
        lines.append("")
        lines.append(f"📝 หมายเหตุ: {order.note}")
    lines.append("")
    lines.append(f"รวม: {order.total_amount:,.0f} บาท")
    if confirmed:
        lines.append("")
        lines.append("✅ ยืนยันแล้ว")
    return "\n".join(lines)


def _confirm_keyboard(order_id: int) -> list[list[dict]]:
    return [[{"text": "✅ ยืนยัน", "callback_data": f"confirm_order:{order_id}"}]]


def format_round_summary(summary: RoundSummaryOut) -> str:
    """จัดรูปแบบข้อความสรุปยอดภาษาไทยสำหรับส่งเข้า Telegram group."""
    lines = [f"📋 สรุปยอด {summary.round_name}", f"สถานะ: {summary.status}", ""]

    ordered_items = [item for item in summary.items if item.quantity > 0]
    if ordered_items:
        for item in ordered_items:
            lines.append(f"- {item.name} x{item.quantity} = {item.subtotal:,.2f} บาท")
    else:
        lines.append("(ยังไม่มีออเดอร์)")

    lines.append("")
    lines.append(f"จำนวนออเดอร์ทั้งหมด: {summary.total_orders}")
    lines.append(f"ยอดรวมทั้งหมด: {summary.total_amount:,.2f} บาท")
    return "\n".join(lines)
