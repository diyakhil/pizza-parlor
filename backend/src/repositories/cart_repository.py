from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.cart import Cart

class CartRepository:
    # this is DI, passing in session to the repository, so that we can use the same session for multiple repositories.
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, cart_id: int) -> Cart | None:
        result = await self.session.execute(
            select(Cart)
            .where(Cart.cart_id == cart_id)
            .options(selectinload(Cart.items))
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Cart | None:
        result = await self.session.execute(
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.items))
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_id: int, total_cost: float, quantity_required: int) -> Cart:
        cart = Cart(
            user_id=user_id,
            total_cost=total_cost,
            quantity_required=quantity_required,
        )
        self.session.add(cart)
        await self.session.flush()
        return cart
    
    async def update(self, cart_id: int, **kwargs) -> Cart | None:
        cart = await self.get_by_id(cart_id)
        if cart is None:
            return None
        for key, value in kwargs.items():
            setattr(cart, key, value)
        await self.session.flush()
        return cart

    async def delete(self, cart_id: int) -> bool:
        cart = await self.session.get(Cart, cart_id)
        if cart is None:
            return False
        await self.session.delete(cart)
        await self.session.flush()
        return True