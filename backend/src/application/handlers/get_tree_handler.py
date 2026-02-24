from __future__ import annotations

from uuid import UUID

from src.domain.aggregates.tree import Tree
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.tree_repository import TreeRepository


async def handle_get_tree(
    tree_repo: TreeRepository,
    tree_id: UUID,
) -> Tree:
    tree = await tree_repo.get_by_id(tree_id)
    if tree is None:
        raise ResourceNotFoundError(f"Tree '{tree_id}' not found")

    return tree
