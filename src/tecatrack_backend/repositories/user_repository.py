import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.models import User
from tecatrack_backend.schemas.user_schemas import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with an asynchronous SQLAlchemy session for
        database operations.

        Parameters:
            session (AsyncSession): Async SQLAlchemy session used by the repository
                for executing queries and persisting entities.
        """
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """
        Retrieve a User by its UUID identifier.

        Parameters:
            user_id (uuid.UUID): The UUID of the user to retrieve.

        Returns:
            User | None: The matching User if found, `None` otherwise.
        """
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a User by exact email address.

        Returns:
            `User` if a matching user exists, `None` otherwise.
        """
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user_create: UserCreate) -> User:
        """
        Create and persist a new User from the given creation schema.

        Parameters:
            user_create (UserCreate): Schema containing fields for the new user.

        Returns:
            User: The persisted User instance with database-generated fields populated.
        """
        db_user = User(**user_create.model_dump())
        self.session.add(db_user)
        await self.session.flush()
        await self.session.refresh(db_user)
        return db_user

    async def update(self, user: User, user_update: UserUpdate) -> User:
        """
        Apply the provided `UserUpdate` fields to an existing `User` instance and
        persist the changes.

        Only fields explicitly set on `user_update` are applied to `user`. The
        repository flushes pending changes and refreshes the instance so
        database-generated values (e.g., default or computed columns) are loaded
        before returning.

        Parameters:
            user (User): The existing user entity to modify.
            user_update (UserUpdate): Partial update data; only set fields will be
                applied.

        Returns:
            User: The updated and refreshed `User` instance.
        """
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """
        Delete the given User from the database and persist the deletion.

        Parameters:
            user (User): The User instance scheduled for removal from the database.
        """
        await self.session.delete(user)
        await self.session.flush()
