# routers/pizza_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.async_session import get_db
from dtos.pizza import PizzaCreate, PizzaUpdate, PizzaRead, PizzaDetailRead

from services.pizza_service import (
    PizzaService,
    PizzaNotFoundError,
    PizzaNameAlreadyExistsError,
)

router = APIRouter(prefix="/pizzas", tags=["pizzas"])


# ---------- Dependency ----------

def get_pizza_service(session: AsyncSession = Depends(get_db)) -> PizzaService:
    return PizzaService(session)


# ---------- Routes ----------

# PizzaDetailRead is safe here now: add_ingredient appends through the relationship, so
# the Pizza that create_pizza returns has its ingredients collection populated in memory
@router.post("", response_model=PizzaDetailRead, status_code=status.HTTP_201_CREATED)
async def create_pizza(
    payload: PizzaCreate,
    service: PizzaService = Depends(get_pizza_service),
):
    try:
        return await service.create_pizza(
            name=payload.name,
            price=payload.price,
            ingredients=payload.ingredients,
        )
    except PizzaNameAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("", response_model=list[PizzaDetailRead])
async def list_pizzas(service: PizzaService = Depends(get_pizza_service)):
    return await service.list_pizzas()


# must be declared before /{pizza_id}, otherwise FastAPI matches the literal
# "by-name" against the int path param and 422s
@router.get("/by-name", response_model=PizzaRead | None)
async def get_pizza_by_name(
    name: str,
    service: PizzaService = Depends(get_pizza_service),
):
    return await service.get_pizza_by_name(name)


@router.get("/{pizza_id}", response_model=PizzaDetailRead)
async def get_pizza(
    pizza_id: int,
    service: PizzaService = Depends(get_pizza_service),
):
    try:
        return await service.get_pizza(pizza_id)
    except PizzaNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{pizza_id}", response_model=PizzaRead)
async def update_pizza(
    pizza_id: int,
    payload: PizzaUpdate,
    service: PizzaService = Depends(get_pizza_service),
):
    # PizzaService.update_pizza takes the DTO and does exclude_unset itself,
    # unlike UserService.update_user which takes **kwargs
    try:
        return await service.update_pizza(pizza_id, payload)
    except PizzaNameAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PizzaNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{pizza_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pizza(
    pizza_id: int,
    service: PizzaService = Depends(get_pizza_service),
):
    try:
        await service.delete_pizza(pizza_id)
    except PizzaNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
