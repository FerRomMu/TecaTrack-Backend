import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.models import User


@pytest.mark.asyncio
async def test_create_user_api_success(
    async_client: AsyncClient, db_session: AsyncSession
):
    user_data = {"email": "api_test@example.com", "full_name": "API Test User"}

    response = await async_client.post("/users/", json=user_data)

    # 1. Check HTTP response
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data

    # 2. Verify directly against the real database
    user_id = uuid.UUID(data["id"])
    result = await db_session.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    assert db_user is not None
    assert db_user.email == user_data["email"]


@pytest.mark.asyncio
async def test_get_user_api_success(
    async_client: AsyncClient, db_session: AsyncSession
):
    # First, let's create a user to fetch
    user_data = {"email": "fetch_me@example.com", "full_name": "Fetch Test"}
    create_response = await async_client.post("/users/", json=user_data)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    # Now, let's fetch the user by ID
    response = await async_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_get_user_api_not_found(async_client: AsyncClient):
    fake_user_id = str(uuid.uuid4())

    response = await async_client.get(f"/users/{fake_user_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_create_user_already_exists_api(async_client: AsyncClient):
    user_data = {"email": "duplicate@example.com", "full_name": "Duplicate"}

    # 1. Create first user
    response1 = await async_client.post("/users/", json=user_data)
    assert response1.status_code == 201

    # 2. Attempt to create again with the same email
    response2 = await async_client.post("/users/", json=user_data)

    # 3. Assert our domain exception handler returned the 400
    assert response2.status_code == 400
    assert response2.json()["detail"] == "User already exists"
