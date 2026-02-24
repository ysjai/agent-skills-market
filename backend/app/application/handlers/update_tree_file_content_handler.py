from __future__ import annotations

import hashlib
from uuid import UUID

from app.domain.aggregates.tree import Tree
from app.domain.entities.blob import Blob
from app.domain.exceptions import ResourceNotFoundError
from app.domain.repositories.blob_repository import BlobRepository
from app.domain.repositories.tree_repository import TreeRepository


async def handle_update_tree_file_content(
    tree_repo: TreeRepository,
    blob_repo: BlobRepository,
    tree_id: UUID,
    path: str,
    content: str,
) -> Tree:
    tree = await tree_repo.get_by_id(tree_id)
    if tree is None:
        raise ResourceNotFoundError(f"Tree '{tree_id}' not found")

    content_bytes = content.encode("utf-8")
    content_hash = hashlib.sha256(content_bytes).hexdigest()
    existing_blob = await blob_repo.get_by_checksum(content_hash)
    if existing_blob:
        new_blob_id = existing_blob.id
    else:
        blob = Blob.create(content_bytes)
        await blob_repo.save(blob)
        new_blob_id = blob.id

    tree.update_entry_content(path=path, new_blob_id=new_blob_id)
    await tree_repo.save(tree)
    return tree
