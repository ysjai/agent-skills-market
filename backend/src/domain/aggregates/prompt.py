from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.entities.prompt_version import PromptVersion
from src.domain.exceptions import ValidationError


@dataclass
class Prompt:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    title: str = ""
    content: str = ""
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_title(self, new_title: str) -> None:
        if not new_title or not new_title.strip():
            raise ValidationError("Prompt title cannot be empty")

        stripped = new_title.strip()
        if len(stripped) > 200:
            raise ValidationError("Prompt title cannot exceed 200 characters")

        self.title = stripped
        self._mark_updated()

    def update_content(self, content: str) -> None:
        self.content = content
        self._mark_updated()

    def update_description(self, description: str | None) -> None:
        self.description = description
        self._mark_updated()

    def update_tags(self, tags: list[str]) -> None:
        normalized = []

        for tag in tags:
            # Strip whitespace and convert to lowercase
            normalized_tag = tag.strip().lower()

            # Validate tag length
            if len(normalized_tag) > 50:
                raise ValidationError("Tag cannot exceed 50 characters")

            # Only add non-empty tags
            if normalized_tag:
                normalized.append(normalized_tag)

        # Deduplicate
        normalized = list(dict.fromkeys(normalized))

        # Check max tags count
        if len(normalized) > 20:
            raise ValidationError("Cannot have more than 20 tags")

        self.tags = normalized
        self._mark_updated()

    def publish_version(self) -> PromptVersion:
        """Create a snapshot of current state as PromptVersion."""
        version = PromptVersion(
            id=uuid4(),
            prompt_id=self.id,
            version_number=self.version,
            title=self.title,
            content=self.content,
            description=self.description,
            tags=self.tags.copy(),
        )
        # Increment version after creating snapshot
        self._mark_updated()
        return version

    def _mark_updated(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
        self.version += 1
