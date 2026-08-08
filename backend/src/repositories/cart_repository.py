from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.cart import Cart
from models.cart_item import CartItem
from decimal import Decimal

class CartRepository:
    # this is DI, passing in session to the repository, so that we can use the same session for multiple repositories.
    def __init__(self, session: AsyncSession):
        self.session = session

    # --- Cart CRUD ---

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

    async def create(self, user_id: int, total_cost: Decimal) -> Cart:
        cart = Cart(user_id=user_id, total_cost=total_cost)
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

    # --- CartItem CRUD ---

    async def get_cart_item_by_id(self, cart_item_id: int) -> CartItem | None:
        return await self.session.get(CartItem, cart_item_id)

    async def get_cart_item(self, cart_id: int, pizza_id: int) -> CartItem | None:
        result = await self.session.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.pizza_id == pizza_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_cart_items(self, cart_id: int) -> list[CartItem]:
        result = await self.session.execute(
            select(CartItem).where(CartItem.cart_id == cart_id)
        )
        return list(result.scalars().all())

    async def add_cart_item(self, cart_id: int, pizza_id: int, qty: int) -> CartItem:
        cart_item = CartItem(cart_id=cart_id, pizza_id=pizza_id, qty=qty)
        self.session.add(cart_item)
        await self.session.flush()
        return cart_item

    async def update_cart_item_qty(self, cart_item_id: int, qty: int) -> CartItem | None:
        cart_item = await self.session.get(CartItem, cart_item_id)
        if cart_item is None:
            return None
        cart_item.qty = qty
        await self.session.flush()
        return cart_item

    async def remove_cart_item(self, cart_item_id: int) -> bool:
        cart_item = await self.session.get(CartItem, cart_item_id)
        if cart_item is None:
            return False
        await self.session.delete(cart_item)
        await self.session.flush()
        return True