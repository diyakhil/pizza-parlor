# services/cart_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.cart_repository import CartRepository
from repositories.pizza_repository import PizzaRepository
from models.cart import Cart


class CartNotFoundError(Exception):
    pass


class PizzaNotFoundError(Exception):
    pass


class CartItemNotFoundError(Exception):
    pass


class CartService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.cart_repo = CartRepository(session)
        self.pizza_repo = PizzaRepository(session)

    async def get_or_create_cart(self, user_id: int) -> Cart:
        cart = await self.cart_repo.get_by_user_id(user_id)
        if cart is not None:
            return cart
        return await self.cart_repo.create(user_id=user_id)

    async def add_item(self, user_id: int, pizza_id: int, qty: int) -> Cart:
        pizza = await self.pizza_repo.get_by_id(pizza_id)
        if pizza is None:
            raise PizzaNotFoundError(f"No pizza with id {pizza_id}")

        cart = await self.get_or_create_cart(user_id)

        existing_item = await self.cart_repo.get_cart_item(cart.cart_id, pizza_id)
        if existing_item is not None:
            await self.cart_repo.update_cart_item_qty(
                existing_item.cart_item_id, existing_item.qty + qty
            )
        else:
            await self.cart_repo.add_cart_item(cart.cart_id, pizza_id, qty)

        return await self.cart_repo.get_by_user_id(user_id)

    async def update_item_qty(self, user_id: int, cart_item_id: int, qty: int) -> Cart:
        cart = await self.cart_repo.get_by_user_id(user_id)
        if cart is None:
            raise CartNotFoundError(f"No cart for user {user_id}")

        if qty <= 0:
            removed = await self.cart_repo.remove_cart_item(cart_item_id)
            if not removed:
                raise CartItemNotFoundError(f"No cart item with id {cart_item_id}")
        else:
            updated = await self.cart_repo.update_cart_item_qty(cart_item_id, qty)
            if updated is None:
                raise CartItemNotFoundError(f"No cart item with id {cart_item_id}")
        return await self.cart_repo.get_by_user_id(user_id)

    async def remove_item(self, user_id: int, cart_item_id: int) -> Cart:
        cart = await self.cart_repo.get_by_user_id(user_id)
        if cart is None:
            raise CartNotFoundError(f"No cart for user {user_id}")

        removed = await self.cart_repo.remove_cart_item(cart_item_id)
        if not removed:
            raise CartItemNotFoundError(f"No cart item with id {cart_item_id}")
        return await self.cart_repo.get_by_user_id(user_id)
    
    async def get_cart(self, user_id: int) -> Cart:
        cart = await self.cart_repo.get_by_user_id(user_id)
        if cart is None:
            raise CartNotFoundError(f"No cart for user {user_id}")
        return cart

    async def clear_cart(self, user_id: int) -> None:
        cart = await self.cart_repo.get_by_user_id(user_id)
        if cart is None:
            raise CartNotFoundError(f"No cart for user {user_id}")
        await self.cart_repo.delete(cart.cart_id)
        return await self.cart_repo.get_by_user_id(user_id)