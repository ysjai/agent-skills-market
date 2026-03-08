from abc import ABC, abstractmethod
from uuid import UUID
from src.domain.aggregates.prompt_favorite import PromptFavorite


class PromptFavoriteRepository(ABC):
    @abstractmethod
    async def save(self, favorite: PromptFavorite) -> PromptFavorite: ...

    @abstractmethod
    async def delete(self, user_id: UUID, shared_prompt_id: UUID) -> None: ...

    @abstractmethod
    async def find_by_user_and_shared_prompt(
        self, user_id: UUID, shared_prompt_id: UUID
    ) -> PromptFavorite | None: ...

    @abstractmethod
    async def find_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[PromptFavorite]: ...

    @abstractmethod
    async def count_by_user(self, user_id: UUID) -> int: ...

    @abstractmethod
    async def update_batch_status(self, shared_prompt_id: UUID, status: str) -> None: ...
