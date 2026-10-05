# services/sync/notification_service.py
# Sync service — runs inside a Celery task, not inside a request.
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

from db.sync_session import get_db
from models.order import Order
from services.order_service import OrderNotFoundError

load_dotenv()

# Defaults point at a local debug SMTP server (MailHog / aiosmtpd on :1025)
# so nothing real gets sent. Set SMTP_USER + SMTP_PASSWORD to use a real relay.
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", "no-reply@pizzaparlor.test")

SUBJECT = "Pizza Parlor - Thanks for your order!"


def _build_body(order: Order) -> str:
    """Render the email body. Must be called while the session is still open —
    it walks order.items and item.pizza, which lazy-load."""
    lines = [
        "Thank you for placing your order at pizza parlor. "
        f"You are order number {order.order_id}. "
        "We will notify you when your order is ready",
        "",
        "Your order:",
    ]

    for item in order.items:
        line_total = item.unit_price * item.qty
        lines.append(
            f"  {item.qty} x {item.pizza.name}"
            f" @ ${item.unit_price:.2f} = ${line_total:.2f}"
        )

    lines += ["", f"Total: ${order.total_cost:.2f}"]
    return "\n".join(lines)


def send_order_confirmation(order_id: int) -> None:
    """Email the confirmation for order_id to the user who placed it."""
    with get_db() as session:
        order = session.get(Order, order_id)
        if order is None:
            raise OrderNotFoundError(f"No order with id {order_id}")

        recipient = order.user.email
        body = _build_body(order)

    message = EmailMessage()
    message["Subject"] = SUBJECT
    message["From"] = SMTP_FROM
    message["To"] = recipient
    message.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        if SMTP_USER and SMTP_PASSWORD:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(message)
