from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.persistence.db.base import Base

if TYPE_CHECKING:
    from src.domain.aggregates.shared_skill import SharedSkill
    from src.domain.entities.skill_like import SkillLike


class SharedSkillModel(Base):
    __tablename__ = "shared_skills"
    __table_args__ = (
        Index("ix_shared_skills_status", "status"),
        Index("ix_shared_skills_category_id", "category_id"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    skill_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    share_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    like_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, server_default=text("0")
    )
    favorite_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        server_default=text("0"),
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'active'"))
    snapshot_name: Mapped[str] = mapped_column(String(255), nullable=False)
    snapshot_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    snapshot_author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        onupdate=text("NOW()"),
        nullable=False,
    )

    def to_domain(self) -> SharedSkill:
        from src.domain.aggregates.shared_skill import SharedSkill

        return SharedSkill(
            id=self.id,
            skill_id=self.skill_id,
            user_id=self.user_id,
            category_id=self.category_id,
            share_message=self.share_message,
            like_count=self.like_count,
            favorite_count=self.favorite_count,
            status=self.status,
            snapshot_name=self.snapshot_name,
            snapshot_description=self.snapshot_description,
            snapshot_author_name=self.snapshot_author_name,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, shared_skill: SharedSkill) -> SharedSkillModel:
        return cls(
            id=shared_skill.id,
            skill_id=shared_skill.skill_id,
            user_id=shared_skill.user_id,
            category_id=shared_skill.category_id,
            share_message=shared_skill.share_message,
            like_count=shared_skill.like_count,
            favorite_count=shared_skill.favorite_count,
            status=shared_skill.status,
            snapshot_name=shared_skill.snapshot_name,
            snapshot_description=shared_skill.snapshot_description,
            snapshot_author_name=shared_skill.snapshot_author_name,
            created_at=shared_skill.created_at,
            updated_at=shared_skill.updated_at,
        )


class SkillLikeModel(Base):
    __tablename__ = "skill_likes"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shared_skill_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("shared_skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )

    def to_domain(self) -> SkillLike:
        from src.domain.entities.skill_like import SkillLike

        return SkillLike(
            id=self.id,
            user_id=self.user_id,
            shared_skill_id=self.shared_skill_id,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, skill_like: SkillLike) -> SkillLikeModel:
        return cls(
            id=skill_like.id,
            user_id=skill_like.user_id,
            shared_skill_id=skill_like.shared_skill_id,
            created_at=skill_like.created_at,
        )
