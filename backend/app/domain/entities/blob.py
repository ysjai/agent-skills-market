from __future__ import annotations

import hashlib
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class Blob:
    id: UUID = field(default_factory=uuid4)
    content: bytes = field(default_factory=bytes)
    checksum: str = field(default="")
    size: int = field(default=0)
    compressed: bool = field(default=False)
    reference_count: int = field(default=0)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.content and not self.size:
            self.size = len(self.content)
        if self.content and not self.checksum:
            self.checksum = self._calculate_hash(self.get_raw_content())

    @classmethod
    def create(cls, content: bytes, compressed: bool = False) -> Blob:
        if not content:
            raise ValueError("Blob content cannot be empty")

        checksum = cls._calculate_hash(content)
        size = len(content)

        return cls(
            id=uuid4(),
            content=content,
            checksum=checksum,
            size=size,
            compressed=compressed,
            reference_count=0,
        )

    @staticmethod
    def _calculate_hash(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def validate_content(self) -> bool:
        if not self.content:
            return False
        return self._calculate_hash(self.content) == self.checksum

    def compress(self) -> None:
        if self.compressed:
            return

        self.content = zlib.compress(self.content, level=3)
        self.compressed = True
        self.size = len(self.content)

    def decompress(self) -> None:
        if not self.compressed:
            return

        self.content = zlib.decompress(self.content)
        self.compressed = False
        self.size = len(self.content)

    def get_raw_content(self) -> bytes:
        if self.compressed:
            try:
                return zlib.decompress(self.content)
            except zlib.error:
                return self.content
        return self.content

    def increment_reference(self) -> None:
        self.reference_count += 1

    def decrement_reference(self) -> None:
        if self.reference_count > 0:
            self.reference_count -= 1

    def is_orphaned(self) -> bool:
        return self.reference_count == 0

    def is_empty(self) -> bool:
        return not self.content or len(self.content) == 0

    def get_content_preview(self, max_length: int = 100) -> str:
        raw = self.get_raw_content()
        preview = raw[:max_length]
        try:
            return preview.decode("utf-8", errors="replace")
        except (UnicodeDecodeError, AttributeError):
            return f"<binary:{len(raw)}bytes>"
