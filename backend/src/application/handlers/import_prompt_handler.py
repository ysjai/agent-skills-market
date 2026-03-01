from uuid import UUID

import yaml

from src.domain.aggregates.prompt import Prompt
from src.domain.exceptions import ValidationError
from src.domain.factories.prompt_factory import PromptFactory
from src.domain.repositories.prompt_repository import PromptRepository


def _parse_frontmatter(markdown: str) -> tuple[dict[str, object], str]:
    """Parse YAML frontmatter from markdown string.

    Returns (metadata_dict, content_body).
    Raises ValidationError if frontmatter is missing or invalid.
    """
    stripped = markdown.strip()
    if not stripped.startswith("---"):
        raise ValidationError("Missing title in import")

    # Find the closing --- delimiter
    end_index = stripped.find("---", 3)
    if end_index == -1:
        raise ValidationError("Missing title in import")

    yaml_text = stripped[3:end_index]
    content = stripped[end_index + 3 :].strip()

    try:
        metadata = yaml.safe_load(yaml_text)
    except yaml.YAMLError:
        raise ValidationError("Invalid YAML frontmatter")

    if not isinstance(metadata, dict):
        raise ValidationError("Missing title in import")

    return metadata, content


async def handle_import_prompt(
    user_id: UUID,
    markdown_content: str,
    prompt_repo: PromptRepository,
) -> Prompt:
    """Import a Prompt from markdown with YAML frontmatter."""
    metadata, content = _parse_frontmatter(markdown_content)

    title = metadata.get("title")
    if not title:
        raise ValidationError("Missing title in import")

    description = metadata.get("description")
    tags = metadata.get("tags")

    prompt = PromptFactory.create(
        user_id=user_id,
        title=str(title),
        content=content,
        description=str(description) if description is not None else None,
    )

    if tags and isinstance(tags, list):
        prompt.update_tags([str(t) for t in tags])

    await prompt_repo.save(prompt)
    return prompt
