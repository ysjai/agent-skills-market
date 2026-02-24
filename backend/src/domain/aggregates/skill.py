from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.value_objects.slug import Slug


@dataclass
class Skill:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    name: str = ""
    slug: Slug = field(default_factory=lambda: Slug("untitled"))
    description: str | None = None
    tree_id: UUID | None = None
    is_public: bool = False
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_name(self, new_name: str) -> None:
        if not new_name or not new_name.strip():
            raise ValueError("Skill name cannot be empty")
        self.name = new_name.strip()
        self.slug = Slug.from_name(self.name)
        self._mark_updated()

    def update_description(self, description: str | None) -> None:
        self.description = description
        self._mark_updated()

    def set_public(self, is_public: bool) -> None:
        self.is_public = is_public
        self._mark_updated()

    def assign_tree(self, tree_id: UUID | None) -> None:
        self.tree_id = tree_id
        self._mark_updated()

    def _mark_updated(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
        self.version += 1
