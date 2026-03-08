from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.prompt_repository import PromptRepository
from src.domain.repositories.shared_prompt_repository import SharedPromptRepository


class PromptFavoriteRepository(Protocol):
    async def update_batch_status(self, shared_prompt_id: UUID, status: str) -> None: ...


async def handle_delete_prompt(
    prompt_id: UUID,
    user_id: UUID,
    prompt_repo: PromptRepository,
    shared_prompt_repo: SharedPromptRepository | None = None,
    favorite_repo: PromptFavoriteRepository | None = None,
) -> None:
    prompt = await prompt_repo.get_by_id(prompt_id)
    if not prompt or prompt.user_id != user_id:
        raise ResourceNotFoundError()

    # Cascade: mark associated SharedPrompts as withdrawn and update favorites
    if shared_prompt_repo and favorite_repo:
        shared_prompts = await shared_prompt_repo.find_all_by_prompt_id(prompt.id)
        for sp in shared_prompts:
            sp.mark_prompt_deleted()
            await shared_prompt_repo.save(sp)
            await favorite_repo.update_batch_status(sp.id, "prompt_deleted")

    await prompt_repo.delete(prompt_id)
