# CLAUDE.md

## General Instructions

Try to explain everything very concisely and without jargon.

## What this project is

A backend for a fictional pizza parlor: users, a menu of pizzas, ingredient inventory,
carts, orders, payments. It is a **personal learning project** — there are no real users,
it will never be deployed, and nothing here needs to be production-grade.

## Why it exists (read this before anything else)

The pizza parlor is a vehicle. **The actual goal is learning system design, specifically
how to work with a queue.** The domain was chosen because it naturally produces the
problems queues exist to solve: an order is placed, but cooking it, charging for it, and
notifying the customer shouldn't all happen inside one blocking HTTP request.

### How Diya wants to work

**Explain concepts and steps. Do not write the code.** This is the default for every request unless she explicitly says "write it" / "implement it" / "just do it."

When asked to add or change something:

1. Explain the concept — what problem this solves, why the pattern exists, what the
   trade-offs are.
2. Lay out the steps she should take, in order, naming the files involved.
3. Point out the gotchas she'll hit (the async/greenlet traps in this codebase are a
   recurring source of them).
4. Stop. Let her write it. Answer follow-ups and review what she wrote if she asks.

Reading the codebase, tracing behavior, diagnosing errors, answering "why does this
happen" — all fine and encouraged. The restriction is on producing implementation code
she asked to learn by writing.

Prefer the simplest thing that works. When a production-grade pattern is worth knowing
about, describe it as "here's what would change if this grew up" rather than building it.
See `~/.claude/projects/.../memory/` for standing decisions on scope.

## Stack

| Piece      | Choice                               | Notes                                       |
| ---------- | ------------------------------------ | ------------------------------------------- |
| Web        | FastAPI + uvicorn                    | async, DI via `Depends`                     |
| ORM        | SQLAlchemy 2.0 (typed `Mapped[...]`) | async engine for the API                    |
| DB         | Postgres                             | two URLs in `.env` — see below              |
| Migrations | Alembic                              | autogenerate from `models.Base.metadata`    |
| Queue      | Celery + Redis                       | broker `redis://…/0`, results `redis://…/1` |
| Validation | Pydantic v2                          | DTOs, `from_attributes=True`                |

### Two database URLs, on purpose

- `DATABASE_URL` → `postgresql+asyncpg://…` — the FastAPI app ([async_session.py](backend/src/db/async_session.py))
- `DATABASE_URL_SYNC` → `postgresql://…` (psycopg2) — Celery workers and Alembic ([sync_session.py](backend/src/db/sync_session.py))

Celery tasks are synchronous functions, and Alembic runs outside an event loop, so
neither can use the async engine. This split is the thing to keep in mind when queue work
starts: **a task cannot reuse the request's session.** It opens its own, via
`sync_session.get_db()`.

## Layout

```
backend/src/
  main.py            FastAPI app; includes the four routers
  routers/           HTTP layer — parse, call a service, map domain errors to status codes
  services/          business logic; owns the domain exceptions
  repositories/      all SQLAlchemy queries; one per aggregate
  models/            ORM tables
  dtos/              Pydantic request/response schemas
  db/                sessions, alembic/, seed.py
  proj/              Celery app + tasks
```

Import paths are **bare** (`from services.user_service import ...`), so `backend/src`
must be the working directory. That's why every Makefile recipe `cd`s into it.

### Layering rule

`router → service → repository → model`. A router never touches a session directly beyond
injecting it; a service never writes a `select()`. Services are constructed with a session
and build their own repositories, so several repos inside one request share one session and
therefore one transaction.

Transactions are owned by the boundary, not the layers: repositories `flush()`,
`get_db()` commits once when the request succeeds and rolls back on any exception.
**A repository never commits.**

## Domain model

```
User ──< Order ──< OrderItem >── Pizza ──< PizzaIngredient >── InventoryItem
  │        └── Payment (1:1)
  └──< Cart ──< CartItem >── Pizza
```

- `OrderItem.unit_price` snapshots the price at order time; `Cart` stores no prices and
  computes nothing — a cart is a wish list, an order is a record.
- `Payment` has a unique `idempotency_key` — the hook for retry-safety once the queue is
  in play.
- Cascades: `Cart→CartItem`, `Order→OrderItem`, `Pizza→PizzaIngredient`,
  `User→Order` are `delete-orphan`. `CartItem.cart_id` also carries a DB-level
  `ondelete="CASCADE"`.
- `InventoryRepository.atomic_decrement` is a conditional `UPDATE … WHERE qty >= n`
  returning `rowcount > 0` — the oversell guard, and the pattern to reach for when two
  workers race on the same row.

## The async gotcha that bites constantly

Under asyncio, touching an unloaded relationship raises `MissingGreenlet`. Two habits in
this codebase exist only because of it:

1. **Repos `selectinload()` collections** they expect callers to serialize
   (`Cart.items`, `Order.items`, `Pizza.ingredients`).
2. **Constructors pass `items=[]` / `ingredients=[]`** on create, which marks the
   collection as loaded so a service can append to it right after the flush.

Consequence for DTOs: a response model may only include a relationship if the repo method
behind that route actually loaded it. `PizzaRead` vs `PizzaDetailRead` is this distinction
made explicit, and `OrderRead` omits `payment` for the same reason.

## Current state

Working: users, pizzas (+ ingredients), carts — full CRUD through router → service → repo.

Not built yet:

- **`OrderService.create_order` / `get_order`** are `NotImplementedError` stubs. The
  routes exist and answer **501**. Three design questions are still open and are Diya's to
  answer: does ordering decrement inventory, does it clear the cart, what is the starting
  `status` string.
- **`services/payment_service.py` is empty.** The agreed shape is immediate capture
  against an in-process fake gateway, no webhooks, no HTTP routes — a step inside
  `create_order`. Diya is implementing this herself; don't write it.
- **The queue is a placeholder.** `proj/tasks.py` contains only `add(x, y)`. Nothing in
  the app enqueues anything. This is the frontier — the whole point of the project starts
  here.
- No tests yet (pytest + pytest-asyncio + httpx are declared in the `dev` extra).
- No auth. `user_id` is a path param or in the request body, which is why
  `cart_router.create_cart` has to validate the user exists by hand — an unknown id would
  otherwise be an FK `IntegrityError` surfacing as a 500.

## Commands

```
make help          list targets
make dev           uvicorn with autoreload (PORT=8001 to override)
make redis-start   brew services start redis   (redis-stop to stop)
make worker        celery -A proj worker -l INFO
make migrate       alembic upgrade head
make revision m="msg"
make seed          python -m db.seed   (run migrate first)
```

Docs at `http://localhost:8000/docs`; health at `/health`.
Seeding is separate from migrations on purpose — Alembic never generates seed data.
