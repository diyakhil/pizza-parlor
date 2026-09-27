# services/order_service.py
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.order_repository import OrderRepository
from repositories.cart_repository import CartRepository
from repositories.pizza_repository import PizzaRepository
from models.order import Order
from models.order_item import OrderItem
from services.payment_gateway import PaymentGateway


class OrderNotFoundError(Exception):
    pass


class EmptyCartError(Exception):
    pass


class PaymentFailedError(Exception):
    pass


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.cart_repo = CartRepository(session)
        self.pizza_repo = PizzaRepository(session)
        self.gateway = PaymentGateway()

    async def create_order(self, user_id: int) -> Order:
        #get the user's cart based on their user_id
        cart = await self.cart_repo.get_by_user_id(user_id)
        if cart is None or not cart.items:
            raise EmptyCartError(f"No items in cart for user {user_id}")

        #create a user's order based on the cart items
        line_items: list[tuple[int, int, Decimal]] = []
        total_cost = Decimal("0.00")
        for item in cart.items:
            pizza = await self.pizza_repo.get_by_id(item.pizza_id)
            line_items.append((item.pizza_id, item.qty, pizza.price))
            total_cost += pizza.price * item.qty

        #save the order in the db
        order = await self.order_repo.create(user_id=user_id, total_cost=total_cost)
        for pizza_id, qty, unit_price in line_items:
            order.items.append(
                OrderItem(pizza_id=pizza_id, qty=qty, unit_price=unit_price)
            )

        #call charge in the payment gateway with the order total and an idempotency key
        charged = self.gateway.charge(
            amount=float(total_cost),
            idempotency_key=f"order-{order.order_id}",
        )

        #if charge fails, rollback transaction and return an error
        if not charged:
            raise PaymentFailedError(f"Payment declined for user {user_id}")

        #if the charge is successful, update the order status to "placed", return the order, and empty the cart
        order.status = "placed"
        for item in list(cart.items):
            await self.cart_repo.remove_cart_item(cart, item.cart_item_id)
        await self.session.flush()
        return order

    async def get_order(self, order_id: int) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id} not found")
        return order
