from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    inventory_item_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    qty_available: Mapped[int] = mapped_column(nullable=False)