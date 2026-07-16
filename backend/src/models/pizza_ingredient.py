from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from models.base import Base
from models.pizza import Pizza
from models.inventory_item import InventoryItem


class PizzaIngredient(Base):
    __tablename__ = "pizza_ingredients"

    pizza_ingredient_id: Mapped[int] = mapped_column(primary_key=True)
    pizza_id: Mapped[int] = mapped_column(ForeignKey("pizzas.pizza_id"))
    inventory_item_id: Mapped[int] = mapped_column(ForeignKey("inventory_items.inventory_item_id"))
    quantity_required: Mapped[int]

    pizza: Mapped["Pizza"] = relationship(back_populates="ingredients")
    inventory_item: Mapped["InventoryItem"] = relationship()