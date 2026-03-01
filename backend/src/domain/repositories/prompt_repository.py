from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.aggregates.prompt import Prompt
from src.domain.entities.prompt_version import PromptVersion


class PromptRepository(ABC):
    @abstractmethod
    async def get_by_id(self, prompt_id: UUID) -> Prompt | None: ...

    @abstractmethod
    async def find_by_user(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
        tag: str | None = None,
        search: str | None = None,
    ) -> list[Prompt]: ...

    @abstractmethod
    async def count_by_user(
        self,
        user_id: UUID,
        tag: str | None = None,
        search: str | None = None,
    ) -> int: ...

    @abstractmethod
    async def save(self, prompt: Prompt) -> None: ...

    @abstractmethod
    async def delete(self, prompt_id: UUID) -> None: ...

    @abstractmethod
    async def save_version(self, version: PromptVersion) -> None: ...

    @abstractmethod
    async def get_versions(self, prompt_id: UUID) -> list[PromptVersion]: ...

    @abstractmethod
    async def get_version_by_id(self, version_id: UUID) -> PromptVersion | None: ...
