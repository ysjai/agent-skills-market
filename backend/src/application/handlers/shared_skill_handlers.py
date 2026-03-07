from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.aggregates.user import User
from src.domain.exceptions import ForbiddenError, ResourceConflictError, ResourceNotFoundError
from src.domain.factories.shared_skill_factory import SharedSkillFactory
from src.domain.repositories.category_repository import CategoryRepository
from src.domain.repositories.shared_skill_repository import SharedSkillRepository
from src.domain.repositories.skill_repository import SkillRepository


class SkillFavoriteRepository(Protocol):
    async def update_snapshot_status_batch(
        self, shared_skill_id: UUID, new_status: str
    ) -> None: ...


async def handle_share_skill(
    skill_id: UUID,
    user: User,
    category_id: UUID,
    share_message: str | None,
    skill_repo: SkillRepository,
    shared_skill_repo: SharedSkillRepository,
    category_repo: CategoryRepository,
) -> SharedSkill:
    skill = await skill_repo.get_by_id(skill_id)
    if skill is None:
        raise ResourceNotFoundError("Skill not found")
    if skill.user_id != user.id:
        raise ForbiddenError("Not authorized to share this skill")

    category = await category_repo.get_by_id(category_id)
    if category is None or not category.is_active:
        raise ResourceNotFoundError("Category not found")

    existing = await shared_skill_repo.find_by_skill_id(skill_id)
    if existing is not None:
        raise ResourceConflictError("Active shared skill already exists for this skill")

    shared_skill = SharedSkillFactory.create(
        skill=skill,
        user=user,
        category_id=category_id,
        share_message=share_message,
    )
    return await shared_skill_repo.save(shared_skill)


async def handle_unshare_skill(
    skill_id: UUID,
    user: User,
    shared_skill_repo: SharedSkillRepository,
    favorite_repo: SkillFavoriteRepository,
) -> SharedSkill:
    shared_skill = await shared_skill_repo.find_by_skill_id(skill_id)
    if shared_skill is None:
        raise ResourceNotFoundError("Shared skill not found")
    if shared_skill.user_id != user.id:
        raise ForbiddenError("Not authorized to unshare this skill")

    shared_skill.withdraw()
    await favorite_repo.update_snapshot_status_batch(shared_skill.id, "skill_withdrawn")
    return await shared_skill_repo.save(shared_skill)
