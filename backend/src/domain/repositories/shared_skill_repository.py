from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.entities.skill_like import SkillLike


class SharedSkillRepository(ABC):
    @abstractmethod
    async def save(self, shared_skill: SharedSkill) -> SharedSkill: ...

    @abstractmethod
    async def find_by_id(self, id: UUID) -> SharedSkill | None: ...

    @abstractmethod
    async def find_by_skill_id(self, skill_id: UUID) -> SharedSkill | None: ...

    @abstractmethod
    async def find_by_user_and_skill(self, user_id: UUID, skill_id: UUID) -> SharedSkill | None: ...

    @abstractmethod
    async def find_all_by_skill_id(self, skill_id: UUID) -> list[SharedSkill]: ...

    @abstractmethod
    async def find_active_by_filters(
        self,
        keyword: str | None,
        category_id: UUID | None,
        sort_by: str,
        skip: int,
        limit: int,
    ) -> list[SharedSkill]: ...

    @abstractmethod
    async def count_active_by_filters(
        self, keyword: str | None, category_id: UUID | None
    ) -> int: ...

    @abstractmethod
    async def delete(self, shared_skill_id: UUID) -> None: ...

    @abstractmethod
    async def find_like(self, user_id: UUID, shared_skill_id: UUID) -> SkillLike | None: ...

    @abstractmethod
    async def save_like(self, like: SkillLike) -> SkillLike: ...

    @abstractmethod
    async def delete_like(self, user_id: UUID, shared_skill_id: UUID) -> None: ...

    @abstractmethod
    async def increment_like_count(self, shared_skill_id: UUID) -> None: ...

    @abstractmethod
    async def decrement_like_count(self, shared_skill_id: UUID) -> None: ...

    @abstractmethod
    async def increment_favorite_count(self, shared_skill_id: UUID) -> None: ...

    @abstractmethod
    async def decrement_favorite_count(self, shared_skill_id: UUID) -> None: ...
