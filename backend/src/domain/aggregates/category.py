from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.value_objects.slug import Slug


@dataclass
class Category:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    slug: Slug = field(default_factory=lambda: Slug("uncategorized"))
    description: str | None = None
    display_order: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_name(self, name: str, slug: Slug) -> None:
        if not name or not name.strip():
            raise ValueError("Category name cannot be empty")
        self.name = name.strip()
        self.slug = slug
        self._mark_updated()

    def deactivate(self) -> None:
        self.is_active = False
        self._mark_updated()

    def activate(self) -> None:
        self.is_active = True
        self._mark_updated()

    def _mark_updated(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
