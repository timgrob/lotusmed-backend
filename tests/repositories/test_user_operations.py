from uuid import uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy.orm import Session

from src.core.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.core.security import verify_password
from src.models.user import User as DBUser
from src.schemas.user import UserCreate, UserUpdate
from src.repositories.user_operations import (
    create_db_user,
    delete_db_user,
    find_db_user,
    list_db_users,
    update_db_user,
)


def add_db_user(
    session: Session,
    first_name: str = "Test",
    last_name: str = "User",
    email: str = "test.user@example.com",
) -> DBUser:
    db_user = DBUser(
        first_name=first_name,
        last_name=last_name,
        email=email,
        hashed_password="hashed",
    )
    session.add(db_user)
    session.commit()
    return db_user


def test_create_user_db(session: Session):
    user_create = UserCreate(
        first_name="Test",
        last_name="User",
        email="test.user@example.com",
        password=SecretStr("password"),
    )

    created_user = create_db_user(user_create, session)
    assert created_user.first_name == "Test"
    assert created_user.last_name == "User"
    assert created_user.email == "test.user@example.com"


def test_create_user_db_duplicate_email(session: Session):
    add_db_user(session)
    user_create = UserCreate(
        first_name="Other",
        last_name="Person",
        email="test.user@example.com",
        password=SecretStr("password"),
    )

    with pytest.raises(UserAlreadyExistsError):
        create_db_user(user_create, session)


def test_find_user_db(session: Session):
    db_user = add_db_user(session)

    found_user = find_db_user(db_user.id, session)
    assert found_user.id == db_user.id
    assert found_user.first_name == "Test"
    assert found_user.last_name == "User"
    assert found_user.email == "test.user@example.com"


def test_find_user_db_not_found(session: Session):
    with pytest.raises(UserNotFoundError):
        find_db_user(uuid4(), session)


def test_list_users_db_empty(session: Session):
    assert list_db_users(session) == []


def test_list_users_db(session: Session):
    add_db_user(session, first_name="One", email="one@example.com")
    add_db_user(session, first_name="Two", email="two@example.com")

    users = list_db_users(session)
    assert {user.first_name for user in users} == {"One", "Two"}


def test_update_user_db(session: Session):
    db_user = add_db_user(session)

    updated_user = update_db_user(db_user.id, UserUpdate(first_name="New"), session)
    assert updated_user.first_name == "New"
    assert updated_user.last_name == "User"
    assert updated_user.email == "test.user@example.com"


def test_update_user_db_password(session: Session):
    db_user = add_db_user(session)

    update_db_user(db_user.id, UserUpdate(password=SecretStr("new_password")), session)
    assert verify_password("new_password", db_user.hashed_password)


def test_update_user_db_not_found(session: Session):
    with pytest.raises(UserNotFoundError):
        update_db_user(uuid4(), UserUpdate(first_name="New"), session)


def test_update_user_db_duplicate_email(session: Session):
    add_db_user(session, email="one@example.com")
    user_two = add_db_user(session, email="two@example.com")

    with pytest.raises(UserAlreadyExistsError):
        update_db_user(user_two.id, UserUpdate(email="one@example.com"), session)


def test_delete_user_db(session: Session):
    db_user = add_db_user(session)
    user_id = db_user.id

    delete_db_user(user_id, session)

    assert session.get(DBUser, user_id) is None


def test_delete_user_db_not_found(session: Session):
    with pytest.raises(UserNotFoundError):
        delete_db_user(uuid4(), session)
