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


def test_create_user_db(session: Session):
    user_create = UserCreate(
        username="test_user",
        email="test.user@example.com",
        password=SecretStr("password"),
    )

    created_user = create_db_user(user_create, session)
    assert created_user.username == "test_user"
    assert created_user.email == "test.user@example.com"


def test_find_user_db(session: Session):
    db_user = DBUser(
        username="test_user",
        email="test.user@example.com",
        hashed_password="hashed",
    )
    session.add(db_user)
    session.commit()

    found_user = find_db_user(db_user.id, session)
    assert found_user.id == db_user.id
    assert found_user.username == "test_user"
    assert found_user.email == "test.user@example.com"


def test_find_user_db_not_found(session: Session):
    with pytest.raises(UserNotFoundError):
        find_db_user(uuid4(), session)


def test_delete_user_db(session: Session):
    db_user = DBUser(
        username="test_user",
        email="test.user@example.com",
        hashed_password="hashed",
    )
    session.add(db_user)
    session.commit()
    user_id = db_user.id

    delete_db_user(user_id, session)

    assert session.get(DBUser, user_id) is None


def test_delete_user_db_not_found(session: Session):
    with pytest.raises(UserNotFoundError):
        delete_db_user(uuid4(), session)


def test_create_user_db_duplicate(session: Session):
    user_create = UserCreate(
        username="test_user",
        email="test.user@example.com",
        password=SecretStr("password"),
    )
    create_db_user(user_create, session)

    with pytest.raises(UserAlreadyExistsError):
        create_db_user(user_create, session)


def test_list_users_db_empty(session: Session):
    assert list_db_users(session) == []


def test_list_users_db(session: Session):
    session.add_all(
        [
            DBUser(username="user_one", email="one@example.com", hashed_password="h"),
            DBUser(username="user_two", email="two@example.com", hashed_password="h"),
        ]
    )
    session.commit()

    users = list_db_users(session)
    assert {user.username for user in users} == {"user_one", "user_two"}


def test_update_user_db(session: Session):
    db_user = DBUser(
        username="test_user",
        email="test.user@example.com",
        hashed_password="hashed",
    )
    session.add(db_user)
    session.commit()

    updated_user = update_db_user(db_user.id, UserUpdate(username="new_name"), session)
    assert updated_user.username == "new_name"
    assert updated_user.email == "test.user@example.com"


def test_update_user_db_password(session: Session):
    db_user = DBUser(
        username="test_user",
        email="test.user@example.com",
        hashed_password="hashed",
    )
    session.add(db_user)
    session.commit()

    update_db_user(db_user.id, UserUpdate(password=SecretStr("new_password")), session)
    assert verify_password("new_password", db_user.hashed_password)


def test_update_user_db_not_found(session: Session):
    with pytest.raises(UserNotFoundError):
        update_db_user(uuid4(), UserUpdate(username="new_name"), session)


def test_update_user_db_duplicate_username(session: Session):
    user_two = DBUser(username="user_two", email="two@example.com", hashed_password="h")
    session.add_all(
        [
            DBUser(username="user_one", email="one@example.com", hashed_password="h"),
            user_two,
        ]
    )
    session.commit()

    with pytest.raises(UserAlreadyExistsError):
        update_db_user(user_two.id, UserUpdate(username="user_one"), session)


def test_update_user_db_duplicate_email(session: Session):
    user_two = DBUser(username="user_two", email="two@example.com", hashed_password="h")
    session.add_all(
        [
            DBUser(username="user_one", email="one@example.com", hashed_password="h"),
            user_two,
        ]
    )
    session.commit()

    with pytest.raises(UserAlreadyExistsError):
        update_db_user(user_two.id, UserUpdate(email="one@example.com"), session)
