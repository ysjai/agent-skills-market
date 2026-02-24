from __future__ import annotations

from uuid import UUID

from app.domain.exceptions import ResourceNotFoundError
from app.domain.repositories.tree_repository import TreeRepository


async def handle_delete_tree(
    tree_repo: TreeRepository,
    tree_id: UUID,
) -> None:
    tree = await tree_repo.get_by_id(tree_id)
    if tree is None:
        raise ResourceNotFoundError(f"Tree '{tree_id}' not found")

    await tree_repo.delete(tree_id)
