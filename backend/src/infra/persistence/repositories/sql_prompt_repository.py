from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.aggregates.prompt import Prompt
from src.domain.entities.prompt_version import PromptVersion
from src.domain.repositories.prompt_repository import PromptRepository
from src.infra.persistence.models.prompt_model import PromptModel, PromptVersionModel


class SqlPromptRepository(PromptRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, prompt_id: UUID) -> Prompt | None:
        result = await self._db.execute(select(PromptModel).where(PromptModel.id == prompt_id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_by_user(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 20,
        tag: str | None = None,
        search: str | None = None,
    ) -> list[Prompt]:
        stmt = select(PromptModel).where(PromptModel.user_id == user_id)

        if tag is not None:
            stmt = stmt.where(PromptModel.tags.contains([tag]))

        if search is not None:
            stmt = stmt.where(PromptModel.title.ilike(f"%{search}%"))

        stmt = stmt.order_by(PromptModel.created_at.desc()).offset(offset).limit(limit)

        result = await self._db.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]

    async def count_by_user(
        self,
        user_id: UUID,
        tag: str | None = None,
        search: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(PromptModel).where(PromptModel.user_id == user_id)

        if tag is not None:
            stmt = stmt.where(PromptModel.tags.contains([tag]))

        if search is not None:
            stmt = stmt.where(PromptModel.title.ilike(f"%{search}%"))

        result = await self._db.execute(stmt)
        return result.scalar_one()

    async def save(self, prompt: Prompt) -> None:
        model = PromptModel.from_domain(prompt)
        await self._db.merge(model)
        await self._db.flush()

    async def delete(self, prompt_id: UUID) -> None:
        result = await self._db.execute(select(PromptModel).where(PromptModel.id == prompt_id))
        model = result.scalar_one_or_none()
        if model:
            await self._db.delete(model)

    async def save_version(self, version: PromptVersion) -> None:
        model = PromptVersionModel.from_domain(version)
        await self._db.merge(model)
        await self._db.flush()

    async def get_versions(self, prompt_id: UUID) -> list[PromptVersion]:
        result = await self._db.execute(
            select(PromptVersionModel)
            .where(PromptVersionModel.prompt_id == prompt_id)
            .order_by(PromptVersionModel.version_number.asc())
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def get_version_by_id(self, version_id: UUID) -> PromptVersion | None:
        result = await self._db.execute(
            select(PromptVersionModel).where(PromptVersionModel.id == version_id)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None
