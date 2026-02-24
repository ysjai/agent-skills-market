from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.domain.aggregates.user import User


class RegisterUserReq(BaseModel):
    email: EmailStr
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=100)


class RegisterUserResp(BaseModel):
    id: UUID
    email: str
    username: str
    phone: str | None
    is_active: bool
    email_verified: bool
    created_at: datetime
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    @classmethod
    def from_domain(
        cls,
        user: User,
        access_token: str,
        refresh_token: str,
    ) -> RegisterUserResp:
        return cls(
            id=user.id,
            email=str(user.email),
            username=user.username,
            phone=user.phone,
            is_active=user.is_active,
            email_verified=user.email_verified,
            created_at=user.created_at,
            access_token=access_token,
            refresh_token=refresh_token,
        )


class LoginReq(BaseModel):
    email: EmailStr
    password: str


class LoginResp(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class GetUserResp(BaseModel):
    id: UUID
    email: str
    username: str
    phone: str | None
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> GetUserResp:
        return cls(
            id=user.id,
            email=str(user.email),
            username=user.username,
            phone=user.phone,
            is_active=user.is_active,
            email_verified=user.email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UpdateUserReq(BaseModel):
    username: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=20)


class UpdateUserResp(BaseModel):
    id: UUID
    email: str
    username: str
    phone: str | None
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> UpdateUserResp:
        return cls(
            id=user.id,
            email=str(user.email),
            username=user.username,
            phone=user.phone,
            is_active=user.is_active,
            email_verified=user.email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
