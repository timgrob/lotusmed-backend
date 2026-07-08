import asyncio
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.core.security import hash_password
from src.models.user import User as DBUser
from src.schemas.user import User, UserCreate, UserUpdate


async def _ensure_email_unique(
    session: AsyncSession, email: str | None, exclude_id: UUID | None = None
) -> None:
    if email is None:
        return

    stmt = select(DBUser).where(DBUser.email == email)
    if exclude_id is not None:
        stmt = stmt.where(DBUser.id != exclude_id)
    if (await session.scalars(stmt)).first() is not None:
        raise UserAlreadyExistsError("Email already exists")


async def create_db_user(user: UserCreate, session: AsyncSession) -> User:
    await _ensure_email_unique(session, user.email)
    hashed_password = await asyncio.to_thread(
        hash_password, user.password.get_secret_value()
    )
    db_user = DBUser(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        status=user.status,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return User.model_validate(db_user, from_attributes=True)


async def find_db_user(user_id: UUID, session: AsyncSession) -> DBUser:
    db_user = await session.get(DBUser, user_id)
    if db_user is None:
        raise UserNotFoundError(f"User not found: {user_id=}")
    return db_user


async def list_db_users(session: AsyncSession) -> list[DBUser]:
    return list((await session.scalars(select(DBUser))).all())


async def update_db_user(
    user_id: UUID, user_update: UserUpdate, session: AsyncSession
) -> User:
    db_user = await find_db_user(user_id, session)
    update_data = user_update.model_dump(exclude_unset=True, exclude_none=True)
    await _ensure_email_unique(session, update_data.get("email"), exclude_id=user_id)
    if (password := update_data.pop("password", None)) is not None:
        db_user.hashed_password = await asyncio.to_thread(
            hash_password, password.get_secret_value()
        )
    for field, value in update_data.items():
        setattr(db_user, field, value)
    await session.commit()
    await session.refresh(db_user)
    return User.model_validate(db_user, from_attributes=True)


async def delete_db_user(user_id: UUID, session: AsyncSession) -> None:
    db_user = await find_db_user(user_id, session)
    await session.delete(db_user)
    await session.commit()
