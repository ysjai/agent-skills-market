from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.aggregates.tree import Tree
from src.domain.repositories.tree_repository import TreeRepository
from src.infra.persistence.models.tree_model import TreeModel


class SqlTreeRepository(TreeRepository):

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, tree_id: UUID) -> Tree | None:
        result = await self._db.execute(select(TreeModel).where(TreeModel.id == tree_id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def save(self, tree: Tree) -> None:
        model = TreeModel.from_domain(tree)
        await self._db.merge(model)

    async def delete(self, tree_id: UUID) -> None:
        result = await self._db.execute(select(TreeModel).where(TreeModel.id == tree_id))
        model = result.scalar_one_or_none()
        if model:
            await self._db.delete(model)

    async def flush(self) -> None:
        await self._db.flush()
