from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from models.base import Base
from models.user import User
from sqlalchemy import Numeric

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.cart_item import CartItem

class Cart(Base):
    __tablename__ = "carts"

    cart_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))

    user: Mapped["User"] = relationship()

    items: Mapped[list["CartItem"]] = relationship(back_populates="cart", cascade="all, delete-orphan", passive_deletes=True)
