from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Numeric, String
from models.base import Base
from models.order import Order


class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"))
    total_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    idempotency_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="payment")