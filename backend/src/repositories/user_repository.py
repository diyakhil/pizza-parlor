from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[User]:
        result = await self.session.execute(select(User))
        return list(result.scalars().all())

    async def create(self, email: str, first_name: str, last_name: str) -> User:
        user = User(email=email, first_name=first_name, last_name=last_name)
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user_id: int, **kwargs) -> User | None:
        user = await self.session.get(User, user_id)
        if user is None:
            return None
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.session.flush()
        return user

    async def delete(self, user_id: int) -> bool:
        user = await self.session.get(User, user_id)
        if user is None:
            return False
        await self.session.delete(user)
        await self.session.flush()
        return True