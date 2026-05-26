from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.persistence.db.base import Base

if TYPE_CHECKING:
    from src.domain.aggregates.prompt import Prompt
    from src.domain.entities.prompt_version import PromptVersion


class PromptModel(Base):
    __tablename__ = "prompts"

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
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(sa.String()),
        nullable=False,
        server_default=text("'{}'"),
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
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

    def to_domain(self) -> Prompt:
        from src.domain.aggregates.prompt import Prompt

        return Prompt(
            id=self.id,
            user_id=self.user_id,
            title=self.title,
            content=self.content,
            description=self.description,
            tags=self.tags if self.tags else [],
            version=self.version,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, prompt: Prompt) -> PromptModel:
        return cls(
            id=prompt.id,
            user_id=prompt.user_id,
            title=prompt.title,
            content=prompt.content,
            description=prompt.description,
            tags=prompt.tags,
            version=prompt.version,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
        )


class PromptVersionModel(Base):
    __tablename__ = "prompt_versions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    prompt_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("prompts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(sa.String()),
        nullable=False,
        server_default=text("'{}'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )

    def to_domain(self) -> PromptVersion:
        from src.domain.entities.prompt_version import PromptVersion

        return PromptVersion(
            id=self.id,
            prompt_id=self.prompt_id,
            version_number=self.version_number,
            title=self.title,
            content=self.content,
            description=self.description,
            tags=self.tags if self.tags else [],
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, version: PromptVersion) -> PromptVersionModel:
        return cls(
            id=version.id,
            prompt_id=version.prompt_id,
            version_number=version.version_number,
            title=version.title,
            content=version.content,
            description=version.description,
            tags=version.tags,
            created_at=version.created_at,
        )
