from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class SharedPrompt:
    prompt_id: UUID | None = None
    user_id: UUID = field(default_factory=uuid4)
    share_message: str | None = None
    like_count: int = 0
    favorite_count: int = 0
    status: str = "active"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.status not in ("active", "withdrawn"):
            raise ValueError(f"Invalid status: {self.status}")
        if self.like_count < 0:
            raise ValueError("like_count cannot be negative")
        if self.favorite_count < 0:
            raise ValueError("favorite_count cannot be negative")

    def withdraw(self):
        self.status = "withdrawn"
        self._mark_updated()

    def mark_prompt_deleted(self):
        self.prompt_id = None
        self.status = "withdrawn"
        self._mark_updated()

    def increment_like_count(self):
        self.like_count += 1
        self._mark_updated()

    def decrement_like_count(self):
        self.like_count = max(0, self.like_count - 1)
        self._mark_updated()

    def increment_favorite_count(self):
        self.favorite_count += 1
        self._mark_updated()

    def decrement_favorite_count(self):
        self.favorite_count = max(0, self.favorite_count - 1)
        self._mark_updated()

    def _mark_updated(self):
        self.updated_at = datetime.now(timezone.utc)
