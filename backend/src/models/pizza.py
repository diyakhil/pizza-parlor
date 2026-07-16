from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base
from decimal import Decimal
from sqlalchemy import Numeric

class Pizza(Base):
    __tablename__ = "pizzas"

    pizza_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)