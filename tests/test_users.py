from fastapi import status
from fastapi.testclient import TestClient


def test_create_user(client: TestClient):
    payload = {
        "username": "test_user",
        "email": "test.user@example.com",
        "password": "password",
    }
    response = client.post("/api/v1/users/", json=payload)
    created_user = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert created_user["username"] == "test_user"
    assert created_user["email"] == "test.user@example.com"
    assert "id" in created_user
    assert "password" not in created_user
