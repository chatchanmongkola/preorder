import pytest

from app.core.config import get_settings
from app.services import telegram_service


@pytest.fixture(autouse=True)
def mock_telegram_api(monkeypatch):
    """Prevent tests from making real calls to the Telegram Bot API.

    Captures all sent messages so tests can assert on them, and no-ops
    the editing/answering functions that aren't worth inspecting at the
    unit-test level.
    """
    sent_messages: list[tuple[str, str | None]] = []

    async def _fake_send(text: str, chat_id: str | None = None) -> None:
        sent_messages.append((text, chat_id))

    async def _fake_send_keyboard(
        text: str, keyboard: list[list[dict]], chat_id: str | None = None
    ) -> dict | None:
        sent_messages.append((text, chat_id))
        return {"message_id": 999}

    async def _fake_edit(*args, **kwargs) -> None:
        pass

    monkeypatch.setattr(telegram_service, "send_message", _fake_send)
    monkeypatch.setattr(telegram_service, "send_message_with_keyboard", _fake_send_keyboard)
    monkeypatch.setattr(telegram_service, "edit_message_text", _fake_edit)
    monkeypatch.setattr(telegram_service, "answer_callback_query", _fake_edit)
    return sent_messages


def _secret_header() -> dict:
    return {"X-Telegram-Bot-Api-Secret-Token": get_settings().TELEGRAM_WEBHOOK_SECRET}


def test_webhook_rejects_missing_secret(client):
    res = client.post("/webhook/telegram", json={"message": {"text": "/status", "chat": {"id": 1}}})
    assert res.status_code == 401


def test_webhook_rejects_wrong_secret(client):
    res = client.post(
        "/webhook/telegram",
        json={"message": {"text": "/status", "chat": {"id": 1}}},
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
    )
    assert res.status_code == 401


def test_webhook_status_command_with_no_rounds(client):
    res = client.post(
        "/webhook/telegram",
        json={"message": {"text": "/status", "chat": {"id": 111}}},
        headers=_secret_header(),
    )
    assert res.status_code == 200
    assert "ยังไม่มีรอบใดๆ" in res.json()["data"]["reply"]


def test_webhook_addmenu_without_open_round(client):
    res = client.post(
        "/webhook/telegram",
        json={"message": {"text": "/addmenu ข้าวผัด 45", "chat": {"id": 111}}},
        headers=_secret_header(),
    )
    assert res.status_code == 200
    assert "ไม่มีรอบที่เปิดอยู่" in res.json()["data"]["reply"]


def test_webhook_open_then_close_sends_summary(client, mock_telegram_api):
    open_res = client.post(
        "/webhook/telegram",
        json={"message": {"text": "/open รอบทดสอบ 2999-01-01 12:00", "chat": {"id": 111}}},
        headers=_secret_header(),
    )
    assert open_res.status_code == 200
    assert "เปิดรอบใหม่แล้ว" in open_res.json()["data"]["reply"]

    close_res = client.post(
        "/webhook/telegram",
        json={"message": {"text": "/close", "chat": {"id": 111}}},
        headers=_secret_header(),
    )
    assert close_res.status_code == 200
    assert "ปิดรอบ" in close_res.json()["data"]["reply"]

    # /close should trigger an auto-summary broadcast in addition to the reply.
    assert any("สรุปยอด" in call_text for call_text, _chat_id in mock_telegram_api)


def test_webhook_ignores_callback_query_without_orders(client, mock_telegram_api):
    """Confirm callback_query for a non-existent order doesn't crash."""
    res = client.post(
        "/webhook/telegram",
        json={
            "callback_query": {
                "id": "cq-1",
                "data": "confirm_order:999",
                "message": {"message_id": 1, "chat": {"id": 111}},
            }
        },
        headers=_secret_header(),
    )
    assert res.status_code == 200


def test_webhook_ignores_non_command_text(client):
    res = client.post(
        "/webhook/telegram",
        json={"message": {"text": "hello there", "chat": {"id": 111}}},
        headers=_secret_header(),
    )
    assert res.status_code == 200
    assert res.json()["message"] == "ignored"


def test_webhook_unknown_command(client):
    res = client.post(
        "/webhook/telegram",
        json={"message": {"text": "/bogus", "chat": {"id": 111}}},
        headers=_secret_header(),
    )
    assert res.status_code == 200
    assert "ไม่รู้จักคำสั่ง" in res.json()["data"]["reply"]
