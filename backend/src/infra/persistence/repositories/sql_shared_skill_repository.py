from __future__ import annotations

from typing import final
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.entities.skill_like import SkillLike
from src.domain.repositories.shared_skill_repository import SharedSkillRepository
from src.infra.persistence.models.shared_skill_model import SharedSkillModel, SkillLikeModel
from src.infra.persistence.models.skill_model import SkillModel


@final
class SqlSharedSkillRepository(SharedSkillRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db: AsyncSession = db

    @override
    async def save(self, shared_skill: SharedSkill) -> SharedSkill:
        model = await self._db.merge(SharedSkillModel.from_domain(shared_skill))
        await self._db.flush()
        return model.to_domain()

    @override
    async def find_by_id(self, id: UUID) -> SharedSkill | None:
        result = await self._db.execute(select(SharedSkillModel).where(SharedSkillModel.id == id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    @override
    async def find_by_skill_id(self, skill_id: UUID) -> SharedSkill | None:
        result = await self._db.execute(
            select(SharedSkillModel).where(
                SharedSkillModel.skill_id == skill_id,
                SharedSkillModel.status == "active",
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    @override
    async def find_by_user_and_skill(self, user_id: UUID, skill_id: UUID) -> SharedSkill | None:
        result = await self._db.execute(
            select(SharedSkillModel).where(
                SharedSkillModel.user_id == user_id,
                SharedSkillModel.skill_id == skill_id,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    @override
    async def find_all_by_skill_id(self, skill_id: UUID) -> list[SharedSkill]:
        result = await self._db.execute(
            select(SharedSkillModel)
            .where(SharedSkillModel.skill_id == skill_id)
            .order_by(SharedSkillModel.created_at.desc())
        )
        return [model.to_domain() for model in result.scalars().all()]

    @override
    async def find_active_by_filters(
        self,
        keyword: str | None,
        category_id: UUID | None,
        sort_by: str,
        skip: int,
        limit: int,
    ) -> list[SharedSkill]:
        stmt = select(SharedSkillModel).where(SharedSkillModel.status == "active")

        if keyword:
            search = f"%{keyword.strip()}%"
            stmt = stmt.join(
                SkillModel, SharedSkillModel.skill_id == SkillModel.id, isouter=True
            ).where(
                or_(
                    SkillModel.name.ilike(search),
                    SkillModel.description.ilike(search),
                )
            )

        if category_id is not None:
            stmt = stmt.where(SharedSkillModel.category_id == category_id)

        if sort_by == "popular":
            stmt = stmt.order_by(
                SharedSkillModel.like_count.desc(), SharedSkillModel.created_at.desc()
            )
        else:
            stmt = stmt.order_by(SharedSkillModel.created_at.desc())

        result = await self._db.execute(stmt.offset(skip).limit(limit))
        return [model.to_domain() for model in result.scalars().all()]

    @override
    async def count_active_by_filters(self, keyword: str | None, category_id: UUID | None) -> int:
        stmt = (
            select(func.count())
            .select_from(SharedSkillModel)
            .where(SharedSkillModel.status == "active")
        )

        if keyword:
            search = f"%{keyword.strip()}%"
            stmt = stmt.join(
                SkillModel, SharedSkillModel.skill_id == SkillModel.id, isouter=True
            ).where(
                or_(
                    SkillModel.name.ilike(search),
                    SkillModel.description.ilike(search),
                )
            )

        if category_id is not None:
            stmt = stmt.where(SharedSkillModel.category_id == category_id)

        result = await self._db.execute(stmt)
        return int(result.scalar_one())

    @override
    async def delete(self, shared_skill_id: UUID) -> None:
        result = await self._db.execute(
            select(SharedSkillModel).where(SharedSkillModel.id == shared_skill_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._db.delete(model)

    @override
    async def find_like(self, user_id: UUID, shared_skill_id: UUID) -> SkillLike | None:
        result = await self._db.execute(
            select(SkillLikeModel).where(
                SkillLikeModel.user_id == user_id,
                SkillLikeModel.shared_skill_id == shared_skill_id,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    @override
    async def save_like(self, like: SkillLike) -> SkillLike:
        model = await self._db.merge(SkillLikeModel.from_domain(like))
        await self._db.flush()
        return model.to_domain()

    @override
    async def delete_like(self, user_id: UUID, shared_skill_id: UUID) -> None:
        result = await self._db.execute(
            select(SkillLikeModel).where(
                SkillLikeModel.user_id == user_id,
                SkillLikeModel.shared_skill_id == shared_skill_id,
            )
        )
        model = result.scalar_one_or_none()
        if model:
            await self._db.delete(model)

    @override
    async def increment_like_count(self, shared_skill_id: UUID) -> None:
        _ = await self._db.execute(
            update(SharedSkillModel)
            .where(SharedSkillModel.id == shared_skill_id)
            .values(like_count=SharedSkillModel.like_count + 1)
        )

    @override
    async def decrement_like_count(self, shared_skill_id: UUID) -> None:
        _ = await self._db.execute(
            update(SharedSkillModel)
            .where(SharedSkillModel.id == shared_skill_id)
            .values(like_count=SharedSkillModel.like_count - 1)
        )

    @override
    async def increment_favorite_count(self, shared_skill_id: UUID) -> None:
        _ = await self._db.execute(
            update(SharedSkillModel)
            .where(SharedSkillModel.id == shared_skill_id)
            .values(favorite_count=SharedSkillModel.favorite_count + 1)
        )

    @override
    async def decrement_favorite_count(self, shared_skill_id: UUID) -> None:
        _ = await self._db.execute(
            update(SharedSkillModel)
            .where(SharedSkillModel.id == shared_skill_id)
            .values(favorite_count=SharedSkillModel.favorite_count - 1)
        )
