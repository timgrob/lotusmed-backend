from uuid import uuid4

import pytest
from fastapi import status
from httpx2 import AsyncClient

pytestmark = pytest.mark.anyio

USERS_URL = "/api/v1/users/"


async def create_user(
    client: AsyncClient,
    first_name: str = "Test",
    last_name: str = "User",
    email: str = "test.user@example.com",
) -> dict:
    response = await client.post(
        USERS_URL,
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": "password",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


async def test_create_user(client: AsyncClient):
    user = await create_user(client)
    assert user["first_name"] == "Test"
    assert user["last_name"] == "User"
    assert user["email"] == "test.user@example.com"
    assert "password" not in user
    assert "hashed_password" not in user


async def test_create_user_duplicate_email(client: AsyncClient):
    await create_user(client)

    response = await client.post(
        USERS_URL,
        json={
            "first_name": "Other",
            "last_name": "Person",
            "email": "test.user@example.com",
            "password": "password",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT


async def test_get_user(client: AsyncClient):
    user = await create_user(client)

    response = await client.get(f"{USERS_URL}{user['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user


async def test_get_user_not_found(client: AsyncClient):
    response = await client.get(f"{USERS_URL}{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_list_users(client: AsyncClient):
    await create_user(client, first_name="One", email="one@example.com")
    await create_user(client, first_name="Two", email="two@example.com")

    response = await client.get(USERS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert {user["first_name"] for user in response.json()} == {"One", "Two"}


async def test_update_user(client: AsyncClient):
    user = await create_user(client)

    response = await client.patch(
        f"{USERS_URL}{user['id']}", json={"first_name": "New"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["first_name"] == "New"
    assert response.json()["last_name"] == "User"


async def test_update_user_not_found(client: AsyncClient):
    response = await client.patch(f"{USERS_URL}{uuid4()}", json={"first_name": "New"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_update_user_ignores_explicit_null(client: AsyncClient):
    user = await create_user(client)

    response = await client.patch(f"{USERS_URL}{user['id']}", json={"first_name": None})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["first_name"] == "Test"


async def test_delete_user(client: AsyncClient):
    user = await create_user(client)

    response = await client.delete(f"{USERS_URL}{user['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await client.get(f"{USERS_URL}{user['id']}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_user_not_found(client: AsyncClient):
    response = await client.delete(f"{USERS_URL}{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
