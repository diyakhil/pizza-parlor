from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Numeric
from models.base import Base
from models.order import Order
from models.pizza import Pizza


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"))
    pizza_id: Mapped[int] = mapped_column(ForeignKey("pizzas.pizza_id"))
    qty: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    pizza: Mapped["Pizza"] = relationship()