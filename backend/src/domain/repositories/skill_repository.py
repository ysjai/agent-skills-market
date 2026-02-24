from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.aggregates.skill import Skill
from src.domain.value_objects.slug import Slug


class SkillRepository(ABC):
    @abstractmethod
    async def get_by_id(self, skill_id: UUID) -> Skill | None: ...

    @abstractmethod
    async def get_by_slug(self, slug: Slug, user_id: UUID) -> Skill | None: ...

    @abstractmethod
    async def find_by_user(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Skill]: ...

    @abstractmethod
    async def save(self, skill: Skill) -> None: ...

    @abstractmethod
    async def delete(self, skill_id: UUID) -> None: ...
