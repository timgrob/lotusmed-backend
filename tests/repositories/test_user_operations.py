from pydantic import SecretStr
from sqlalchemy.orm import Session

from src.schemas.user import UserCreate
from src.repositories.user_operations import create_db_user


def test_create_user_db(session: Session):
    user_create = UserCreate(
        username="test_user",
        email="test.user@example.com",
        password=SecretStr("password"),
    )

    created_user = create_db_user(user_create, session)
    assert created_user.username == "test_user"
    assert created_user.email == "test.user@example.com"
