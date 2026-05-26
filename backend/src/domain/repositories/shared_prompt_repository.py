from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.aggregates.shared_prompt import SharedPrompt
from src.domain.entities.prompt_like import PromptLike


class SharedPromptRepository(ABC):
    @abstractmethod
    async def save(self, shared_prompt: SharedPrompt) -> SharedPrompt: ...

    @abstractmethod
    async def find_by_id(self, id: UUID) -> SharedPrompt | None: ...

    @abstractmethod
    async def find_by_prompt_id(self, prompt_id: UUID) -> SharedPrompt | None: ...

    @abstractmethod
    async def find_by_user_and_prompt(
        self, user_id: UUID, prompt_id: UUID
    ) -> SharedPrompt | None: ...

    @abstractmethod
    async def find_all_by_prompt_id(self, prompt_id: UUID) -> list[SharedPrompt]: ...

    @abstractmethod
    async def find_active_by_filters(
        self,
        keyword: str | None,
        tags: list[str] | None,
        sort_by: str,
        skip: int,
        limit: int,
        user_id: UUID | None = None,
    ) -> list[SharedPrompt]: ...

    @abstractmethod
    async def count_active_by_filters(
        self, keyword: str | None, tags: list[str] | None, user_id: UUID | None = None
    ) -> int: ...

    @abstractmethod
    async def delete(self, shared_prompt_id: UUID) -> None: ...

    # Like operations
    @abstractmethod
    async def find_like(self, user_id: UUID, shared_prompt_id: UUID) -> PromptLike | None: ...

    @abstractmethod
    async def save_like(self, like: PromptLike) -> PromptLike: ...

    @abstractmethod
    async def delete_like(self, user_id: UUID, shared_prompt_id: UUID) -> None: ...

    @abstractmethod
    async def increment_like_count(self, shared_prompt_id: UUID) -> None: ...

    @abstractmethod
    async def decrement_like_count(self, shared_prompt_id: UUID) -> None: ...

    @abstractmethod
    async def increment_favorite_count(self, shared_prompt_id: UUID) -> None: ...

    @abstractmethod
    async def decrement_favorite_count(self, shared_prompt_id: UUID) -> None: ...
