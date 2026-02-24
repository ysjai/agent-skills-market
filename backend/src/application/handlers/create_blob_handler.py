from __future__ import annotations

from fastapi import HTTPException, status

from src.core.config import get_settings
from src.domain.entities.blob import Blob
from src.domain.factories.blob_factory import BlobFactory
from src.domain.repositories.blob_repository import BlobRepository


async def handle_create_blob(
    content: bytes,
    blob_repo: BlobRepository,
    compress: bool = True,
) -> Blob:
    settings = get_settings()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes",
        )
    blob = BlobFactory.create_from_content(content=content, compressed=compress)
    existing = await blob_repo.get_by_checksum(blob.checksum, compressed=compress)
    if existing:
        return existing
    await blob_repo.save(blob)
    return blob
