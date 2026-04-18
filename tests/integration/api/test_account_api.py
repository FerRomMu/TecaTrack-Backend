import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tecatrack_backend.models import Account

# test_create_account_api_success
@pytest.mark.asyncio
async def test_create_account_api_success(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    # 1. Create a user first (Account needs user_id)
    """
    Integration test that verifies the accounts API creates an account and that
    the account is persisted.

    Creates a user, creates an account for that user, asserts the HTTP response is
    201 and contains `bank`, `cbu`, `balance`, and `id`, converts the returned `id`
    to a UUID, and asserts a corresponding `Account` row exists in the database
    with the expected `bank` and a `Decimal('100.50')` balance.
    """
    user_data = {"email": "account_owner@example.com", "full_name": "Account Owner"}
    user_res = await async_client.post("/users/", json=user_data)
    assert user_res.status_code == 201
    user_id = user_res.json()["id"]

    # 2. Create the account
    account_data = {
        "bank": "Teca Bank",
        "balance": "100.50",
        "cbu": "1234567890123456789012",
        "user_id": user_id,
    }

    response = await async_client.post("/accounts/", json=account_data)

    # 3. Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["bank"] == account_data["bank"]
    assert data["cbu"] == account_data["cbu"]
    assert data["balance"] == "100.50"
    assert "id" in data

    # 4. Verify DB
    account_uuid = uuid.UUID(data["id"])
    result = await db_session.execute(select(Account).where(Account.id == account_uuid))
    db_account = result.scalar_one_or_none()
    assert db_account is not None
    assert db_account.bank == account_data["bank"]
    assert db_account.balance == Decimal("100.50")


# test_create_account_invalid_cbu_api
@pytest.mark.asyncio
async def test_create_account_invalid_cbu_api(async_client: AsyncClient) -> None:
    """
    Integration test that verifies the accounts API rejects accounts with invalid CBUs.

    Creates a user, attempts to create an account with an invalid CBU (too short),
    asserts the HTTP response is 400 and contains `detail` message about invalid CBU.
    """
    user_data = {
        "email": "invalid_cbu_owner@example.com",
        "full_name": "Invalid CBU Owner",
    }
    user_res = await async_client.post("/users/", json=user_data)
    assert user_res.status_code == 201
    user_id = user_res.json()["id"]

    # 2. Create the account with invalid CBU
    account_data = {
        "bank": "Teca Bank",
        "balance": "100.50",
        "cbu": "123456789012345678901",
        "user_id": user_id,
    }

    response = await async_client.post("/accounts/", json=account_data)

    # 3. Verify response
    assert response.status_code == 400
    data = response.json()
    assert "Invalid entity structure" in data["detail"]


# test_create_account_duplicate_cbu_api
@pytest.mark.asyncio
async def test_create_account_duplicate_cbu_api(async_client: AsyncClient) -> None:
    # 1. Create a user
    """
    Verifies that creating an account with a CBU already present in the system
    is rejected.

    Creates a user and an account, then attempts to create a second account with
    the same `cbu` and asserts the API responds with HTTP 400 and a `detail`
    message containing "already exists".
    """
    user_data = {"email": "dup_cbu@example.com", "full_name": "Dup CBU"}
    user_res = await async_client.post("/users/", json=user_data)
    user_id = user_res.json()["id"]

    account_data = {
        "bank": "Teca Bank",
        "balance": "0.00",
        "cbu": "9999999999999999999999",
        "user_id": user_id,
    }

    # 2. Create first account
    res1 = await async_client.post("/accounts/", json=account_data)
    assert res1.status_code == 201

    # 3. Attempt duplicate CBU
    res2 = await async_client.post("/accounts/", json=account_data)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()


# test_create_account_non_existent_user_api
@pytest.mark.asyncio
async def test_create_account_non_existent_user_api(async_client: AsyncClient) -> None:
    """
    Verifies that creating an account with a non-existent user is rejected.

    Attempts to create an account with a non-existent user and asserts the API
    responds with HTTP 404 and a `detail` message containing "not found".
    """
    account_data = {
        "bank": "Teca Bank",
        "balance": "0.00",
        "cbu": "9999999999999999999999",
        "user_id": str(uuid.uuid4()),
    }

    response = await async_client.post("/accounts/", json=account_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# test_get_account_api_success
@pytest.mark.asyncio
async def test_get_account_api_success(async_client: AsyncClient) -> None:
    # 1. Create user and account
    """
    Verifies that an account created via the API can be retrieved by its ID and
    that the returned CBU matches the created account.

    Creates a user and an account, performs GET /accounts/{id}, and asserts the
    response status is 200 and the `cbu` field equals the originally provided CBU.
    """
    user_res = await async_client.post(
        "/users/", json={"email": "get_acc@ex.com", "full_name": "Get Acc"}
    )
    user_id = user_res.json()["id"]

    acc_data = {
        "bank": "Bank Inc",
        "balance": "50.00",
        "cbu": "1111111111111111111111",
        "user_id": user_id,
    }
    create_res = await async_client.post("/accounts/", json=acc_data)
    acc_id = create_res.json()["id"]

    # 2. Fetch by ID
    response = await async_client.get(f"/accounts/{acc_id}")
    assert response.status_code == 200
    assert response.json()["cbu"] == acc_data["cbu"]


# test_get_account_api_not_found
@pytest.mark.asyncio
async def test_get_account_api_not_found(async_client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    response = await async_client.get(f"/accounts/{fake_id}")
    assert response.status_code == 404


# test_get_account_by_cbu_api_success
@pytest.mark.asyncio
async def test_get_account_by_cbu_api_success(async_client: AsyncClient) -> None:
    # 1. Create user and account
    """
    Verify that an account can be retrieved by its CBU and the response contains
    the expected bank.

    Creates a user and an account with a known CBU, requests the account by that
    CBU, and asserts the API returns HTTP 200 and the account's `bank` matches
    the created account.
    """
    user_res = await async_client.post(
        "/users/", json={"email": "cbu_acc@ex.com", "full_name": "CBU Acc"}
    )
    user_id = user_res.json()["id"]
    cbu = "2222222222222222222222"

    await async_client.post(
        "/accounts/",
        json={"bank": "CBU Bank", "balance": "0.00", "cbu": cbu, "user_id": user_id},
    )

    # 2. Fetch by CBU
    response = await async_client.get(f"/accounts/cbu/{cbu}")
    assert response.status_code == 200
    assert response.json()["bank"] == "CBU Bank"


# test_get_account_by_cbu_api_not_found
@pytest.mark.asyncio
async def test_get_account_by_cbu_api_not_found(async_client: AsyncClient) -> None:
    """
    Verify that fetching an account by a non-existent CBU returns HTTP 404.

    Attempts to retrieve an account using a CBU that does not exist in the
    database and asserts the API responds with status 404 and a `detail`
    message containing "not found".
    """
    fake_cbu = "9999999999999999999999"
    response = await async_client.get(f"/accounts/cbu/{fake_cbu}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# test_get_accounts_by_user_api_success
@pytest.mark.asyncio
async def test_get_accounts_by_user_api_success(async_client: AsyncClient) -> None:
    # 1. Create user
    """
    Verify that fetching accounts for a specific user returns all created accounts and
    the correct aggregated total balance.

    Creates a user, creates two accounts for that user, calls GET
    /accounts/user/{user_id}, and asserts the response status is 200, the returned
    accounts list contains exactly two entries, and `total_balance` equals
    "300.50".
    """
    user_res = await async_client.post(
        "/users/", json={"email": "user_accs@ex.com", "full_name": "User Accs"}
    )
    user_id = user_res.json()["id"]

    # 2. Create two accounts
    await async_client.post(
        "/accounts/",
        json={
            "bank": "Bank A",
            "balance": "100.00",
            "cbu": "3333333333333333333333",
            "user_id": user_id,
        },
    )
    await async_client.post(
        "/accounts/",
        json={
            "bank": "Bank B",
            "balance": "200.50",
            "cbu": "4444444444444444444444",
            "user_id": user_id,
        },
    )

    # 3. Fetch all accounts for user
    response = await async_client.get(f"/accounts/user/{user_id}")
    assert response.status_code == 200
    data = response.json()

    assert len(data["accounts"]) == 2
    assert data["total_balance"] == "300.50"


# test_get_accounts_by_user_api_not_found
@pytest.mark.asyncio
async def test_get_accounts_by_user_api_not_found(async_client: AsyncClient) -> None:
    """
    Verify that fetching accounts for a non-existent user returns HTTP 404.

    Attempts to retrieve accounts for a non-existent user and asserts the API
    responds with status 404 and a `detail` message containing "not found".
    """
    fake_user_id = str(uuid.uuid4())
    response = await async_client.get(f"/accounts/user/{fake_user_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

# test_get_accounts_by_user_with_no_accounts
@pytest.mark.asyncio
async def test_get_accounts_by_user_with_no_accounts(async_client: AsyncClient) -> None:
    """
    Verify that fetching accounts for a user with no accounts returns an empty list and zero total balance.

    Creates a user with no accounts, calls GET /accounts/user/{user_id}, and asserts the response status is 200,
    the accounts list is empty, and `total_balance` equals "0.00".
    """
    user_res = await async_client.post(
        "/users/", json={"email": "no_accs@ex.com", "full_name": "No Accs"}
    )
    user_id = user_res.json()["id"]

    response = await async_client.get(f"/accounts/user/{user_id}")
    assert response.status_code == 200
    data = response.json()

    assert len(data["accounts"]) == 0
    assert data["total_balance"] == "0.00"