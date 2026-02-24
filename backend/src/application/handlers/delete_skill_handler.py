from uuid import UUID

from src.domain.exceptions import ForbiddenError, ResourceNotFoundError
from src.domain.repositories.blob_repository import BlobRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository


async def handle_delete_skill(
    skill_id: UUID,
    user_id: UUID,
    skill_repo: SkillRepository,
    tree_repo: TreeRepository,
    blob_repo: BlobRepository,
) -> None:
    skill = await skill_repo.get_by_id(skill_id)
    if not skill:
        raise ResourceNotFoundError()
    if skill.user_id != user_id:
        raise ForbiddenError("Not authorized to delete this skill")

    if skill.tree_id:
        tree = await tree_repo.get_by_id(skill.tree_id)
        if tree:
            blob_ids = [entry.blob_id for entry in tree.entries if entry.blob_id]
            for blob_id in blob_ids:
                should_delete = await blob_repo.decrement_reference_count(blob_id)
                if should_delete:
                    await blob_repo.delete(blob_id)

        await tree_repo.delete(skill.tree_id)

    await skill_repo.delete(skill_id)
