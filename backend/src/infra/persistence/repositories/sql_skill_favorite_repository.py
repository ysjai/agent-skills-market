from __future__ import annotations

from typing import final
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.aggregates.skill_favorite import SkillFavorite
from src.infra.persistence.models.skill_favorite_model import SkillFavoriteModel


@final
class SqlSkillFavoriteRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def save(self, skill_favorite: SkillFavorite) -> SkillFavorite:
        model = await self._db.merge(SkillFavoriteModel.from_domain(skill_favorite))
        await self._db.flush()
        return model.to_domain()

    async def delete(self, user_id: UUID, shared_skill_id: UUID) -> None:
        result = await self._db.execute(
            select(SkillFavoriteModel).where(
                SkillFavoriteModel.user_id == user_id,
                SkillFavoriteModel.shared_skill_id == shared_skill_id,
            )
        )
        model = result.scalar_one_or_none()
        if model is not None:
            await self._db.delete(model)

    async def find_by_user_and_shared_skill(
        self, user_id: UUID, shared_skill_id: UUID
    ) -> SkillFavorite | None:
        result = await self._db.execute(
            select(SkillFavoriteModel).where(
                SkillFavoriteModel.user_id == user_id,
                SkillFavoriteModel.shared_skill_id == shared_skill_id,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model is not None else None

    async def find_by_user(self, user_id: UUID, skip: int, limit: int) -> list[SkillFavorite]:
        result = await self._db.execute(
            select(SkillFavoriteModel)
            .where(SkillFavoriteModel.user_id == user_id)
            .order_by(SkillFavoriteModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def count_by_user(self, user_id: UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .select_from(SkillFavoriteModel)
            .where(SkillFavoriteModel.user_id == user_id)
        )
        return int(result.scalar_one())

    async def find_all_by_shared_skill_id(self, shared_skill_id: UUID) -> list[SkillFavorite]:
        result = await self._db.execute(
            select(SkillFavoriteModel)
            .where(SkillFavoriteModel.shared_skill_id == shared_skill_id)
            .order_by(SkillFavoriteModel.created_at.desc())
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def update_snapshot_status_batch(self, shared_skill_id: UUID, new_status: str) -> None:
        values: dict[str, object] = {"snapshot_status": new_status}
        if new_status == "skill_deleted":
            values["shared_skill_id"] = None

        _ = await self._db.execute(
            update(SkillFavoriteModel)
            .where(SkillFavoriteModel.shared_skill_id == shared_skill_id)
            .values(**values)
        )
