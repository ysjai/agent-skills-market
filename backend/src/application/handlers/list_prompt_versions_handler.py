from uuid import UUID

from src.domain.entities.prompt_version import PromptVersion
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.prompt_repository import PromptRepository


async def handle_list_prompt_versions(
    prompt_id: UUID,
    user_id: UUID,
    prompt_repo: PromptRepository,
) -> list[PromptVersion]:
    prompt = await prompt_repo.get_by_id(prompt_id)
    if not prompt or prompt.user_id != user_id:
        raise ResourceNotFoundError()

    return await prompt_repo.get_versions(prompt_id)
