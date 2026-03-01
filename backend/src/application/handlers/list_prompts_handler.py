from uuid import UUID

from src.domain.aggregates.prompt import Prompt
from src.domain.repositories.prompt_repository import PromptRepository


async def handle_list_prompts(
    user_id: UUID,
    offset: int,
    limit: int,
    prompt_repo: PromptRepository,
    tag: str | None = None,
    search: str | None = None,
) -> tuple[list[Prompt], int]:
    prompts = await prompt_repo.find_by_user(user_id, offset=offset, limit=limit, tag=tag, search=search)
    total = await prompt_repo.count_by_user(user_id, tag=tag, search=search)
    return prompts, total
