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

    async def create(self, user_id: int) -> Cart:
        cart = Cart(user_id=user_id, items=[])
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

    # takes the Cart itself, not cart_id: appending through the relationship lets
    # SQLAlchemy fill in cart_id at flush AND keeps cart.items correct in memory, so
    # callers can return the cart directly instead of re-querying it. Setting the FK by
    # hand does the insert but leaves an already-loaded cart.items stale.
    async def add_cart_item(self, cart: Cart, pizza_id: int, qty: int) -> CartItem:
        cart_item = CartItem(pizza_id=pizza_id, qty=qty)
        cart.items.append(cart_item)
        await self.session.flush()
        return cart_item

    async def update_cart_item_qty(self, cart_item_id: int, qty: int) -> CartItem | None:
        cart_item = await self.session.get(CartItem, cart_item_id)
        if cart_item is None:
            return None
        cart_item.qty = qty
        await self.session.flush()
        return cart_item

    async def remove_cart_item(self, cart: Cart, cart_item_id: int) -> bool:
        cart_item = next(
            (i for i in cart.items if i.cart_item_id == cart_item_id), None
        )
        if cart_item is None:
            return False
        cart.items.remove(cart_item)
        await self.session.delete(cart_item)
        await self.session.flush()
        return True