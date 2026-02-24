from uuid import UUID

from src.domain.aggregates.skill import Skill
from src.domain.exceptions import ForbiddenError, ResourceNotFoundError
from src.domain.repositories.skill_repository import SkillRepository


async def handle_get_skill(
    skill_id: UUID,
    user_id: UUID,
    skill_repo: SkillRepository,
) -> Skill:
    skill = await skill_repo.get_by_id(skill_id)
    if not skill:
        raise ResourceNotFoundError()
    if skill.user_id != user_id:
        raise ForbiddenError()
    return skill
