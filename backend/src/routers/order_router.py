# routers/order_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.async_session import get_db
from dtos.order import OrderCreate, OrderRead

from services.order_service import (
    OrderService,
    OrderNotFoundError,
    EmptyCartError,
    PaymentFailedError,
    InsufficientInventoryError,
)

router = APIRouter(prefix="/orders", tags=["orders"])


# ---------- Dependency ----------

def get_order_service(session: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(session)


# ---------- Routes ----------

# NOTE: OrderService.get_order is still a `raise NotImplementedError` stub, so GET
# answers 501. create_order is implemented.
@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.create_order(payload.user_id)
    except EmptyCartError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InsufficientInventoryError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PaymentFailedError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(e)
        )


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
):
    try:
        return await service.get_order(order_id)
    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotImplementedError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="OrderService.get_order is not implemented yet",
        )
