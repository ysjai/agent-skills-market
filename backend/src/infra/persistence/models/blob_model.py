from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, LargeBinary, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.persistence.db.base import Base

if TYPE_CHECKING:
    from src.domain.entities.blob import Blob


class BlobModel(Base):
    __tablename__ = "blobs"
    __table_args__ = (
        UniqueConstraint("content_hash", "compressed", name="uq_blob_content_hash_compressed"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    compressed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reference_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )

    def to_domain(self) -> Blob:
        from src.domain.entities.blob import Blob

        return Blob(
            id=self.id,
            content=self.content,
            checksum=self.content_hash,
            size=self.size,
            compressed=self.compressed,
            reference_count=self.reference_count,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, blob: Blob) -> BlobModel:
        return cls(
            id=blob.id,
            content_hash=blob.checksum,
            content=blob.content,
            size=blob.size,
            compressed=blob.compressed,
            reference_count=blob.reference_count,
            created_at=blob.created_at,
        )
