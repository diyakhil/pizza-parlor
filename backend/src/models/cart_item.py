from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from models.base import Base
from models.cart import Cart
from models.pizza import Pizza


class CartItem(Base):
    __tablename__ = "cart_items"

    cart_item_id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.cart_id"))
    pizza_id: Mapped[int] = mapped_column(ForeignKey("pizzas.pizza_id"))
    qty: Mapped[int]

    cart: Mapped["Cart"] = relationship(back_populates="items")
    pizza: Mapped["Pizza"] = relationship()