from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.persistence.db.base import Base

if TYPE_CHECKING:
    from src.domain.aggregates.skill_favorite import SkillFavorite


class SkillFavoriteModel(Base):
    __tablename__: str = "skill_favorites"
    __table_args__: tuple[Index, ...] = (
        Index(
            "uq_skill_favorites_user_id_shared_skill_id",
            "user_id",
            "shared_skill_id",
            unique=True,
            postgresql_where=text("shared_skill_id IS NOT NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    shared_skill_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    snapshot_name: Mapped[str] = mapped_column(String(255), nullable=False)
    snapshot_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    snapshot_slug: Mapped[str] = mapped_column(String(255), nullable=False)
    snapshot_author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    snapshot_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
        server_default=text("'active'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )

    def to_domain(self) -> SkillFavorite:
        from src.domain.aggregates.skill_favorite import SkillFavorite

        return SkillFavorite(
            id=self.id,
            user_id=self.user_id,
            shared_skill_id=self.shared_skill_id,
            snapshot_name=self.snapshot_name,
            snapshot_description=self.snapshot_description,
            snapshot_slug=self.snapshot_slug,
            snapshot_author_name=self.snapshot_author_name,
            snapshot_status=self.snapshot_status,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, skill_favorite: SkillFavorite) -> SkillFavoriteModel:
        return cls(
            id=skill_favorite.id,
            user_id=skill_favorite.user_id,
            shared_skill_id=skill_favorite.shared_skill_id,
            snapshot_name=skill_favorite.snapshot_name,
            snapshot_description=skill_favorite.snapshot_description,
            snapshot_slug=skill_favorite.snapshot_slug,
            snapshot_author_name=skill_favorite.snapshot_author_name,
            snapshot_status=skill_favorite.snapshot_status,
            created_at=skill_favorite.created_at,
        )
