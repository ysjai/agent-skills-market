from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.aggregates.skill import Skill
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.value_objects.slug import Slug
from src.infra.persistence.models.skill_model import SkillModel


class SqlSkillRepository(SkillRepository):

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, skill_id: UUID) -> Skill | None:
        result = await self._db.execute(select(SkillModel).where(SkillModel.id == skill_id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_slug(self, slug: Slug, user_id: UUID) -> Skill | None:
        result = await self._db.execute(
            select(SkillModel).where(
                SkillModel.slug == str(slug),
                SkillModel.user_id == user_id,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_by_user(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Skill]:
        result = await self._db.execute(
            select(SkillModel)
            .where(SkillModel.user_id == user_id)
            .order_by(SkillModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def save(self, skill: Skill) -> None:
        model = SkillModel.from_domain(skill)
        await self._db.merge(model)
        await self._db.flush()

    async def delete(self, skill_id: UUID) -> None:
        result = await self._db.execute(select(SkillModel).where(SkillModel.id == skill_id))
        model = result.scalar_one_or_none()
        if model:
            await self._db.delete(model)
