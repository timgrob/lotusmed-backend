from uuid import UUID

from fastapi import APIRouter, status

from src.api.dependencies import SessionDep
from src.models.user import User as DBUser
from src.repositories.user_operations import (
    create_db_user,
    delete_db_user,
    find_db_user,
    list_db_users,
    update_db_user,
)
from src.schemas.user import User, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, session: SessionDep) -> User:
    return create_db_user(payload, session)


@router.get("/", response_model=list[User])
def list_users(session: SessionDep) -> list[DBUser]:
    return list_db_users(session)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: UUID, session: SessionDep) -> DBUser:
    return find_db_user(user_id, session)


@router.patch("/{user_id}", response_model=User)
def update_user(user_id: UUID, payload: UserUpdate, session: SessionDep) -> User:
    return update_db_user(user_id, payload, session)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, session: SessionDep) -> None:
    delete_db_user(user_id, session)
