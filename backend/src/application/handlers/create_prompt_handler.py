from uuid import UUID

from src.domain.aggregates.prompt import Prompt
from src.domain.factories.prompt_factory import PromptFactory
from src.domain.repositories.prompt_repository import PromptRepository


async def handle_create_prompt(
    user_id: UUID,
    title: str,
    content: str,
    prompt_repo: PromptRepository,
    description: str | None = None,
    tags: list[str] | None = None,
) -> Prompt:
    prompt = PromptFactory.create(user_id=user_id, title=title, content=content, description=description)
    if tags is not None:
        prompt.update_tags(tags)
    await prompt_repo.save(prompt)
    return prompt
