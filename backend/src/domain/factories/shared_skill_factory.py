from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from src.domain.aggregates.shared_skill import SharedSkill

if TYPE_CHECKING:
    from src.domain.aggregates.skill import Skill
    from src.domain.aggregates.user import User


class SharedSkillFactory:
    @classmethod
    def create(
        cls,
        skill: Skill,
        user: User,
        category_id: UUID,
        share_message: str | None = None,
    ) -> SharedSkill:
        now = datetime.now(timezone.utc)

        return SharedSkill(
            id=uuid4(),
            skill_id=skill.id,
            user_id=user.id,
            category_id=category_id,
            share_message=share_message,
            snapshot_name=skill.name,
            snapshot_description=skill.description,
            snapshot_author_name=user.username,
            created_at=now,
            updated_at=now,
        )
