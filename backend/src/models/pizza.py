from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from decimal import Decimal
from sqlalchemy import Numeric

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.pizza_ingredient import PizzaIngredient

class Pizza(Base):
    __tablename__ = "pizzas"

    pizza_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    ingredients: Mapped[list["PizzaIngredient"]] = relationship(back_populates="pizza")
