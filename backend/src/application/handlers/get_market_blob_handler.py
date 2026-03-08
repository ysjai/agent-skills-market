from __future__ import annotations

from uuid import UUID

from src.domain.entities.blob import Blob
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.blob_repository import BlobRepository
from src.domain.repositories.shared_skill_repository import SharedSkillRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository


async def handle_get_market_blob(
    shared_skill_id: UUID,
    blob_id: UUID,
    shared_skill_repo: SharedSkillRepository,
    skill_repo: SkillRepository,
    tree_repo: TreeRepository,
    blob_repo: BlobRepository,
) -> Blob:
    shared_skill = await shared_skill_repo.find_by_id(shared_skill_id)
    if shared_skill is None or shared_skill.skill_id is None:
        raise ResourceNotFoundError("Shared skill not found")

    skill = await skill_repo.get_by_id(shared_skill.skill_id)
    if skill is None or skill.tree_id is None:
        raise ResourceNotFoundError("Skill content not available")

    tree = await tree_repo.get_by_id(skill.tree_id)
    if tree is None:
        raise ResourceNotFoundError("File tree not found")

    blob_ids_in_tree = {entry.blob_id for entry in tree.entries if entry.blob_id}
    if blob_id not in blob_ids_in_tree:
        raise ResourceNotFoundError("Blob not found in this skill")

    blob = await blob_repo.get_by_id(blob_id)
    if blob is None:
        raise ResourceNotFoundError("Blob not found")

    return blob
