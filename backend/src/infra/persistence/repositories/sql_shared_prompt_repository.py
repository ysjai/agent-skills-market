from __future__ import annotations

from typing import final
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from src.domain.aggregates.shared_prompt import SharedPrompt
from src.domain.entities.prompt_like import PromptLike
from src.domain.repositories.shared_prompt_repository import SharedPromptRepository
from src.infra.persistence.models.prompt_model import PromptModel
from src.infra.persistence.models.shared_prompt_model import PromptLikeModel, SharedPromptModel


@final
class SqlSharedPromptRepository(SharedPromptRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db: AsyncSession = db

    @override
    async def save(self, shared_prompt: SharedPrompt) -> SharedPrompt:
        model = await self._db.merge(SharedPromptModel.from_domain(shared_prompt))
        await self._db.flush()
        return model.to_domain()

    @override
    async def find_by_id(self, id: UUID) -> SharedPrompt | None:
        result = await self._db.execute(select(SharedPromptModel).where(SharedPromptModel.id == id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    @override
    async def find_by_prompt_id(self, prompt_id: UUID) -> SharedPrompt | None:
        result = await self._db.execute(
            select(SharedPromptModel).where(
                SharedPromptModel.prompt_id == prompt_id,
                SharedPromptModel.status == "active",
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    @override
    async def find_by_user_and_prompt(self, user_id: UUID, prompt_id: UUID) -> SharedPrompt | None:
        result = await self._db.execute(
            select(SharedPromptModel).where(
                SharedPromptModel.user_id == user_id,
                SharedPromptModel.prompt_id == prompt_id,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    @override
    async def find_all_by_prompt_id(self, prompt_id: UUID) -> list[SharedPrompt]:
        result = await self._db.execute(
            select(SharedPromptModel)
            .where(SharedPromptModel.prompt_id == prompt_id)
            .order_by(SharedPromptModel.created_at.desc())
        )
        return [model.to_domain() for model in result.scalars().all()]

    @override
    async def find_active_by_filters(
        self,
        keyword: str | None,
        tags: list[str] | None,
        sort_by: str,
        skip: int,
        limit: int,
        user_id: UUID | None = None,
    ) -> list[SharedPrompt]:
        stmt = select(SharedPromptModel).where(SharedPromptModel.status == "active")

        if user_id:
            stmt = stmt.where(SharedPromptModel.user_id == user_id)

        if keyword or tags:
            stmt = stmt.join(
                PromptModel,
                SharedPromptModel.prompt_id == PromptModel.id,
                isouter=True,
            )

        if keyword:
            search = f"%{keyword.strip()}%"
            stmt = stmt.where(
                or_(
                    PromptModel.title.ilike(search),
                    PromptModel.description.ilike(search),
                )
            )

        if tags:
            stmt = stmt.where(PromptModel.tags.overlap(tags))

        if sort_by == "popular":
            stmt = stmt.order_by(
                SharedPromptModel.like_count.desc(), SharedPromptModel.created_at.desc()
            )
        else:
            stmt = stmt.order_by(SharedPromptModel.created_at.desc())

        result = await self._db.execute(stmt.offset(skip).limit(limit))
        return [model.to_domain() for model in result.scalars().all()]

    @override
    async def count_active_by_filters(
        self, keyword: str | None, tags: list[str] | None, user_id: UUID | None = None
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(SharedPromptModel)
            .where(SharedPromptModel.status == "active")
        )

        if user_id:
            stmt = stmt.where(SharedPromptModel.user_id == user_id)

        if keyword or tags:
            stmt = stmt.join(
                PromptModel,
                SharedPromptModel.prompt_id == PromptModel.id,
                isouter=True,
            )

        if keyword:
            search = f"%{keyword.strip()}%"
            stmt = stmt.where(
                or_(
                    PromptModel.title.ilike(search),
                    PromptModel.description.ilike(search),
                )
            )

        if tags:
            stmt = stmt.where(PromptModel.tags.overlap(tags))

        result = await self._db.execute(stmt)
        return int(result.scalar_one())

    @override
    async def delete(self, shared_prompt_id: UUID) -> None:
        result = await self._db.execute(
            select(SharedPromptModel).where(SharedPromptModel.id == shared_prompt_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._db.delete(model)

    @override
    async def find_like(self, user_id: UUID, shared_prompt_id: UUID) -> PromptLike | None:
        result = await self._db.execute(
            select(PromptLikeModel).where(
                PromptLikeModel.user_id == user_id,
                PromptLikeModel.shared_prompt_id == shared_prompt_id,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    @override
    async def save_like(self, like: PromptLike) -> PromptLike:
        model = await self._db.merge(PromptLikeModel.from_domain(like))
        await self._db.flush()
        return model.to_domain()

    @override
    async def delete_like(self, user_id: UUID, shared_prompt_id: UUID) -> None:
        result = await self._db.execute(
            select(PromptLikeModel).where(
                PromptLikeModel.user_id == user_id,
                PromptLikeModel.shared_prompt_id == shared_prompt_id,
            )
        )
        model = result.scalar_one_or_none()
        if model:
            await self._db.delete(model)

    @override
    async def increment_like_count(self, shared_prompt_id: UUID) -> None:
        _ = await self._db.execute(
            update(SharedPromptModel)
            .where(SharedPromptModel.id == shared_prompt_id)
            .values(like_count=SharedPromptModel.like_count + 1)
        )

    @override
    async def decrement_like_count(self, shared_prompt_id: UUID) -> None:
        _ = await self._db.execute(
            update(SharedPromptModel)
            .where(SharedPromptModel.id == shared_prompt_id)
            .values(like_count=SharedPromptModel.like_count - 1)
        )

    @override
    async def increment_favorite_count(self, shared_prompt_id: UUID) -> None:
        _ = await self._db.execute(
            update(SharedPromptModel)
            .where(SharedPromptModel.id == shared_prompt_id)
            .values(favorite_count=SharedPromptModel.favorite_count + 1)
        )

    @override
    async def decrement_favorite_count(self, shared_prompt_id: UUID) -> None:
        _ = await self._db.execute(
            update(SharedPromptModel)
            .where(SharedPromptModel.id == shared_prompt_id)
            .values(favorite_count=SharedPromptModel.favorite_count - 1)
        )
