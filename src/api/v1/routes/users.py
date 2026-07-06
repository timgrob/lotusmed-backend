from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.security import hash_password
from src.db.database import get_session
from src.models.user import User as DBUser
from src.schemas.user import User, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, session: SessionDep) -> DBUser:
    user = DBUser(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password.get_secret_value()),
        role=payload.role,
        status=payload.status,
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )
    session.refresh(user)
    return user


@router.put("/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
def update_user(user_id: UUID, payload: UserUpdate, session: SessionDep) -> DBUser:
    if not (user := session.get(DBUser, user_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)
    if (password := update_data.pop("password", None)) is not None:
        user.hashed_password = hash_password(password.get_secret_value())
    for field, value in update_data.items():
        setattr(user, field, value)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, session: SessionDep) -> None:
    if not (user := session.get(DBUser, user_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    session.delete(user)
    session.commit()
