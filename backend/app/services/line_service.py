import httpx

from app.core.config import get_settings

settings = get_settings()

LINE_TOKEN_URL = "https://api.line.me/oauth2/v2.1/token"
LINE_VERIFY_URL = "https://api.line.me/oauth2/v2.1/verify"


class LineAuthError(Exception):
    """Raised when the LINE OAuth code exchange or id_token verification fails."""


async def exchange_code_for_profile(code: str, redirect_uri: str) -> dict:
    """แลก authorization code จาก LINE Login เป็นข้อมูลโปรไฟล์ผู้ใช้ (sub, name, picture).

    Uses LINE's own /verify endpoint to validate the id_token signature/audience,
    so we never need to manage LINE's JWKS ourselves.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        token_res = await client.post(
            LINE_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": settings.LINE_CLIENT_ID,
                "client_secret": settings.LINE_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_res.status_code != 200:
            raise LineAuthError(f"LINE token exchange failed: {token_res.text}")

        id_token = token_res.json().get("id_token")
        if not id_token:
            raise LineAuthError("LINE token response missing id_token")

        return await verify_id_token(id_token)


async def verify_id_token(id_token: str) -> dict:
    """Verify an id_token directly via LINE's verify endpoint and return the profile payload."""
    async with httpx.AsyncClient(timeout=10) as client:
        verify_res = await client.post(
            LINE_VERIFY_URL,
            data={"id_token": id_token, "client_id": settings.LINE_CLIENT_ID},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if verify_res.status_code != 200:
            raise LineAuthError(f"LINE id_token verification failed: {verify_res.text}")

        return verify_res.json()
