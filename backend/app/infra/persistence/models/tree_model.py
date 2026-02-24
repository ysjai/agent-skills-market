from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.persistence.db.base import Base

if TYPE_CHECKING:
    from app.domain.aggregates.tree import Tree


class TreeModel(Base):
    __tablename__ = "trees"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )

    def to_domain(self) -> Tree:
        from app.domain.aggregates.tree import Tree

        entries_data = self.data.get("entries", [])

        tree = Tree(
            id=self.id,
            created_at=self.created_at,
        )

        for entry_data in entries_data:
            tree._add_entry_from_dict(entry_data)

        return tree

    @classmethod
    def from_domain(cls, tree: Tree) -> TreeModel:
        return cls(
            id=tree.id,
            data=tree.to_dict(),
            created_at=tree.created_at,
        )
