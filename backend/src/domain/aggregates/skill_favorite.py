from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.exceptions import ValidationError


@dataclass
class SkillFavorite:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    shared_skill_id: UUID | None = None
    snapshot_name: str = ""
    snapshot_description: str | None = None
    snapshot_slug: str = ""
    snapshot_author_name: str = ""
    snapshot_status: str = "active"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._validate_status(self.snapshot_status)

    def mark_skill_withdrawn(self) -> None:
        self.snapshot_status = "skill_withdrawn"

    def mark_skill_deleted(self) -> None:
        self.snapshot_status = "skill_deleted"
        self.shared_skill_id = None

    def is_snapshot_stale(self) -> bool:
        return self.snapshot_status != "active"

    @staticmethod
    def _validate_status(status: str) -> None:
        if status not in {"active", "skill_withdrawn", "skill_deleted"}:
            raise ValidationError(
                "Skill favorite snapshot status must be one of 'active', 'skill_withdrawn', or 'skill_deleted'"
            )
