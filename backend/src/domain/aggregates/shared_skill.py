from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.exceptions import ValidationError


@dataclass
class SharedSkill:
    id: UUID = field(default_factory=uuid4)
    skill_id: UUID | None = None
    user_id: UUID = field(default_factory=uuid4)
    category_id: UUID = field(default_factory=uuid4)
    share_message: str | None = None
    like_count: int = 0
    favorite_count: int = 0
    status: str = "active"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._validate_status(self.status)
        self._validate_count(self.like_count, "Like count cannot be negative")
        self._validate_count(self.favorite_count, "Favorite count cannot be negative")

    def withdraw(self) -> None:
        if self.status == "withdrawn":
            return
        self.status = "withdrawn"
        self._mark_updated()

    def reactivate(self, category_id: UUID, share_message: str | None) -> None:
        self.status = "active"
        self.category_id = category_id
        self.share_message = share_message
        self._mark_updated()

    def mark_skill_deleted(self) -> None:
        self.skill_id = None
        self.status = "withdrawn"
        self._mark_updated()

    def increment_like_count(self) -> None:
        self.like_count += 1
        self._mark_updated()

    def decrement_like_count(self) -> None:
        self._validate_count(self.like_count - 1, "Like count cannot be negative")
        self.like_count -= 1
        self._mark_updated()

    def increment_favorite_count(self) -> None:
        self.favorite_count += 1
        self._mark_updated()

    def decrement_favorite_count(self) -> None:
        self._validate_count(self.favorite_count - 1, "Favorite count cannot be negative")
        self.favorite_count -= 1
        self._mark_updated()

    def _mark_updated(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def _validate_status(status: str) -> None:
        if status not in {"active", "withdrawn"}:
            raise ValidationError("Shared skill status must be either 'active' or 'withdrawn'")

    @staticmethod
    def _validate_count(count: int, message: str) -> None:
        if count < 0:
            raise ValidationError(message)
