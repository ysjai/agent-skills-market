from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar

from typing_extensions import override

from src.domain.exceptions import ValidationError


@dataclass(frozen=True)
class Email:
    value: str

    _VALID_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    _MAX_LENGTH: ClassVar[int] = 255

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", self._validate(self.value))

    @classmethod
    def _validate(cls, value: str) -> str:
        if not value:
            raise ValidationError("Email cannot be empty")

        normalized = value.strip().lower()

        if len(normalized) > cls._MAX_LENGTH:
            raise ValidationError(f"Email cannot exceed {cls._MAX_LENGTH} characters")

        if not cls._VALID_PATTERN.match(normalized):
            raise ValidationError("Invalid email format")

        local, _, domain = normalized.partition("@")
        if not local or not domain:
            raise ValidationError("Invalid email format")

        if "." not in domain:
            raise ValidationError("Invalid email format")

        return normalized

    @property
    def local_part(self) -> str:
        return self.value.split("@")[0]

    @property
    def domain(self) -> str:
        return self.value.split("@")[1]

    @override
    def __str__(self) -> str:
        return self.value

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return NotImplemented
        return self.value == other.value

    @override
    def __hash__(self) -> int:
        return hash(self.value)
