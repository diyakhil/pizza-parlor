from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from models.base import Base
from models.user import User
from sqlalchemy import Numeric

class Cart(Base):
    __tablename__ = "carts"

    cart_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    total_cost: Mapped[float] =  mapped_column(Numeric(10, 2), nullable=False)
    quantity_required: Mapped[int]

    user: Mapped["User"] = relationship()