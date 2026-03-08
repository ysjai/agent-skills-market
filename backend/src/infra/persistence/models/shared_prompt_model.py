from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.persistence.db.base import Base

if TYPE_CHECKING:
    from src.domain.aggregates.shared_prompt import SharedPrompt
    from src.domain.entities.prompt_like import PromptLike


class SharedPromptModel(Base):
    __tablename__ = "shared_prompts"
    __table_args__ = (
        Index("ix_shared_prompts_status", "status"),
        Index("ix_shared_prompts_user_id", "user_id"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    prompt_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("prompts.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
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

    def to_domain(self) -> SharedPrompt:
        from src.domain.aggregates.shared_prompt import SharedPrompt

        return SharedPrompt(
            id=self.id,
            prompt_id=self.prompt_id,
            user_id=self.user_id,
            share_message=self.share_message,
            like_count=self.like_count,
            favorite_count=self.favorite_count,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, shared_prompt: SharedPrompt) -> SharedPromptModel:
        return cls(
            id=shared_prompt.id,
            prompt_id=shared_prompt.prompt_id,
            user_id=shared_prompt.user_id,
            share_message=shared_prompt.share_message,
            like_count=shared_prompt.like_count,
            favorite_count=shared_prompt.favorite_count,
            status=shared_prompt.status,
            created_at=shared_prompt.created_at,
            updated_at=shared_prompt.updated_at,
        )


class PromptLikeModel(Base):
    __tablename__ = "prompt_likes"

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
    shared_prompt_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("shared_prompts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )

    def to_domain(self) -> PromptLike:
        from src.domain.entities.prompt_like import PromptLike

        return PromptLike(
            id=self.id,
            user_id=self.user_id,
            shared_prompt_id=self.shared_prompt_id,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, prompt_like: PromptLike) -> PromptLikeModel:
        return cls(
            id=prompt_like.id,
            user_id=prompt_like.user_id,
            shared_prompt_id=prompt_like.shared_prompt_id,
            created_at=prompt_like.created_at,
        )
