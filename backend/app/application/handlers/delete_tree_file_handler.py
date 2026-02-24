from __future__ import annotations

from uuid import UUID

from app.domain.aggregates.tree import Tree
from app.domain.exceptions import ResourceNotFoundError, ValidationError
from app.domain.repositories.blob_repository import BlobRepository
from app.domain.repositories.tree_repository import TreeRepository


async def handle_delete_tree_file(
    tree_repo: TreeRepository,
    blob_repo: BlobRepository,
    tree_id: UUID,
    path: str,
) -> Tree:
    tree = await tree_repo.get_by_id(tree_id)
    if tree is None:
        raise ResourceNotFoundError(f"Tree '{tree_id}' not found")

    normalized_path = path.strip("/")
    if normalized_path == "SKILL.md":
        raise ValidationError("Cannot delete SKILL.md file")

    blob_ids = tree.delete_entry(path)

    for blob_id in blob_ids:
        should_delete = await blob_repo.decrement_reference_count(blob_id)
        if should_delete:
            await blob_repo.delete(blob_id)

    await tree_repo.save(tree)
    return tree
