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
