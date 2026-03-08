from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import DateTime, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.persistence.db.base import Base

if TYPE_CHECKING:
    from src.domain.aggregates.prompt_favorite import PromptFavorite


class PromptFavoriteModel(Base):
    __tablename__: str = "prompt_favorites"
    __table_args__: tuple[Index, ...] = (
        Index(
            "uq_prompt_favorites_user_id_shared_prompt_id",
            "user_id",
            "shared_prompt_id",
            unique=True,
            postgresql_where=text("shared_prompt_id IS NOT NULL"),
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
    shared_prompt_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    snapshot_title: Mapped[str] = mapped_column(String(200), nullable=False)
    snapshot_content: Mapped[str] = mapped_column(Text, nullable=False)
    snapshot_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    snapshot_tags: Mapped[list[str]] = mapped_column(
        ARRAY(sa.String()),
        nullable=False,
        server_default=text("'{}'"),
    )
    snapshot_author_name: Mapped[str] = mapped_column(String(100), nullable=False)
    snapshot_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    snapshot_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
        server_default=text("'active'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )

    def to_domain(self) -> PromptFavorite:
        from src.domain.aggregates.prompt_favorite import PromptFavorite

        return PromptFavorite(
            id=self.id,
            user_id=self.user_id,
            shared_prompt_id=self.shared_prompt_id,
            snapshot_title=self.snapshot_title,
            snapshot_content=self.snapshot_content,
            snapshot_description=self.snapshot_description,
            snapshot_tags=self.snapshot_tags if self.snapshot_tags else [],
            snapshot_author_name=self.snapshot_author_name,
            snapshot_version=self.snapshot_version,
            snapshot_status=self.snapshot_status,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, prompt_favorite: PromptFavorite) -> PromptFavoriteModel:
        return cls(
            id=prompt_favorite.id,
            user_id=prompt_favorite.user_id,
            shared_prompt_id=prompt_favorite.shared_prompt_id,
            snapshot_title=prompt_favorite.snapshot_title,
            snapshot_content=prompt_favorite.snapshot_content,
            snapshot_description=prompt_favorite.snapshot_description,
            snapshot_tags=prompt_favorite.snapshot_tags,
            snapshot_author_name=prompt_favorite.snapshot_author_name,
            snapshot_version=prompt_favorite.snapshot_version,
            snapshot_status=prompt_favorite.snapshot_status,
            created_at=prompt_favorite.created_at,
        )
