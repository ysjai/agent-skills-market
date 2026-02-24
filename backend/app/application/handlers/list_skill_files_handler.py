from uuid import UUID

from app.domain.exceptions import ResourceNotFoundError
from app.domain.repositories.skill_repository import SkillRepository
from app.domain.repositories.tree_repository import TreeRepository


async def handle_list_skill_files(
    skill_id: UUID,
    user_id: UUID,
    skill_repo: SkillRepository,
    tree_repo: TreeRepository,
) -> tuple:
    """List all files for a skill."""
    skill = await skill_repo.get_by_id(skill_id)
    if not skill or skill.user_id != user_id:
        raise ResourceNotFoundError()

    if not skill.tree_id:
        return skill, []

    tree = await tree_repo.get_by_id(skill.tree_id)
    if not tree:
        return skill, []

    return skill, tree.entries
