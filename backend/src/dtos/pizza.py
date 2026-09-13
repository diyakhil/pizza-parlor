from decimal import Decimal
from pydantic import BaseModel, ConfigDict


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


class PizzaIngredientRead(BaseModel):
    pizza_ingredient_id: int
    inventory_item_id: int
    quantity_required: int

    model_config = ConfigDict(from_attributes=True)


# two read DTOs on purpose: PizzaRead is safe to return from ANY endpoint, because it
# never touches a relationship. PizzaDetailRead includes ingredients, so it may only be
# used by endpoints whose repo method selectinload()s them — otherwise serializing would
# trigger a lazy load outside the async greenlet context and raise MissingGreenlet.
class PizzaRead(BaseModel):
    pizza_id: int
    name: str
    price: Decimal

    model_config = ConfigDict(from_attributes=True)


class PizzaDetailRead(PizzaRead):
    ingredients: list[PizzaIngredientRead] = []
