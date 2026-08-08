# services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user_repository import UserRepository
from models.user import User


class EmailAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register_user(self, email: str, first_name: str, last_name: str) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            raise EmailAlreadyExistsError(f"A user with email {email} already exists")

        return await self.user_repo.create(
            email=email, first_name=first_name, last_name=last_name
        )

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"No user with id {user_id}")
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repo.get_by_email(email)

    async def list_users(self) -> list[User]:
        return await self.user_repo.list_all()

    async def update_user(self, user_id: int, **kwargs) -> User:
        # if email is being changed, enforce uniqueness here too
        if "email" in kwargs:
            existing = await self.user_repo.get_by_email(kwargs["email"])
            if existing is not None and existing.user_id != user_id:
                raise EmailAlreadyExistsError(f"A user with email {kwargs['email']} already exists")

        user = await self.user_repo.update(user_id, **kwargs)
        if user is None:
            raise UserNotFoundError(f"No user with id {user_id}")
        return user

    async def delete_user(self, user_id: int) -> None:
        deleted = await self.user_repo.delete(user_id)
        if not deleted:
            raise UserNotFoundError(f"No user with id {user_id}")