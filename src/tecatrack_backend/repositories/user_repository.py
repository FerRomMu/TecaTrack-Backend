import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.models import User
from tecatrack_backend.schemas.user import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user_create: UserCreate) -> User:
        db_user = User(**user_create.model_dump())
        self.session.add(db_user)
        await self.session.flush()
        await self.session.refresh(db_user)
        return db_user

    async def update(self, user: User, user_update: UserUpdate) -> User:
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.flush()
