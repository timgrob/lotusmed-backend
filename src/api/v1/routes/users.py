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
async def create_user(payload: UserCreate, session: SessionDep) -> DBUser:
    return await create_db_user(payload, session)


@router.get("/", response_model=list[User])
async def list_users(session: SessionDep) -> list[DBUser]:
    return await list_db_users(session)


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: UUID, session: SessionDep) -> DBUser:
    return await find_db_user(user_id, session)


@router.patch("/{user_id}", response_model=User)
async def update_user(
    user_id: UUID, payload: UserUpdate, session: SessionDep
) -> DBUser:
    return await update_db_user(user_id, payload, session)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, session: SessionDep) -> None:
    await delete_db_user(user_id, session)
