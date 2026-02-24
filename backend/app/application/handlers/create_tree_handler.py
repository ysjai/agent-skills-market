from __future__ import annotations

from typing import Any

from app.domain.aggregates.tree import Tree
from app.domain.factories.tree_factory import TreeFactory
from app.domain.repositories.tree_repository import TreeRepository


async def handle_create_tree(
    tree_repo: TreeRepository,
    entries: list[dict[str, Any]] | None = None,
) -> Tree:
    tree = TreeFactory.create(entries)
    await tree_repo.save(tree)
    return tree
