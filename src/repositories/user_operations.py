from uuid import UUID

from sqlalchemy.orm import Session

from src.core.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.core.security import hash_password
from src.models.user import User as DBUser
from src.schemas.user import User, UserCreate, UserUpdate


def _ensure_email_unique(
    session: Session, email: str | None, exclude_id: UUID | None = None
) -> None:
    if email is None:
        return

    query = session.query(DBUser).filter(DBUser.email == email)
    if exclude_id is not None:
        query = query.filter(DBUser.id != exclude_id)
    if query.first() is not None:
        raise UserAlreadyExistsError("Email already exists")


def create_db_user(user: UserCreate, session: Session) -> User:
    _ensure_email_unique(session, user.email)
    db_user = DBUser(
        first_name=user.first_name,
        last_name=user.last_name,
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


def list_db_users(session: Session) -> list[DBUser]:
    return session.query(DBUser).all()


def update_db_user(user_id: UUID, user_update: UserUpdate, session: Session) -> User:
    db_user = find_db_user(user_id, session)
    update_data = user_update.model_dump(exclude_unset=True, exclude_none=True)
    _ensure_email_unique(session, update_data.get("email"), exclude_id=user_id)
    if (password := update_data.pop("password", None)) is not None:
        db_user.hashed_password = hash_password(password.get_secret_value())
    for field, value in update_data.items():
        setattr(db_user, field, value)
    session.commit()
    session.refresh(db_user)
    return User.model_validate(db_user, from_attributes=True)


def delete_db_user(user_id: UUID, session: Session) -> None:
    db_user = find_db_user(user_id, session)
    session.delete(db_user)
    session.commit()
