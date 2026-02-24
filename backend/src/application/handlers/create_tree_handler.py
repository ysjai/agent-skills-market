from __future__ import annotations

from typing import Any

from src.domain.aggregates.tree import Tree
from src.domain.factories.tree_factory import TreeFactory
from src.domain.repositories.tree_repository import TreeRepository


async def handle_create_tree(
    tree_repo: TreeRepository,
    entries: list[dict[str, Any]] | None = None,
) -> Tree:
    tree = TreeFactory.create(entries)
    await tree_repo.save(tree)
    return tree
