# docs/templates/aggregate_skill.py

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.domain.value_objects.slug import Slug


@dataclass
class Skill:
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    slug: Slug
    description: str | None
    tree_id: uuid.UUID | None
    version: int
    created_at: datetime
    updated_at: datetime

    _is_deleted: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Skill name cannot be empty")
        if len(self.name) > 200:
            raise ValueError("Skill name cannot exceed 200 characters")

    @classmethod
    def create(
        cls,
        user_id: uuid.UUID,
        name: str,
        description: str | None = None,
        tree_id: uuid.UUID | None = None,
    ) -> Skill:
        now = datetime.utcnow()
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name.strip(),
            slug=Slug.from_name(name),
            description=description,
            tree_id=tree_id,
            version=1,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        if name is not None:
            if not name.strip():
                raise ValueError("Skill name cannot be empty")
            self.name = name.strip()
            self.slug = Slug.from_name(name)

        if description is not None:
            self.description = description

        self._increment_version()
        self.updated_at = datetime.utcnow()

    def assign_tree(self, tree_id: uuid.UUID) -> None:
        if self.tree_id == tree_id:
            return
        self.tree_id = tree_id
        self._increment_version()
        self.updated_at = datetime.utcnow()

    def delete(self) -> None:
        if self._is_deleted:
            raise ValueError("Skill is already deleted")
        self._is_deleted = True
        self._increment_version()
        self.updated_at = datetime.utcnow()

    def _increment_version(self) -> None:
        self.version += 1

    @property
    def is_deleted(self) -> bool:
        return self._is_deleted
