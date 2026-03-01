from uuid import UUID

from src.domain.aggregates.prompt import Prompt
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.prompt_repository import PromptRepository


async def handle_update_prompt(
    prompt_id: UUID,
    user_id: UUID,
    prompt_repo: PromptRepository,
    title: str | None = None,
    content: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
) -> Prompt:
    prompt = await prompt_repo.get_by_id(prompt_id)
    if not prompt or prompt.user_id != user_id:
        raise ResourceNotFoundError()
    if title is not None:
        prompt.update_title(title)
    if content is not None:
        prompt.update_content(content)
    if description is not None:
        prompt.update_description(description)
    if tags is not None:
        prompt.update_tags(tags)
    await prompt_repo.save(prompt)
    return prompt
