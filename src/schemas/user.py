from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr

from src.schemas.user_option import UserRole, UserStatus


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.PENDING


class UserCreate(UserBase):
    password: SecretStr


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: SecretStr | None = None
    role: UserRole | None = None
    status: UserStatus | None = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
