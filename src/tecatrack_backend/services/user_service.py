import uuid

from sqlalchemy.exc import IntegrityError

from tecatrack_backend.core.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from tecatrack_backend.models import User
from tecatrack_backend.repositories.user_repository import UserRepository
from tecatrack_backend.schemas.user_schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository):
        """
        Initialize the UserService with a UserRepository.

        The provided repository is used to perform persistence operations for
        user-related actions.
        """
        self.repository = repository

    async def get_user(self, user_id: uuid.UUID) -> User:
        """
        Fetches a user by UUID.

        Parameters:
            user_id (uuid.UUID): UUID of the user to retrieve.

        Returns:
            User: The user with the given UUID.

        Raises:
            EntityNotFoundError: If no user exists with the given `user_id`.
        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)
        return user

    async def get_user_by_email(self, email: str) -> User:
        """
        Retrieve a user by their email address.

        Parameters:
            email (str): The email address of the user to look up.

        Returns:
            user (User): The matching user object.

        Raises:
            EntityNotFoundError: If no user exists with the given email.
        """
        user = await self.repository.get_by_email(email)
        if not user:
            raise EntityNotFoundError("User", email)
        return user

    async def create_user(self, user_create: UserCreate) -> User:
        """
        Create a new user from the supplied creation data.

        Parameters:
            user_create (UserCreate): Creation payload containing the user's email and
            profile fields.

        Returns:
            User: The created user object.

        Raises:
            EntityAlreadyExistsError: If a user with the same email already exists.
        """
        try:
            return await self.repository.create(user_create)
        except IntegrityError as e:
            raise EntityAlreadyExistsError("User", user_create.email) from e

    async def update_user(self, user_id: uuid.UUID, user_update: UserUpdate) -> User:
        """
        Update attributes of an existing user.

        Parameters:
            user_id (uuid.UUID): Identifier of the user to update.
            user_update (UserUpdate): Fields to apply to the user.

        Returns:
            User: The updated user.

        Raises:
            EntityNotFoundError: If no user exists with the given `user_id`.
            EntityAlreadyExistsError: If the update would violate a uniqueness
            constraint (e.g., duplicate email).
        """
        user = await self.get_user(user_id)
        try:
            return await self.repository.update(user, user_update)
        except IntegrityError as exc:
            raise EntityAlreadyExistsError("User", user_id) from exc

    async def delete_user(self, user_id: uuid.UUID) -> None:
        """
        Delete the user identified by the given UUID.

        Parameters:
            user_id (uuid.UUID): UUID of the user to delete.

        Raises:
            EntityNotFoundError: If no user exists with the given `user_id`.
        """
        user = await self.get_user(user_id)
        await self.repository.delete(user)
