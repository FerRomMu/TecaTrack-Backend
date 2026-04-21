import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.models import User


@pytest.mark.asyncio
async def test_create_user_api_success(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Verifies that POST /users/ creates a user, returns the expected response
    fields, and persists the user in the database.

    Sends a POST request with user data, asserts a 201 status and that the
    response JSON contains the same email and an `id`, converts the returned `id`
    to a UUID, queries the database for that user, and asserts the record exists
    with the expected email.
    """
    user_data = {
        "email": "api_test@example.com",
        "full_name": "API Test User",
        "cuil": "11111111111",
    }

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
) -> None:
    # First, let's create a user to fetch
    user_data = {
        "email": "fetch_me@example.com",
        "full_name": "Fetch Test",
        "cuil": "22222222222",
    }
    create_response = await async_client.post("/users/", json=user_data)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    # Now, let's fetch the user by ID
    response = await async_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_get_user_api_not_found(async_client: AsyncClient) -> None:
    """
    Check that fetching a nonexistent user returns HTTP 404.

    Sends a GET request to /users/{id} using a random UUID and asserts the
    response status code is 404.
    """
    fake_user_id = str(uuid.uuid4())

    response = await async_client.get(f"/users/{fake_user_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_user_already_exists_api(async_client: AsyncClient) -> None:
    """
    Check that creating a user with an email that already exists results in a 400
    response on the second request.

    Sends two POST requests to /users/ with identical payload; asserts the first returns
    HTTP 201 and the second returns HTTP 400.
    """
    user_data = {
        "email": "duplicate@example.com",
        "full_name": "Duplicate",
        "cuil": "33333333333",
    }

    # 1. Create first user
    response1 = await async_client.post("/users/", json=user_data)
    assert response1.status_code == 201

    # 2. Attempt to create again with the same email
    response2 = await async_client.post("/users/", json=user_data)

    # 3. Assert our domain exception handler returned the 400
    assert response2.status_code == 400
