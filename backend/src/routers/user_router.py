# routers/user_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import EmailStr
from dtos.user import UserCreate, UserUpdate, UserRead

from db.async_session import get_db

from services.user_service import (
    UserService,
    EmailAlreadyExistsError,
    UserNotFoundError,
)

router = APIRouter(prefix="/users", tags=["users"])


# ---------- Dependency ----------

#don't need to create a DI container for this just now, since we are just importing session. for python DI container, we will have to define the
#scope and the "recipe" for the service (what all dependencies it needs to be constructed). for now, we can just use Depends to inject the session into the service.
def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)


# ---------- Routes ----------

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
):
    try:
        return await service.register_user(
            email=payload.email,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("", response_model=list[UserRead])
async def list_users(service: UserService = Depends(get_user_service)):
    return await service.list_users()


@router.get("/by-email", response_model=UserRead | None)
async def get_user_by_email(
    email: EmailStr,
    service: UserService = Depends(get_user_service),
):
    return await service.get_user_by_email(email)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    try:
        return await service.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
):
    updates = payload.model_dump(exclude_unset=True)
    try:
        return await service.update_user(user_id, **updates)
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    try:
        await service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))