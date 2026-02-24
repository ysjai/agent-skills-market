from uuid import UUID

from app.domain.aggregates.skill import Skill
from app.domain.exceptions import ResourceConflictError
from app.domain.factories.skill_factory import SkillFactory
from app.domain.factories.tree_factory import TreeFactory
from app.domain.repositories.skill_repository import SkillRepository
from app.domain.repositories.tree_repository import TreeRepository
from app.domain.value_objects.slug import Slug


async def handle_import_skill(
    user_id: UUID,
    name: str,
    skill_repo: SkillRepository,
    tree_repo: TreeRepository,
    description: str | None = None,
    slug: str | None = None,
) -> Skill:
    skill_slug = Slug(slug) if slug else Slug.from_name(name)
    existing = await skill_repo.get_by_slug(skill_slug, user_id)
    if existing:
        raise ResourceConflictError()

    tree = TreeFactory.create()
    await tree_repo.save(tree)
    await tree_repo.flush()

    skill = SkillFactory.create(user_id=user_id, name=name, description=description, slug=slug)
    skill.assign_tree(tree.id)
    await skill_repo.save(skill)
    return skill
