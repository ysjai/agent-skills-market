from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.aggregates.skill import Skill
from app.domain.exceptions import ValidationError
from app.domain.value_objects.slug import Slug


class SkillFactory:
    _MAX_NAME_LENGTH = 128
    _MAX_DESCRIPTION_LENGTH = 2048

    @classmethod
    def create(
        cls,
        user_id: UUID,
        name: str,
        description: str | None = None,
        slug: str | None = None,
    ) -> Skill:
        validated_name = cls._validate_name(name)
        validated_description = cls._validate_description(description)

        if slug:
            skill_slug = Slug(slug)
        else:
            skill_slug = Slug.from_name(validated_name)

        now = datetime.now(timezone.utc)

        return Skill(
            id=uuid4(),
            user_id=user_id,
            name=validated_name,
            slug=skill_slug,
            description=validated_description or "",
            version=1,
            created_at=now,
            updated_at=now,
            is_public=False,
        )

    @classmethod
    def _validate_name(cls, name: str) -> str:
        if not name:
            raise ValidationError("Skill name cannot be empty")

        stripped = name.strip()

        if not stripped:
            raise ValidationError("Skill name cannot be empty")

        if len(stripped) > cls._MAX_NAME_LENGTH:
            raise ValidationError(f"Skill name cannot exceed {cls._MAX_NAME_LENGTH} characters")

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
