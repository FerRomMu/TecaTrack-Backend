import uuid

from tecatrack_backend.core.exceptions import UserAlreadyExistsError, UserNotFoundError
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
        Retrieve a user by their UUID.

        Parameters:
            user_id (uuid.UUID): The UUID of the user to retrieve.

        Returns:
            User: The user matching the provided UUID.

        Raises:
            UserNotFoundError: If no user exists with the given `user_id`.
        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found.")
        return user

    async def get_user_by_email(self, email: str) -> User:
        """
        Retrieve a user by their email address.

        Parameters:
            email (str): The email address of the user to look up.

        Returns:
            user (User): The matching user object.

        Raises:
            UserNotFoundError: If no user exists with the given email.
        """
        user = await self.repository.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email {email} not found.")
        return user

    async def create_user(self, user_create: UserCreate) -> User:
        """
        Create a new user from the provided creation data.

        Parameters:
            user_create (UserCreate): Data required to create the user, including email
                and other profile fields.

        Returns:
            User: The newly created user object.

        Raises:
            UserAlreadyExistsError: If a user with the same email already exists.
        """
        existing_user = await self.repository.get_by_email(user_create.email)
        if existing_user:
            raise UserAlreadyExistsError(
                f"User with email {user_create.email} already exists."
            )
        return await self.repository.create(user_create)

    async def update_user(self, user_id: uuid.UUID, user_update: UserUpdate) -> User:
        """
        Update an existing user's attributes.

        Parameters:
            user_id (uuid.UUID): The unique identifier of the user to update.
            user_update (UserUpdate): Fields to apply to the user.

        Returns:
            User: The updated user.

        Raises:
            UserNotFoundError: If no user exists with the given `user_id`.
        """
        user = await self.get_user(user_id)
        return await self.repository.update(user, user_update)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        """
        Delete the user identified by the given UUID.

        Parameters:
            user_id (uuid.UUID): UUID of the user to delete.

        Raises:
            UserNotFoundError: If no user exists with the given `user_id`.
        """
        user = await self.get_user(user_id)
        await self.repository.delete(user)
