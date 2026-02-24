from __future__ import annotations

from uuid import UUID

from app.domain.aggregates.tree import Tree
from app.domain.exceptions import ResourceNotFoundError
from app.domain.repositories.tree_repository import TreeRepository


async def handle_rename_tree_file(
    tree_repo: TreeRepository,
    tree_id: UUID,
    old_path: str,
    new_path: str,
) -> Tree:
    tree = await tree_repo.get_by_id(tree_id)
    if tree is None:
        raise ResourceNotFoundError(f"Tree '{tree_id}' not found")

    tree.rename_entry(old_path, new_path)
    await tree_repo.save(tree)
    return tree
