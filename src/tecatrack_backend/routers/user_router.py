import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.core.database import get_db
from tecatrack_backend.repositories.user_repository import UserRepository
from tecatrack_backend.schemas.user import UserCreate, UserRead, UserUpdate
from tecatrack_backend.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserService:
    repository = UserRepository(session)
    return UserService(repository)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    return await service.create_user(user_create)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: uuid.UUID,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    return await service.get_user(user_id)


@router.get("/email/{email}", response_model=UserRead)
async def get_user_by_email(
    email: str,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    return await service.get_user_by_email(email)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    return await service.update_user(user_id, user_update)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    await service.delete_user(user_id)
