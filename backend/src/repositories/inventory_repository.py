from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.inventory_item import InventoryItem


class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, inventory_item_id: int) -> InventoryItem | None:
        return await self.session.get(InventoryItem, inventory_item_id)

    async def get_by_name(self, name: str) -> InventoryItem | None:
        result = await self.session.execute(
            select(InventoryItem).where(InventoryItem.name == name)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[InventoryItem]:
        result = await self.session.execute(select(InventoryItem))
        return list(result.scalars().all())

    async def create(self, name: str, qty_available: int) -> InventoryItem:
        item = InventoryItem(name=name, qty_available=qty_available)
        self.session.add(item)
        await self.session.flush()
        return item

    async def update(self, inventory_item_id: int, **kwargs) -> InventoryItem | None:
        item = await self.get_by_id(inventory_item_id)
        if item is None:
            return None
        for key, value in kwargs.items():
            setattr(item, key, value)
        await self.session.flush()
        return item

    async def delete(self, inventory_item_id: int) -> bool:
        item = await self.session.get(InventoryItem, inventory_item_id)
        if item is None:
            return False
        await self.session.delete(item)
        await self.session.flush()
        return True

    #this is the conditional update method so that one request hit multiple times does not cause race conditions
    # and two people decrementing the same inventory item at the same time does not cause negative inventory (overselling)
    async def atomic_decrement(self, inventory_item_id: int, qty: int) -> bool:
        result = await self.session.execute(
            update(InventoryItem)
            .where(
                InventoryItem.inventory_item_id == inventory_item_id,
                InventoryItem.qty_available >= qty,
            )
            .values(qty_available=InventoryItem.qty_available - qty)
        )
        return result.rowcount > 0