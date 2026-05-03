from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.models.user import User, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

USERS_DB: dict[UUID, User] = {}


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate) -> User:
    user = User(**payload.model_dump())
    USERS_DB[user.id] = user
    return user


@router.put("/{user_id}", response_model=User)
def update_user(user_id: UUID, payload: UserUpdate) -> User:
    if not (current_user := USERS_DB.get(user_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)
    updated_user = current_user.model_copy(update=update_data)
    updated_user.updated_at = datetime.now(datetime.UTC)
    USERS_DB[user_id] = updated_user
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID) -> None:
    if user_id not in USERS_DB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    del USERS_DB[user_id]
