from uuid import UUID

from app.domain.aggregates.skill import Skill
from app.domain.repositories.skill_repository import SkillRepository


async def handle_list_skills(
    user_id: UUID,
    offset: int,
    limit: int,
    skill_repo: SkillRepository,
) -> list[Skill]:
    skills = await skill_repo.find_by_user(user_id, offset=offset, limit=limit)
    return skills
