from typing import final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from src.domain.aggregates.category import Category
from src.domain.repositories.category_repository import CategoryRepository
from src.infra.persistence.models.category_model import CategoryModel


@final
class SqlCategoryRepository(CategoryRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db: AsyncSession = db

    @override
    async def get_by_id(self, category_id: UUID) -> Category | None:
        result = await self._db.execute(
            select(CategoryModel).where(CategoryModel.id == category_id)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    @override
    async def get_all_active(self) -> list[Category]:
        result = await self._db.execute(
            select(CategoryModel)
            .where(CategoryModel.is_active)
            .order_by(CategoryModel.display_order)
        )
        return [model.to_domain() for model in result.scalars().all()]
