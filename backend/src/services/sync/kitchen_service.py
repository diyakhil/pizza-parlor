# services/sync/kitchen_service.py
# Sync service — runs inside a Celery task, not inside a request.
from sqlalchemy import select

from db.sync_session import get_db
from models.kitchen_tickets import KitchenTicket
from models.order import Order
from services.order_service import OrderNotFoundError

# A ticket starts life waiting for a cook to pick it up.
INITIAL_STATUS = "queued"


def create_ticket_for_order(order_id: int) -> int:
    """Open a kitchen ticket for order_id and return its ticket_id.

    Safe to call twice: order_id is unique on kitchen_tickets, so a redelivered
    task returns the existing ticket instead of tripping an IntegrityError.
    """
    with get_db() as session:
        order = session.get(Order, order_id)
        if order is None:
            raise OrderNotFoundError(f"No order with id {order_id}")

        existing = session.execute(
            #order id is not a primary key on kitchen tickets so this is why we use the sql builder instead
            select(KitchenTicket).where(KitchenTicket.order_id == order_id)
        ).scalar_one_or_none()
        if existing is not None:
            return existing.ticket_id

        ticket = KitchenTicket(order_id=order.order_id, status=INITIAL_STATUS)
        session.add(ticket)
        session.flush()
        return ticket.ticket_id
