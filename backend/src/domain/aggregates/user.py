from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.value_objects.email import Email


@dataclass
class User:
    id: UUID = field(default_factory=uuid4)
    email: Email = field(default_factory=lambda: Email("placeholder@invalid"))
    username: str = ""
    phone: str | None = None
    password_hash: str = ""
    is_active: bool = True
    email_verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def verify_email(self) -> None:
        if self.email_verified:
            return
        self.email_verified = True
        self._mark_updated()

    def deactivate(self) -> None:
        if not self.is_active:
            return
        self.is_active = False
        self._mark_updated()

    def activate(self) -> None:
        if self.is_active:
            return
        self.is_active = True
        self._mark_updated()

    def change_password(self, new_password_hash: str) -> None:
        if not new_password_hash:
            raise ValueError("Password hash cannot be empty")
        self.password_hash = new_password_hash
        self._mark_updated()

    def update_profile(self, username: str | None = None, phone: str | None = None) -> None:
        if username is not None:
            if not username.strip():
                raise ValueError("Username cannot be empty")
            self.username = username.strip()
        self.phone = phone.strip() if phone else None
        self._mark_updated()

    def is_authenticated(self) -> bool:
        return self.is_active and self.email_verified

    def _mark_updated(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
