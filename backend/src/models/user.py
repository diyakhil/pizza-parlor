from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.order import Order

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)

    orders: Mapped[list["Order"]] = relationship(back_populates="user")