from __future__ import annotations

from uuid import UUID

from src.domain.aggregates.shared_prompt import SharedPrompt
from src.domain.aggregates.user import User
from src.domain.exceptions import ForbiddenError, ResourceConflictError, ResourceNotFoundError
from src.domain.factories.shared_prompt_factory import SharedPromptFactory
from src.domain.repositories.shared_prompt_repository import SharedPromptRepository


async def handle_share_prompt(
    prompt_id: UUID,
    user: User,
    prompt_repo,
    shared_prompt_repo: SharedPromptRepository,
    share_message: str | None = None,
) -> SharedPrompt:
    prompt = await prompt_repo.get_by_id(prompt_id)
    if not prompt:
        raise ResourceNotFoundError("Prompt not found")
    if prompt.user_id != user.id:
        raise ForbiddenError("You can only share your own prompts")

    existing = await shared_prompt_repo.find_by_user_and_prompt(user.id, prompt_id)
    if existing and existing.status == "active":
        raise ResourceConflictError("Prompt already shared")

    shared_prompt = SharedPromptFactory.create(
        prompt_id=prompt.id,
        user_id=user.id,
        share_message=share_message,
    )
    return await shared_prompt_repo.save(shared_prompt)


async def handle_unshare_prompt(
    prompt_id: UUID,
    user: User,
    prompt_repo,
    shared_prompt_repo: SharedPromptRepository,
    favorite_repo=None,
) -> SharedPrompt:
    prompt = await prompt_repo.get_by_id(prompt_id)
    if not prompt:
        raise ResourceNotFoundError("Prompt not found")
    if prompt.user_id != user.id:
        raise ForbiddenError("You can only unshare your own prompts")

    shared_prompt = await shared_prompt_repo.find_by_prompt_id(prompt_id)
    if not shared_prompt or shared_prompt.status != "active":
        raise ResourceNotFoundError("No active share found")

    shared_prompt.withdraw()
    await shared_prompt_repo.save(shared_prompt)

    if favorite_repo:
        await favorite_repo.update_batch_status(shared_prompt.id, "prompt_withdrawn")

    return shared_prompt
