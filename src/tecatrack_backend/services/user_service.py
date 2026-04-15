import uuid

from tecatrack_backend.exceptions import UserAlreadyExistsError, UserNotFoundError
from tecatrack_backend.models import User
from tecatrack_backend.repositories.user_repository import UserRepository
from tecatrack_backend.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found.")
        return user

    async def get_user_by_email(self, email: str) -> User:
        user = await self.repository.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email {email} not found.")
        return user

    async def create_user(self, user_create: UserCreate) -> User:
        existing_user = await self.repository.get_by_email(user_create.email)
        if existing_user:
            raise UserAlreadyExistsError(
                f"User with email {user_create.email} already exists."
            )
        return await self.repository.create(user_create)

    async def update_user(self, user_id: uuid.UUID, user_update: UserUpdate) -> User:
        user = await self.get_user(user_id)
        return await self.repository.update(user, user_update)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.get_user(user_id)
        await self.repository.delete(user)
