from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.aggregates.skill_favorite import SkillFavorite
from src.domain.aggregates.user import User
from src.domain.exceptions import ResourceConflictError, ResourceNotFoundError
from src.domain.factories.skill_favorite_factory import SkillFavoriteFactory
from src.domain.repositories.shared_skill_repository import SharedSkillRepository
from src.domain.repositories.skill_repository import SkillRepository


class FavoriteRepository(Protocol):
    async def save(self, skill_favorite: SkillFavorite) -> SkillFavorite: ...

    async def delete(self, user_id: UUID, shared_skill_id: UUID) -> None: ...

    async def find_by_user_and_shared_skill(
        self, user_id: UUID, shared_skill_id: UUID
    ) -> SkillFavorite | None: ...

    async def find_by_user(self, user_id: UUID, skip: int, limit: int) -> list[SkillFavorite]: ...

    async def count_by_user(self, user_id: UUID) -> int: ...


async def handle_favorite_skill(
    shared_skill_id: UUID,
    user: User,
    shared_skill_repo: SharedSkillRepository,
    favorite_repo: FavoriteRepository,
    skill_repo: SkillRepository,
) -> SkillFavorite:
    shared_skill = await shared_skill_repo.find_by_id(shared_skill_id)
    if shared_skill is None or shared_skill.status != "active":
        raise ResourceNotFoundError("Shared skill not found")

    existing_favorite = await favorite_repo.find_by_user_and_shared_skill(user.id, shared_skill_id)
    if existing_favorite is not None:
        raise ResourceConflictError("Skill already favorited")

    skill = None
    if shared_skill.skill_id is not None:
        skill = await skill_repo.get_by_id(shared_skill.skill_id)

    favorite = SkillFavoriteFactory.create(user_id=user.id, shared_skill=shared_skill, skill=skill)
    saved_favorite = await favorite_repo.save(favorite)
    await shared_skill_repo.increment_favorite_count(shared_skill_id)
    return saved_favorite


async def handle_unfavorite_skill(
    shared_skill_id: UUID,
    user: User,
    shared_skill_repo: SharedSkillRepository,
    favorite_repo: FavoriteRepository,
) -> None:
    favorite = await favorite_repo.find_by_user_and_shared_skill(user.id, shared_skill_id)
    if favorite is None:
        raise ResourceNotFoundError("Favorite not found")

    await favorite_repo.delete(user.id, shared_skill_id)
    await shared_skill_repo.decrement_favorite_count(shared_skill_id)


async def handle_list_favorites(
    user: User,
    favorite_repo: FavoriteRepository,
    skip: int,
    limit: int,
) -> tuple[list[SkillFavorite], int]:
    favorites = await favorite_repo.find_by_user(user.id, skip, limit)
    total = await favorite_repo.count_by_user(user.id)
    return favorites, total
