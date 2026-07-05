from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoundOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    opens_at: datetime
    closes_at: datetime
    status: str


class MenuItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    round_id: int
    sku: str
    name: str
    price: float


class RoundSummaryItem(BaseModel):
    menu_item_id: int
    name: str
    quantity: int
    subtotal: float


class RoundSummaryOut(BaseModel):
    round_id: int
    round_name: str
    status: str
    total_orders: int
    total_amount: float
    items: list[RoundSummaryItem]
