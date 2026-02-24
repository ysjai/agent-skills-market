from __future__ import annotations

from uuid import UUID

from app.domain.entities.blob import Blob
from app.domain.exceptions import ResourceNotFoundError
from app.domain.repositories.blob_repository import BlobRepository


async def handle_get_blob(
    blob_id: UUID,
    blob_repo: BlobRepository,
) -> Blob:
    blob = await blob_repo.get_by_id(blob_id)
    if not blob:
        raise ResourceNotFoundError()
    return blob
