from __future__ import annotations

from typing import Any
from uuid import UUID

from src.domain.aggregates.tree import Tree
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.tree_repository import TreeRepository


async def handle_update_tree(
    tree_repo: TreeRepository,
    tree_id: UUID,
    entries: list[dict[str, Any]],
) -> Tree:
    tree = await tree_repo.get_by_id(tree_id)
    if tree is None:
        raise ResourceNotFoundError(f"Tree '{tree_id}' not found")

    tree.entries = []
    for entry_data in entries:
        tree.add_entry(
            path=entry_data["path"],
            entry_type=entry_data["type"],
            blob_id=entry_data.get("blob_id"),
        )

    await tree_repo.save(tree)
    return tree
