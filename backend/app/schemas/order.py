from pydantic import BaseModel, ConfigDict, Field


class OrderItemIn(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    round_id: int
    items: list[OrderItemIn]
    note: str | None = None


class OrderUpdate(BaseModel):
    items: list[OrderItemIn]
    note: str | None = None


class OrderItemOut(BaseModel):
    id: int
    menu_item_id: int
    name: str
    quantity: int
    price_snapshot: float


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    round_id: int
    status: str
    note: str | None
    total_amount: float
    items: list[OrderItemOut]
