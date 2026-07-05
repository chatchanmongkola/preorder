from pydantic import BaseModel


class LineCallbackRequest(BaseModel):
    code: str
    redirect_uri: str | None = None


class LiffLoginRequest(BaseModel):
    id_token: str


class DevLoginRequest(BaseModel):
    as_admin: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
