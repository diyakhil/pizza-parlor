# routers/cart_router.py
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.async_session import get_db
from dtos.cart import CartItemCreate, CartItemQtyUpdate, CartRead

from services.cart_service import (
    CartService,
    CartNotFoundError,
    CartItemNotFoundError,
    PizzaNotFoundError,
)
from services.user_service import UserService, UserNotFoundError

# there is no auth layer yet, so user_id is a path param rather than coming from a token
router = APIRouter(prefix="/carts", tags=["carts"])


# ---------- Dependency ----------

def get_cart_service(session: AsyncSession = Depends(get_db)) -> CartService:
    return CartService(session)


# FastAPI caches get_db per request, so both services below share one session and
# therefore one transaction
def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)


# ---------- Routes ----------

# get-or-create, so it is idempotent: 201 when a cart is actually created, 200 when the
# user already had one. CartService.get_or_create_cart cannot tell us which happened,
# so we probe first — the probe doubles as the response on the already-exists path.
@router.post("/{user_id}", response_model=CartRead, status_code=status.HTTP_201_CREATED)
async def create_cart(
    user_id: int,
    response: Response,
    service: CartService = Depends(get_cart_service),
    user_service: UserService = Depends(get_user_service),
):
    try:
        cart = await service.get_cart(user_id)
        response.status_code = status.HTTP_200_OK
        return cart
    except CartNotFoundError:
        pass

    # carts.user_id is a FK, so an unknown user_id would otherwise surface as an
    # IntegrityError -> 500. CartService does not check the user exists, and with no auth
    # layer the router is the only place that knows user_id is unvalidated input.
    try:
        await user_service.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    await service.get_or_create_cart(user_id)
    # re-read rather than returning get_or_create_cart's value: on the create path it
    # returns the freshly flushed Cart, whose items collection is not loaded, and
    # serializing CartRead.items would then lazy-load outside the greenlet context
    return await service.get_cart(user_id)


# every CartService method below returns the cart via cart_repo.get_by_user_id, which
# selectinload()s items — so CartRead can safely include the nested items collection
@router.get("/{user_id}", response_model=CartRead)
async def get_cart(
    user_id: int,
    service: CartService = Depends(get_cart_service),
):
    try:
        return await service.get_cart(user_id)
    except CartNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# add_item creates the cart on demand, so this doubles as "create cart".
# 200 rather than 201 because the resource returned is the cart, which may already exist.
@router.post("/{user_id}/items", response_model=CartRead)
async def add_item(
    user_id: int,
    payload: CartItemCreate,
    service: CartService = Depends(get_cart_service),
):
    try:
        return await service.add_item(
            user_id=user_id,
            pizza_id=payload.pizza_id,
            qty=payload.qty,
        )
    except PizzaNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{user_id}/items/{cart_item_id}", response_model=CartRead)
async def update_item_qty(
    user_id: int,
    cart_item_id: int,
    payload: CartItemQtyUpdate,
    service: CartService = Depends(get_cart_service),
):
    try:
        return await service.update_item_qty(
            user_id=user_id,
            cart_item_id=cart_item_id,
            qty=payload.qty,
        )
    except CartNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CartItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{user_id}/items/{cart_item_id}", response_model=CartRead)
async def remove_item(
    user_id: int,
    cart_item_id: int,
    service: CartService = Depends(get_cart_service),
):
    try:
        return await service.remove_item(user_id=user_id, cart_item_id=cart_item_id)
    except CartNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CartItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# clear_cart deletes the Cart row itself (cart_items go with it via the
# delete-orphan cascade), so there is no cart left to return -> 204
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    user_id: int,
    service: CartService = Depends(get_cart_service),
):
    try:
        await service.clear_cart(user_id)
    except CartNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
