from uuid import UUID

import yaml

from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.prompt_repository import PromptRepository


async def handle_export_prompt(
    prompt_id: UUID,
    user_id: UUID,
    prompt_repo: PromptRepository,
) -> str:
    """Export a Prompt as markdown with YAML frontmatter."""
    prompt = await prompt_repo.get_by_id(prompt_id)
    if prompt is None or prompt.user_id != user_id:
        raise ResourceNotFoundError()

    frontmatter: dict[str, object] = {"title": prompt.title}

    if prompt.description:
        frontmatter["description"] = prompt.description

    if prompt.tags:
        frontmatter["tags"] = prompt.tags

    frontmatter["version"] = prompt.version

    yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)

    return f"---\n{yaml_str}---\n\n{prompt.content}"
