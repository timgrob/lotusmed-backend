from fastapi import status
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app=app)


def test_root():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Application is running"}
