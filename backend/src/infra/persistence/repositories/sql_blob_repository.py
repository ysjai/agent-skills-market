from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.blob import Blob
from src.domain.repositories.blob_repository import BlobRepository
from src.infra.persistence.models.blob_model import BlobModel


class SqlBlobRepository(BlobRepository):

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, blob_id: UUID) -> Blob | None:
        result = await self._db.execute(select(BlobModel).where(BlobModel.id == blob_id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_checksum(
        self, content_hash: str, compressed: bool | None = None
    ) -> Blob | None:
        query = select(BlobModel).where(BlobModel.content_hash == content_hash)
        if compressed is not None:
            query = query.where(BlobModel.compressed == compressed)
        result = await self._db.execute(query)
        model = result.scalars().first()
        return model.to_domain() if model else None

    async def save(self, blob: Blob) -> None:
        model = BlobModel.from_domain(blob)
        await self._db.merge(model)
        await self._db.flush()

    async def delete(self, blob_id: UUID) -> None:
        result = await self._db.execute(select(BlobModel).where(BlobModel.id == blob_id))
        model = result.scalar_one_or_none()
        if model:
            await self._db.delete(model)
            await self._db.flush()

    async def decrement_reference_count(self, blob_id: UUID) -> bool:
        result = await self._db.execute(select(BlobModel).where(BlobModel.id == blob_id))
        model = result.scalar_one_or_none()
        if model is None:
            return False
        model.reference_count -= 1
        await self._db.flush()
        return model.reference_count <= 0

    async def increment_reference_count(self, blob_id: UUID) -> None:
        result = await self._db.execute(select(BlobModel).where(BlobModel.id == blob_id))
        model = result.scalar_one_or_none()
        if model:
            model.reference_count += 1
            await self._db.flush()
