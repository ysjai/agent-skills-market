from __future__ import annotations

import hashlib
import zlib
from uuid import uuid4

from app.domain.entities.blob import Blob


class BlobFactory:
    @classmethod
    def create_from_content(
        cls,
        content: bytes,
        compressed: bool = False,
    ) -> Blob:
        original_checksum = cls._calculate_hash(content) if content else cls._empty_hash()
        original_size = len(content)

        if compressed and content:
            stored_content = zlib.compress(content, level=3)
            actually_compressed = True
        else:
            stored_content = content
            actually_compressed = False if not content else compressed

        return Blob(
            id=uuid4(),
            content=stored_content,
            checksum=original_checksum,
            size=original_size,
            compressed=actually_compressed,
            reference_count=0,
        )

    @staticmethod
    def _calculate_hash(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def _empty_hash() -> str:
        return hashlib.sha256(b"").hexdigest()
