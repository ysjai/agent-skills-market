# docs/templates/repository_skill.py

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.entities.skill import Skill

from app.domain.value_objects.slug import Slug


class SkillRepository(ABC):
    @abstractmethod
    async def get_by_id(self, skill_id: uuid.UUID) -> Skill | None:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: Slug, user_id: uuid.UUID) -> Skill | None:
        pass

    @abstractmethod
    async def get_by_user(self, user_id: uuid.UUID) -> list[Skill]:
        pass

    @abstractmethod
    async def save(self, skill: Skill) -> None:
        pass

    @abstractmethod
    async def delete(self, skill_id: uuid.UUID) -> None:
        pass


from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.persistence.db.base import Base


class SkillModel(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tree_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.skill_repository import SkillRepository
from app.infra.persistence.models.skill_model import SkillModel


class SqlSkillRepository(SkillRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, skill_id: uuid.UUID) -> Skill | None:
        result = await self._db.execute(
            select(SkillModel).where(
                SkillModel.id == skill_id,
                SkillModel.is_deleted == False,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_slug(
        self,
        slug: Slug,
        user_id: uuid.UUID,
    ) -> Skill | None:
        result = await self._db.execute(
            select(SkillModel).where(
                SkillModel.slug == str(slug),
                SkillModel.user_id == user_id,
                SkillModel.is_deleted == False,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_user(self, user_id: uuid.UUID) -> list[Skill]:
        result = await self._db.execute(
            select(SkillModel)
            .where(
                SkillModel.user_id == user_id,
                SkillModel.is_deleted == False,
            )
            .order_by(SkillModel.created_at.desc())
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def save(self, skill: Skill) -> None:
        model = self._to_model(skill)
        self._db.add(model)
        await self._db.flush()

    async def delete(self, skill_id: uuid.UUID) -> None:
        result = await self._db.execute(select(SkillModel).where(SkillModel.id == skill_id))
        model = result.scalar_one_or_none()
        if model:
            model.is_deleted = True
            await self._db.flush()

    def _to_domain(self, model: SkillModel) -> Skill:
        return Skill(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            slug=Slug(model.slug),
            description=model.description,
            tree_id=model.tree_id,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, skill: Skill) -> SkillModel:
        return SkillModel(
            id=skill.id,
            user_id=skill.user_id,
            name=skill.name,
            slug=str(skill.slug),
            description=skill.description,
            tree_id=skill.tree_id,
            version=skill.version,
            is_deleted=skill.is_deleted,
            created_at=skill.created_at,
            updated_at=skill.updated_at,
        )
