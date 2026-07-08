from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, SecretStr

from src.schemas.user_option import UserRole, UserStatus


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.PENDING
    password: SecretStr


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    role: UserRole | None = None
    status: UserStatus | None = None
    password: SecretStr | None = None


class User(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime
