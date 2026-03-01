from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.aggregates.prompt import Prompt
from src.domain.exceptions import ValidationError


class PromptFactory:
    _MAX_TITLE_LENGTH = 200
    _MAX_DESCRIPTION_LENGTH = 1000
    _MAX_TAG_LENGTH = 50
    _MAX_TAGS_COUNT = 20

    @classmethod
    def create(
        cls,
        user_id: UUID,
        title: str,
        content: str,
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> Prompt:
        """Create a new Prompt with validation."""
        validated_title = cls._validate_title(title)
        validated_description = cls._validate_description(description)
        validated_tags = cls._validate_tags(tags or [])

        now = datetime.now(timezone.utc)

        return Prompt(
            id=uuid4(),
            user_id=user_id,
            title=validated_title,
            content=content,
            description=validated_description,
            tags=validated_tags,
            version=1,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def _validate_title(cls, title: str) -> str:
        """Validate prompt title."""
        if not title:
            raise ValidationError("Prompt title cannot be empty")

        stripped = title.strip()

        if not stripped:
            raise ValidationError("Prompt title cannot be empty")

        if len(stripped) > cls._MAX_TITLE_LENGTH:
            raise ValidationError(f"Prompt title cannot exceed {cls._MAX_TITLE_LENGTH} characters")

        return stripped

    @classmethod
    def _validate_description(cls, description: str | None) -> str | None:
        """Validate prompt description."""
        if description is None:
            return None

        if len(description) > cls._MAX_DESCRIPTION_LENGTH:
            raise ValidationError(
                f"Description cannot exceed {cls._MAX_DESCRIPTION_LENGTH} characters"
            )

        return description

    @classmethod
    def _validate_tags(cls, tags: list[str]) -> list[str]:
        """Validate and normalize tags."""
        normalized = []

        for tag in tags:
            # Strip whitespace and convert to lowercase
            normalized_tag = tag.strip().lower()

            # Validate tag length
            if len(normalized_tag) > cls._MAX_TAG_LENGTH:
                raise ValidationError(f"Tag cannot exceed {cls._MAX_TAG_LENGTH} characters")

            # Only add non-empty tags
            if normalized_tag:
                normalized.append(normalized_tag)

        # Deduplicate
        normalized = list(dict.fromkeys(normalized))

        # Check max tags count
        if len(normalized) > cls._MAX_TAGS_COUNT:
            raise ValidationError(f"Cannot have more than {cls._MAX_TAGS_COUNT} tags")

        return normalized
