from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.entities.blob import Blob


class UploadBlobResp(BaseModel):
    id: UUID
    content_hash: str = Field(..., min_length=64, max_length=64)
    size: int = Field(..., ge=0)
    compressed: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, blob: Blob) -> "UploadBlobResp":
        return cls(
            id=blob.id,
            content_hash=blob.checksum,
            size=blob.size,
            compressed=blob.compressed,
            created_at=blob.created_at,
        )


class GetBlobResp(BaseModel):
    id: UUID
    content_hash: str = Field(..., min_length=64, max_length=64)
    size: int = Field(..., ge=0)
    compressed: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, blob: Blob) -> "GetBlobResp":
        return cls(
            id=blob.id,
            content_hash=blob.checksum,
            size=blob.size,
            compressed=blob.compressed,
            created_at=blob.created_at,
        )
