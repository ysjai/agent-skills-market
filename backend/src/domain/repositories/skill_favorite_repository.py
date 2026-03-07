from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.aggregates.skill_favorite import SkillFavorite


class SkillFavoriteRepository(ABC):
    @abstractmethod
    async def save(self, skill_favorite: SkillFavorite) -> SkillFavorite: ...

    @abstractmethod
    async def delete(self, user_id: UUID, shared_skill_id: UUID) -> None: ...

    @abstractmethod
    async def find_by_user_and_shared_skill(
        self, user_id: UUID, shared_skill_id: UUID
    ) -> SkillFavorite | None: ...

    @abstractmethod
    async def find_by_user(self, user_id: UUID, skip: int, limit: int) -> list[SkillFavorite]: ...

    @abstractmethod
    async def count_by_user(self, user_id: UUID) -> int: ...

    @abstractmethod
    async def find_all_by_shared_skill_id(self, shared_skill_id: UUID) -> list[SkillFavorite]: ...

    @abstractmethod
    async def update_snapshot_status_batch(
        self, shared_skill_id: UUID, new_status: str
    ) -> None: ...
