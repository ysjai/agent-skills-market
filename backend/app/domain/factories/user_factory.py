from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.domain.aggregates.user import User
from app.domain.exceptions import ValidationError
from app.domain.value_objects.email import Email


class UserFactory:
    _MAX_USERNAME_LENGTH = 100
    _MAX_PHONE_LENGTH = 20

    @classmethod
    def create(
        cls,
        email: str,
        username: str,
        password_hash: str,
        phone: str | None = None,
    ) -> User:
        validated_email = Email(email)
        validated_username = cls._validate_username(username)
        validated_phone = cls._validate_phone(phone)
        validated_password_hash = cls._validate_password_hash(password_hash)

        now = datetime.now(timezone.utc)

        return User(
            id=uuid4(),
            email=validated_email,
            username=validated_username,
            phone=validated_phone,
            password_hash=validated_password_hash,
            is_active=True,
            email_verified=False,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def _validate_username(cls, username: str) -> str:
        if not username:
            raise ValidationError("Username cannot be empty")

        stripped = username.strip()

        if not stripped:
            raise ValidationError("Username cannot be empty")

        if len(stripped) > cls._MAX_USERNAME_LENGTH:
            raise ValidationError(f"Username cannot exceed {cls._MAX_USERNAME_LENGTH} characters")

        return stripped

    @classmethod
    def _validate_phone(cls, phone: str | None) -> str | None:
        if phone is None:
            return None

        stripped = phone.strip()

        if not stripped:
            return None

        if len(stripped) > cls._MAX_PHONE_LENGTH:
            raise ValidationError(f"Phone cannot exceed {cls._MAX_PHONE_LENGTH} characters")

        return stripped

    @classmethod
    def _validate_password_hash(cls, password_hash: str) -> str:
        if not password_hash:
            raise ValidationError("Password hash cannot be empty")

        return password_hash
