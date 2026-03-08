from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class PromptFavorite:
    user_id: UUID = field(default_factory=uuid4)
    shared_prompt_id: UUID | None = None
    snapshot_title: str = ""
    snapshot_content: str = ""
    snapshot_description: str | None = None
    snapshot_tags: list[str] = field(default_factory=list)
    snapshot_author_name: str = ""
    snapshot_version: int = 1
    snapshot_status: str = "active"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def mark_prompt_withdrawn(self):
        self.snapshot_status = "prompt_withdrawn"

    def mark_prompt_deleted(self):
        self.snapshot_status = "prompt_deleted"
        self.shared_prompt_id = None

    def is_version_stale(self, current_version: int) -> bool:
        return current_version > self.snapshot_version

    def refresh_snapshot(
        self,
        title: str,
        content: str,
        description: str | None,
        tags: list[str],
        version: int,
    ):
        self.snapshot_title = title
        self.snapshot_content = content
        self.snapshot_description = description
        self.snapshot_tags = tags
        self.snapshot_version = version
        self.snapshot_status = "active"
