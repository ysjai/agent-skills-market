from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.aggregates.skill import Skill
from src.domain.aggregates.skill_favorite import SkillFavorite


class SkillFavoriteFactory:
    @classmethod
    def create(
        cls,
        user_id: UUID,
        shared_skill: SharedSkill,
        skill: Skill | None,
    ) -> SkillFavorite:
        return SkillFavorite(
            id=uuid4(),
            user_id=user_id,
            shared_skill_id=shared_skill.id,
            snapshot_name=skill.name if skill is not None else shared_skill.snapshot_name,
            snapshot_description=(
                skill.description if skill is not None else shared_skill.snapshot_description
            ),
            snapshot_slug=str(skill.slug) if skill is not None else "",
            snapshot_author_name=shared_skill.snapshot_author_name,
            snapshot_status="active",
            created_at=datetime.now(timezone.utc),
        )
