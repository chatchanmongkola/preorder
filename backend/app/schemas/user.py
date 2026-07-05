from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    line_user_id: str
    display_name: str
    picture_url: str | None = None
    role: str
