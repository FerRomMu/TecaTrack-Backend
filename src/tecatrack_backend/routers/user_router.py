import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.core.database import get_db
from tecatrack_backend.repositories.user_repository import UserRepository
from tecatrack_backend.schemas.user_schemas import UserCreate, UserRead, UserUpdate
from tecatrack_backend.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserService:
    """
    Constructs a UserService backed by a UserRepository using the provided
    database session.

    Returns:
        UserService: A service instance configured with a UserRepository that uses
            the given AsyncSession.
    """
    repository = UserRepository(session)
    return UserService(repository)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """
    Create a new user from the provided payload.

    Parameters:
        user_create (UserCreate): Data required to create the user.

    Returns:
        UserRead: The created user representation.
    """
    return await service.create_user(user_create)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: uuid.UUID,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """
    Retrieve a user by UUID.

    Returns:
        UserRead: The user's data as a `UserRead` model.
    """
    return await service.get_user(user_id)


@router.get("/email/{email}", response_model=UserRead)
async def get_user_by_email(
    email: str,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """
    Retrieve a user by their email address.

    Parameters:
        email (str): Email address of the user to retrieve.

    Returns:
        UserRead: The user matching the given email.
    """
    return await service.get_user_by_email(email)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """
    Apply partial updates to an existing user identified by `user_id`.

    Parameters:
        user_id (uuid.UUID): UUID of the user to update.
        user_update (UserUpdate): Fields to update on the user; only provided fields
            will be changed.

    Returns:
        UserRead: The updated user representation.
    """
    return await service.update_user(user_id, user_update)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    """
    Delete the user identified by the given UUID.

    Parameters:
        user_id (uuid.UUID): UUID of the user to delete.
    """
    await service.delete_user(user_id)
