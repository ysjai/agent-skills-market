from __future__ import annotations

import io
import zipfile
from uuid import UUID

from src.domain.aggregates.tree import Tree
from src.domain.exceptions import ForbiddenError, ResourceNotFoundError
from src.domain.repositories.blob_repository import BlobRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository


async def handle_download_skill(
    user_id: UUID,
    skill_id: UUID,
    platform: str | None,
    skill_repo: SkillRepository,
    tree_repo: TreeRepository,
    blob_repo: BlobRepository,
) -> tuple[bytes, str, str]:
    """
    Download a skill.

    Returns: (content_bytes, media_type, filename)
    """
    skill = await skill_repo.get_by_id(skill_id)
    if skill is None:
        raise ResourceNotFoundError("Skill not found")

    if skill.user_id != user_id:
        raise ForbiddenError("Not authorized to access this skill")

    if not skill.tree_id:
        if platform == "claude":
            return b"", "text/markdown", f"{skill.slug}.md"
        else:
            return b"", "application/zip", f"{skill.slug}.zip"

    tree = await tree_repo.get_by_id(skill.tree_id)
    if tree is None:
        raise ResourceNotFoundError("Tree not found")

    if platform == "claude":
        content = await _generate_markdown(tree, blob_repo)
        return content.encode("utf-8"), "text/markdown", f"{skill.slug}.md"
    else:
        zip_content: bytes = await _generate_zip(tree, blob_repo)
        return zip_content, "application/zip", f"{skill.slug}.zip"


async def _generate_markdown(tree: Tree, blob_repo: BlobRepository) -> str:
    """Generate markdown content from tree entries."""
    lines = []

    for entry in tree.entries:
        if entry.is_file() and entry.blob_id:
            blob = await blob_repo.get_by_id(entry.blob_id)
            if blob:
                content = blob.get_raw_content().decode("utf-8", errors="replace")
                lines.append(f"## File: {str(entry.path)}")
                lines.append("")
                lines.append("```")
                lines.append(content)
                lines.append("```")
                lines.append("")

    return "\n".join(lines)


async def _generate_zip(tree: Tree, blob_repo: BlobRepository) -> bytes:
    """Generate zip content from tree entries."""
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for entry in tree.entries:
            if entry.is_file() and entry.blob_id:
                blob = await blob_repo.get_by_id(entry.blob_id)
                if blob:
                    content = blob.get_raw_content()
                    zf.writestr(str(entry.path), content)

    buffer.seek(0)
    return buffer.getvalue()
