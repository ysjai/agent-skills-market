from __future__ import annotations

from uuid import UUID

from src.domain.aggregates.tree import Tree
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.shared_skill_repository import SharedSkillRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository


async def handle_get_market_skill_tree(
    shared_skill_id: UUID,
    shared_skill_repo: SharedSkillRepository,
    skill_repo: SkillRepository,
    tree_repo: TreeRepository,
) -> Tree:
    shared_skill = await shared_skill_repo.find_by_id(shared_skill_id)
    if shared_skill is None:
        raise ResourceNotFoundError("Shared skill not found")

    if shared_skill.skill_id is None:
        raise ResourceNotFoundError("Skill content is no longer available")

    skill = await skill_repo.get_by_id(shared_skill.skill_id)
    if skill is None:
        raise ResourceNotFoundError("Original skill not found")

    if skill.tree_id is None:
        raise ResourceNotFoundError("Skill has no file tree")

    tree = await tree_repo.get_by_id(skill.tree_id)
    if tree is None:
        raise ResourceNotFoundError("File tree not found")

    return tree
