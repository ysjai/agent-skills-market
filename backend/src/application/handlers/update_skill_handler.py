from uuid import UUID

from src.domain.aggregates.skill import Skill
from src.domain.exceptions import ForbiddenError, ResourceConflictError, ResourceNotFoundError
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.value_objects.slug import Slug


async def handle_update_skill(
    skill_id: UUID,
    user_id: UUID,
    name: str | None,
    description: str | None,
    is_public: bool | None,
    tree_id: UUID | None,
    skill_repo: SkillRepository,
) -> Skill:
    skill = await skill_repo.get_by_id(skill_id)
    if not skill:
        raise ResourceNotFoundError()
    if skill.user_id != user_id:
        raise ForbiddenError("Not authorized to update this skill")
    if name is not None:
        new_slug = Slug.from_name(name)
        existing = await skill_repo.get_by_slug(new_slug, user_id)
        if existing and existing.id != skill_id:
            raise ResourceConflictError()
        skill.update_name(name)
    if description is not None:
        skill.update_description(description)
    if is_public is not None:
        skill.set_public(is_public)
    if tree_id is not None:
        skill.assign_tree(tree_id)
    await skill_repo.save(skill)
    return skill
