from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import ClassVar

from typing_extensions import override

from app.domain.exceptions import ValidationError


@dataclass(frozen=True)
class Path:
    value: str

    _MAX_LENGTH: ClassVar[int] = 512
    _TRAVERSAL_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\.\.|~")

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", self._validate(self.value))

    @classmethod
    def _validate(cls, value: str) -> str:
        if len(value) > cls._MAX_LENGTH:
            raise ValidationError(f"Path cannot exceed {cls._MAX_LENGTH} characters")

        if not value:
            return value

        if cls._TRAVERSAL_PATTERN.search(value):
            raise ValidationError("Path contains traversal sequences")

        is_dir = value.endswith("/")

        normalized = os.path.normpath(value)

        if normalized.startswith("/"):
            raise ValidationError("Path must be relative (cannot start with /)")

        if ".." in normalized:
            raise ValidationError("Path contains traversal sequences")

        if is_dir and not normalized.endswith("/"):
            normalized += "/"

        return normalized

    def is_directory(self) -> bool:
        return self.value.endswith("/")

    def is_file(self) -> bool:
        return bool(self.value) and not self.is_directory()

    def extension(self) -> str | None:
        if self.is_directory():
            return None
        parts = self.value.rsplit(".", 1)
        return parts[-1] if len(parts) > 1 and parts[-1] else None

    def has_extension(self) -> bool:
        return self.extension() is not None

    def filename(self) -> str | None:
        if not self.value:
            return None
        return self.value.rstrip("/").split("/")[-1]

    def parent(self) -> Path:
        if not self.value or "/" not in self.value.rstrip("/"):
            return Path("")
        parent_path = str(PurePosixPath(self.value).parent)
        if self.is_directory() and parent_path:
            parent_path += "/"
        return Path(parent_path)

    def join(self, other: str) -> Path:
        if not self.value:
            return Path(other)
        base = self.value.rstrip("/")
        return Path(f"{base}/{other}")

    @override
    def __str__(self) -> str:
        return self.value

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Path):
            return NotImplemented
        return self.value == other.value

    @override
    def __hash__(self) -> int:
        return hash(self.value)

    def __truediv__(self, other: str) -> Path:
        return self.join(other)
