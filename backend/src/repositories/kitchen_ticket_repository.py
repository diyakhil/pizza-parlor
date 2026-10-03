from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.kitchen_tickets import KitchenTicket
from models.order import Order


class KitchenTicketRepository:
    # this is DI, passing in session to the repository, so that we can use the same session for multiple repositories.
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, ticket_id: int) -> KitchenTicket | None:
        return await self.session.get(KitchenTicket, ticket_id)

    async def get_by_order_id(self, order_id: int) -> KitchenTicket | None:
        result = await self.session.execute(
            select(KitchenTicket).where(KitchenTicket.order_id == order_id)
        )
        return result.scalar_one_or_none()

    # the ticket on its own says nothing about what to cook, so this loads the order
    async def get_with_order(self, ticket_id: int) -> KitchenTicket | None:
        result = await self.session.execute(
            select(KitchenTicket)
            .where(KitchenTicket.ticket_id == ticket_id)
            .options(selectinload(KitchenTicket.order).selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def list_by_status(self, status: str) -> list[KitchenTicket]:
        result = await self.session.execute(
            select(KitchenTicket)
            .where(KitchenTicket.status == status)
            .order_by(KitchenTicket.created_at)
        )
        return list(result.scalars().all())

    async def create(self, order_id: int, status: str = "queued") -> KitchenTicket:
        ticket = KitchenTicket(order_id=order_id, status=status)
        self.session.add(ticket)
        await self.session.flush()
        return ticket

    async def update(self, ticket_id: int, **kwargs) -> KitchenTicket | None:
        ticket = await self.get_by_id(ticket_id)
        if ticket is None:
            return None
        for key, value in kwargs.items():
            setattr(ticket, key, value)
        await self.session.flush()
        return ticket

    async def delete(self, ticket_id: int) -> bool:
        ticket = await self.session.get(KitchenTicket, ticket_id)
        if ticket is None:
            return False
        await self.session.delete(ticket)
        await self.session.flush()
        return True
