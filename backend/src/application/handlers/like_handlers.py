from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.aggregates.user import User
from src.domain.entities.skill_like import SkillLike
from src.domain.exceptions import ResourceConflictError, ResourceNotFoundError
from src.domain.repositories.shared_skill_repository import SharedSkillRepository


async def handle_like_skill(
    shared_skill_id: UUID,
    user: User,
    shared_skill_repo: SharedSkillRepository,
) -> SharedSkill:
    shared_skill = await shared_skill_repo.find_by_id(shared_skill_id)
    if shared_skill is None:
        raise ResourceNotFoundError("Shared skill not found")

    existing_like = await shared_skill_repo.find_like(user.id, shared_skill_id)
    if existing_like is not None:
        raise ResourceConflictError("Shared skill already liked")

    like = SkillLike(
        id=uuid4(),
        user_id=user.id,
        shared_skill_id=shared_skill_id,
        created_at=datetime.now(timezone.utc),
    )
    _ = await shared_skill_repo.save_like(like)
    await shared_skill_repo.increment_like_count(shared_skill_id)

    updated_shared_skill = await shared_skill_repo.find_by_id(shared_skill_id)
    if updated_shared_skill is None:
        raise ResourceNotFoundError("Shared skill not found")
    return updated_shared_skill


async def handle_unlike_skill(
    shared_skill_id: UUID,
    user: User,
    shared_skill_repo: SharedSkillRepository,
) -> SharedSkill:
    shared_skill = await shared_skill_repo.find_by_id(shared_skill_id)
    if shared_skill is None:
        raise ResourceNotFoundError("Shared skill not found")

    existing_like = await shared_skill_repo.find_like(user.id, shared_skill_id)
    if existing_like is None:
        raise ResourceNotFoundError("Like not found")

    await shared_skill_repo.delete_like(user.id, shared_skill_id)
    await shared_skill_repo.decrement_like_count(shared_skill_id)

    updated_shared_skill = await shared_skill_repo.find_by_id(shared_skill_id)
    if updated_shared_skill is None:
        raise ResourceNotFoundError("Shared skill not found")
    return updated_shared_skill
