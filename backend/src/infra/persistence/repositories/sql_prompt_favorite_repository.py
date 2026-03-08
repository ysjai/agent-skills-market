from __future__ import annotations

from typing import final
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.aggregates.prompt_favorite import PromptFavorite
from src.domain.repositories.prompt_favorite_repository import PromptFavoriteRepository
from src.infra.persistence.models.prompt_favorite_model import PromptFavoriteModel


@final
class SqlPromptFavoriteRepository(PromptFavoriteRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def save(self, favorite: PromptFavorite) -> PromptFavorite:
        model = await self._db.merge(PromptFavoriteModel.from_domain(favorite))
        await self._db.flush()
        return model.to_domain()

    async def find_by_id(self, favorite_id: UUID) -> PromptFavorite | None:
        result = await self._db.execute(
            select(PromptFavoriteModel).where(PromptFavoriteModel.id == favorite_id)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model is not None else None

    async def delete(self, user_id: UUID, shared_prompt_id: UUID) -> None:
        result = await self._db.execute(
            select(PromptFavoriteModel).where(
                PromptFavoriteModel.user_id == user_id,
                PromptFavoriteModel.shared_prompt_id == shared_prompt_id,
            )
        )
        model = result.scalar_one_or_none()
        if model is not None:
            await self._db.delete(model)

    async def find_by_user_and_shared_prompt(
        self, user_id: UUID, shared_prompt_id: UUID
    ) -> PromptFavorite | None:
        result = await self._db.execute(
            select(PromptFavoriteModel).where(
                PromptFavoriteModel.user_id == user_id,
                PromptFavoriteModel.shared_prompt_id == shared_prompt_id,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model is not None else None

    async def find_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[PromptFavorite]:
        result = await self._db.execute(
            select(PromptFavoriteModel)
            .where(PromptFavoriteModel.user_id == user_id)
            .order_by(PromptFavoriteModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def count_by_user(self, user_id: UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .select_from(PromptFavoriteModel)
            .where(PromptFavoriteModel.user_id == user_id)
        )
        return int(result.scalar_one())

    async def update_batch_status(self, shared_prompt_id: UUID, status: str) -> None:
        values: dict[str, object] = {"snapshot_status": status}
        if status == "prompt_deleted":
            values["shared_prompt_id"] = None

        _ = await self._db.execute(
            update(PromptFavoriteModel)
            .where(PromptFavoriteModel.shared_prompt_id == shared_prompt_id)
            .values(**values)
        )
