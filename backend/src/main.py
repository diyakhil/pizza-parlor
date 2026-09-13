# main.py — FastAPI application entrypoint
from fastapi import FastAPI

from routers.user_router import router as user_router
from routers.pizza_router import router as pizza_router
from routers.cart_router import router as cart_router
from routers.order_router import router as order_router

app = FastAPI(title="Pizza Parlor", version="0.1.0")

# each router already carries its own prefix and tags
app.include_router(user_router)
app.include_router(pizza_router)
app.include_router(cart_router)
app.include_router(order_router)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}
