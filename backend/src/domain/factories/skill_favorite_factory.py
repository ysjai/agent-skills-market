from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.aggregates.skill import Skill
from src.domain.aggregates.skill_favorite import SkillFavorite
from src.domain.aggregates.user import User


class SkillFavoriteFactory:
    @classmethod
    def create(
        cls,
        user_id: UUID,
        shared_skill: SharedSkill,
        skill: Skill | None,
        shared_by: User | None = None,
    ) -> SkillFavorite:
        return SkillFavorite(
            id=uuid4(),
            user_id=user_id,
            shared_skill_id=shared_skill.id,
            snapshot_name=skill.name if skill is not None else "",
            snapshot_description=(skill.description if skill is not None else None),
            snapshot_slug=str(skill.slug) if skill is not None else "",
            snapshot_author_name=shared_by.username if shared_by is not None else "",
            snapshot_status="active",
            created_at=datetime.now(timezone.utc),
        )
