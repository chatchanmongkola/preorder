from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.services import telegram_commands, telegram_service

router = APIRouter(prefix="/webhook/telegram", tags=["telegram"])
settings = get_settings()


@router.post("")
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if not settings.TELEGRAM_WEBHOOK_SECRET or x_telegram_bot_api_secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret")

    update = await request.json()

    # Handle callback query (inline button clicks).
    if "callback_query" in update:
        cq = update["callback_query"]
        data = cq.get("data", "")
        chat_id = str(cq["message"]["chat"]["id"])
        message_id = cq["message"]["message_id"]

        await telegram_commands.handle_callback_data(db, data, chat_id, message_id)
        await telegram_service.answer_callback_query(cq["id"])
        return {"data": None, "error": None, "message": "ok"}

    message = update.get("message") or {}
    text = message.get("text", "")
    chat_id = str(message.get("chat", {}).get("id", "")) or None

    if not text.startswith("/"):
        return {"data": None, "error": None, "message": "ignored"}

    reply = await telegram_commands.handle_command(db, text, chat_id=chat_id)
    if chat_id:
        await telegram_service.send_message(reply, chat_id=chat_id)

    return {"data": {"reply": reply}, "error": None, "message": "ok"}
