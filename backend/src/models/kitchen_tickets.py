from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, String, func
from models.base import Base
from models.order import Order


class KitchenTicket(Base):
    __tablename__ = "kitchen_tickets"

    ticket_id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.order_id"), unique=True, nullable=False
    )

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    order: Mapped["Order"] = relationship()
