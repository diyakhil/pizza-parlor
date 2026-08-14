# services/order_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.order_repository import OrderRepository
from repositories.cart_repository import CartRepository
from models.order import Order


class OrderNotFoundError(Exception):
    pass


class EmptyCartError(Exception):
    pass


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.cart_repo = CartRepository(session)

    async def create_order(self, user_id: int) -> Order:
        raise NotImplementedError

    async def get_order(self, order_id: int) -> Order:
        raise NotImplementedError
