from __future__ import annotations

import re
from dataclasses import dataclass

from src.domain.exceptions import ValidationError


@dataclass(frozen=True)
class Slug:
    value: str

    _VALID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    _MAX_LENGTH = 128

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", self._validate(self.value))

    @classmethod
    def _validate(cls, value: str) -> str:
        if not value:
            raise ValidationError("Slug cannot be empty")
        value = value.lower()
        if len(value) > cls._MAX_LENGTH:
            raise ValidationError(f"Slug cannot exceed {cls._MAX_LENGTH} characters")
        if not cls._VALID_PATTERN.match(value):
            raise ValidationError("Slug must contain only lowercase letters, numbers, and hyphens")
        return value

    @classmethod
    def from_name(cls, name: str) -> Slug:
        slug = name.lower().strip()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s]+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        if not slug:
            raise ValidationError("Cannot generate slug from empty name")
        return cls(slug)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Slug):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
