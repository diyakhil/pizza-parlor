from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from sqlalchemy import ForeignKey
from models.user import User
from sqlalchemy import Numeric

class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    total_cost: Mapped[float] =  mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship()

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")
    payment: Mapped["Payment"] = relationship(back_populates="order")