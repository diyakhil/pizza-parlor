from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.payment import Payment


class PaymentRepository:
    # this is DI, passing in session to the repository, so that we can use the same session for multiple repositories.
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, payment_id: int) -> Payment | None:
        return await self.session.get(Payment, payment_id)

    async def get_by_order_id(self, order_id: int) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalar_one_or_none()

    # the lookup that makes the idempotency key worth having: before charging, ask whether
    # this key was already attempted.
    async def get_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    # status defaults to "pending" because the row is inserted BEFORE the gateway call —
    # the caller updates it once the outcome is known.
    async def create(
        self,
        order_id: int,
        total_cost: Decimal,
        idempotency_key: str,
        status: str = "pending",
    ) -> Payment:
        payment = Payment(
            order_id=order_id,
            total_cost=total_cost,
            idempotency_key=idempotency_key,
            status=status,
        )
        self.session.add(payment)
        await self.session.flush()
        return payment
