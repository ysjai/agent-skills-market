from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.aggregates.tree import Tree


class TreeRepository(ABC):
    @abstractmethod
    async def get_by_id(self, tree_id: UUID) -> Tree | None: ...

    @abstractmethod
    async def save(self, tree: Tree) -> None: ...

    @abstractmethod
    async def delete(self, tree_id: UUID) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...
