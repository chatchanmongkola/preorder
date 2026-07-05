from pydantic import BaseModel


class LineCallbackRequest(BaseModel):
    code: str
    redirect_uri: str | None = None


class DevLoginRequest(BaseModel):
    as_admin: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
