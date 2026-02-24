from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.blob import Blob


class BlobRepository(ABC):
    @abstractmethod
    async def get_by_id(self, blob_id: UUID) -> Blob | None: ...

    @abstractmethod
    async def get_by_checksum(
        self, content_hash: str, compressed: bool | None = None
    ) -> Blob | None: ...

    @abstractmethod
    async def save(self, blob: Blob) -> None: ...

    @abstractmethod
    async def delete(self, blob_id: UUID) -> None: ...

    @abstractmethod
    async def decrement_reference_count(self, blob_id: UUID) -> bool: ...

    @abstractmethod
    async def increment_reference_count(self, blob_id: UUID) -> None: ...
