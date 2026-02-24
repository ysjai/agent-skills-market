from uuid import UUID

from src.domain.aggregates.skill import Skill
from src.domain.exceptions import ResourceConflictError
from src.domain.factories.skill_factory import SkillFactory
from src.domain.factories.tree_factory import TreeFactory
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository
from src.domain.value_objects.slug import Slug


async def handle_create_skill(
    user_id: UUID,
    name: str,
    description: str | None,
    skill_repo: SkillRepository,
    tree_repo: TreeRepository,
) -> Skill:
    slug = Slug.from_name(name)
    existing = await skill_repo.get_by_slug(slug, user_id)
    if existing:
        raise ResourceConflictError()

    tree = TreeFactory.create()
    await tree_repo.save(tree)
    await tree_repo.flush()  # Flush tree to DB before saving skill with tree_id

    skill = SkillFactory.create(user_id=user_id, name=name, description=description)
    skill.assign_tree(tree.id)
    await skill_repo.save(skill)
    return skill
