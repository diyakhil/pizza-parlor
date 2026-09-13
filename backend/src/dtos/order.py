from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    user_id: int  # no auth yet, so the caller states who is ordering


class OrderItemRead(BaseModel):
    order_item_id: int
    pizza_id: int
    qty: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


# payment is deliberately absent: OrderRepository.get_by_id only selectinload()s items,
# so serializing Order.payment would lazy-load and raise MissingGreenlet.
class OrderRead(BaseModel):
    order_id: int
    user_id: int
    total_cost: Decimal
    status: str
    items: list[OrderItemRead] = []

    model_config = ConfigDict(from_attributes=True)
