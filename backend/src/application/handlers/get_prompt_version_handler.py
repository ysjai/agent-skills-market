from uuid import UUID

from src.domain.entities.prompt_version import PromptVersion
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.prompt_repository import PromptRepository


async def handle_get_prompt_version(
    prompt_id: UUID,
    version_id: UUID,
    user_id: UUID,
    prompt_repo: PromptRepository,
) -> PromptVersion:
    prompt = await prompt_repo.get_by_id(prompt_id)
    if not prompt or prompt.user_id != user_id:
        raise ResourceNotFoundError()

    version = await prompt_repo.get_version_by_id(version_id)
    if not version or version.prompt_id != prompt_id:
        raise ResourceNotFoundError()

    return version
