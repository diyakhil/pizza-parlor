"""Celery task definitions — the queue's entry points.

A task makes a piece of work enqueueable: `create_order` calls `.delay(...)` on
one of these, which drops a message on Redis and returns immediately, so the slow
parts (email, kitchen dispatch) happen in a worker instead of the HTTP request.

Tasks are plain sync functions — they run outside the event loop, so the sync
services they call open their own session. Pass IDs, not ORM objects since it is stored in redis as text; the worker
re-fetches the row. Keep the bodies trivial: one call into `services/sync/`.
The name is what makes the task discoverable by Celery.
"""

from .celery import app
from services.sync.notification_service import send_order_confirmation
from services.sync.kitchen_service import create_ticket_for_order


@app.task(name="notifications.send_order_confirmation", ignore_result=True)
def send_order_confirmation_task(order_id: int) -> None:
    send_order_confirmation(order_id)

@app.task(name="kitchen.create_ticket_for_order", ignore_result=True)
def create_ticket_for_order_task(order_id: int) -> None:
    create_ticket_for_order(order_id)
