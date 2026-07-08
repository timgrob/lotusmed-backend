from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

USERS_URL = "/api/v1/users/"


def create_user(
    client: TestClient,
    username: str = "test_user",
    email: str = "test.user@example.com",
) -> dict:
    response = client.post(
        USERS_URL,
        json={"username": username, "email": email, "password": "password"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


def test_create_user(client: TestClient):
    user = create_user(client)
    assert user["username"] == "test_user"
    assert user["email"] == "test.user@example.com"
    assert "password" not in user
    assert "hashed_password" not in user


def test_create_user_duplicate(client: TestClient):
    create_user(client)

    response = client.post(
        USERS_URL,
        json={
            "username": "test_user",
            "email": "test.user@example.com",
            "password": "password",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_get_user(client: TestClient):
    user = create_user(client)

    response = client.get(f"{USERS_URL}{user['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user


def test_get_user_not_found(client: TestClient):
    response = client.get(f"{USERS_URL}{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_users(client: TestClient):
    create_user(client, username="user_one", email="one@example.com")
    create_user(client, username="user_two", email="two@example.com")

    response = client.get(USERS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert {user["username"] for user in response.json()} == {"user_one", "user_two"}


def test_update_user(client: TestClient):
    user = create_user(client)

    response = client.patch(f"{USERS_URL}{user['id']}", json={"username": "new_name"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "new_name"
    assert response.json()["email"] == "test.user@example.com"


def test_update_user_not_found(client: TestClient):
    response = client.patch(f"{USERS_URL}{uuid4()}", json={"username": "new_name"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_user_ignores_explicit_null(client: TestClient):
    user = create_user(client)

    response = client.patch(f"{USERS_URL}{user['id']}", json={"username": None})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "test_user"


def test_delete_user(client: TestClient):
    user = create_user(client)

    response = client.delete(f"{USERS_URL}{user['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get(f"{USERS_URL}{user['id']}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_not_found(client: TestClient):
    response = client.delete(f"{USERS_URL}{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
