from decimal import Decimal
from pydantic import BaseModel


class PizzaIngredientCreate(BaseModel):
    inventory_item_id: int
    quantity_required: int


class PizzaCreate(BaseModel):
    name: str
    price: Decimal
    ingredients: list[PizzaIngredientCreate] = []

class PizzaUpdate(BaseModel):
    name: str | None = None
    price: Decimal | None = None