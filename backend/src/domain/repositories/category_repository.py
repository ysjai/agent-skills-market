from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.aggregates.category import Category


class CategoryRepository(ABC):
    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Category | None: ...

    @abstractmethod
    async def get_all_active(self) -> list[Category]: ...
