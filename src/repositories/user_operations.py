from uuid import UUID

from sqlalchemy.orm import Session

from src.core.exceptions import UserNotFoundError
from src.core.security import hash_password
from src.models.user import User as DBUser
from src.schemas.user import User, UserCreate


def create_db_user(user: UserCreate, session: Session) -> User:
    db_user = DBUser(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password.get_secret_value()),
        role=user.role,
        status=user.status,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return User.model_validate(db_user, from_attributes=True)


def find_db_user(user_id: UUID, session: Session) -> DBUser:
    db_user = session.query(DBUser).filter(DBUser.id == user_id).first()
    if db_user is None:
        raise UserNotFoundError(f"User not found: {user_id=}")
    return db_user


def delete_db_user(user_id: UUID, session: Session) -> None:
    db_user = find_db_user(user_id, session)
    session.delete(db_user)
    session.commit()
