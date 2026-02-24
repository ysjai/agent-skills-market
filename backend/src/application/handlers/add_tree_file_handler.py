from __future__ import annotations

import hashlib
from uuid import UUID

from src.domain.aggregates.tree import Tree
from src.domain.exceptions import ResourceNotFoundError
from src.domain.factories.blob_factory import BlobFactory
from src.domain.repositories.blob_repository import BlobRepository
from src.domain.repositories.tree_repository import TreeRepository


async def handle_add_tree_file(
    tree_repo: TreeRepository,
    blob_repo: BlobRepository,
    tree_id: UUID,
    path: str,
    entry_type: str,
    blob_id: UUID | None = None,
    content: str | None = None,
) -> Tree:
    tree = await tree_repo.get_by_id(tree_id)
    if tree is None:
        raise ResourceNotFoundError(f"Tree '{tree_id}' not found")

    if content is not None and blob_id is None:
        content_bytes = content.encode("utf-8")
        content_hash = hashlib.sha256(content_bytes).hexdigest()
        existing_blob = await blob_repo.get_by_checksum(content_hash)
        if existing_blob:
            blob_id = existing_blob.id
        else:
            blob = BlobFactory.create_from_content(content_bytes)
            await blob_repo.save(blob)
            blob_id = blob.id

    tree.add_entry(path=path, entry_type=entry_type, blob_id=blob_id)

    if blob_id:
        await blob_repo.increment_reference_count(blob_id)

    await tree_repo.save(tree)
    return tree
