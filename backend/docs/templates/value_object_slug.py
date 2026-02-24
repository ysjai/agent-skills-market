# docs/templates/value_object_slug.py

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Slug:
    value: str

    _VALID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    _MAX_LENGTH = 100

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", self._validate(self.value))

    @classmethod
    def _validate(cls, value: str) -> str:
        if not value:
            raise ValueError("Slug cannot be empty")
        if len(value) > cls._MAX_LENGTH:
            raise ValueError(f"Slug cannot exceed {cls._MAX_LENGTH} characters")
        if not cls._VALID_PATTERN.match(value):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        return value.lower()

    @classmethod
    def from_name(cls, name: str) -> Slug:
        slug = name.lower().strip()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s]+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        return cls(slug)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Slug):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
