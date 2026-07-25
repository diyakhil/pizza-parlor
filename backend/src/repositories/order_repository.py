from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.order import Order

class OrderRepository:
    # this is DI, passing in session to the repository, so that we can use the same session for multiple repositories.
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, order_id: int) -> Order | None:
        result = await self.session.execute(
            select(Order)
            .where(Order.order_id == order_id)
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Order | None:
        result = await self.session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, total_cost: float, quantity_required: int) -> Order:
        order = Order(
            user_id=user_id,
            total_cost=total_cost,
            quantity_required=quantity_required,
        )
        self.session.add(order)
        await self.session.flush()
        return order

    async def update(self, order_id: int, **kwargs) -> Order | None:
        order = await self.get_by_id(order_id)
        if order is None:
            return None
        for key, value in kwargs.items():
            setattr(order, key, value)
        await self.session.flush()
        return order

    async def delete(self, order_id: int) -> bool:
        order = await self.session.get(Order, order_id)
        if order is None:
            return False
        await self.session.delete(order)
        await self.session.flush()
        return True