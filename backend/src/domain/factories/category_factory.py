from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.domain.aggregates.category import Category
from src.domain.exceptions import ValidationError
from src.domain.value_objects.slug import Slug


class CategoryFactory:
    _MAX_NAME_LENGTH = 128
    _MAX_DESCRIPTION_LENGTH = 1024

    @classmethod
    def create(
        cls,
        name: str,
        slug: Slug,
        description: str | None = None,
        display_order: int = 0,
    ) -> Category:
        validated_name = cls._validate_name(name)
        validated_description = cls._validate_description(description)

        now = datetime.now(timezone.utc)

        return Category(
            id=uuid4(),
            name=validated_name,
            slug=slug,
            description=validated_description,
            display_order=display_order,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def _validate_name(cls, name: str) -> str:
        if not name:
            raise ValidationError("Category name cannot be empty")

        stripped = name.strip()

        if not stripped:
            raise ValidationError("Category name cannot be empty")

        if len(stripped) > cls._MAX_NAME_LENGTH:
            raise ValidationError(f"Category name cannot exceed {cls._MAX_NAME_LENGTH} characters")

        return stripped

    @classmethod
    def _validate_description(cls, description: str | None) -> str | None:
        if description is None:
            return None

        if len(description) > cls._MAX_DESCRIPTION_LENGTH:
            raise ValidationError(
                f"Description cannot exceed {cls._MAX_DESCRIPTION_LENGTH} characters"
            )

        return description
