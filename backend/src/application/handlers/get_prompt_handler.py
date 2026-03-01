from uuid import UUID

from src.domain.aggregates.prompt import Prompt
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.prompt_repository import PromptRepository


async def handle_get_prompt(
    prompt_id: UUID,
    user_id: UUID,
    prompt_repo: PromptRepository,
) -> Prompt:
    prompt = await prompt_repo.get_by_id(prompt_id)
    if not prompt or prompt.user_id != user_id:
        raise ResourceNotFoundError()
    return prompt
