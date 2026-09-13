from pydantic import BaseModel, ConfigDict, Field


class CartItemCreate(BaseModel):
    pizza_id: int
    qty: int = Field(gt=0)  # adding must be positive; use PATCH to decrement or remove


class CartItemQtyUpdate(BaseModel):
    qty: int  # qty <= 0 removes the item — CartService.update_item_qty handles that


class CartItemRead(BaseModel):
    cart_item_id: int
    pizza_id: int
    qty: int

    model_config = ConfigDict(from_attributes=True)


class CartRead(BaseModel):
    cart_id: int
    user_id: int
    items: list[CartItemRead] = []

    model_config = ConfigDict(from_attributes=True)
