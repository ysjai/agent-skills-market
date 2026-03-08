from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.aggregates.shared_prompt import SharedPrompt
from src.domain.aggregates.user import User
from src.domain.entities.prompt_like import PromptLike
from src.domain.exceptions import ResourceConflictError, ResourceNotFoundError
from src.domain.repositories.shared_prompt_repository import SharedPromptRepository


async def handle_like_prompt(
    shared_prompt_id: UUID,
    user: User,
    shared_prompt_repo: SharedPromptRepository,
) -> SharedPrompt:
    shared_prompt = await shared_prompt_repo.find_by_id(shared_prompt_id)
    if shared_prompt is None:
        raise ResourceNotFoundError("Shared prompt not found")

    existing_like = await shared_prompt_repo.find_like(user.id, shared_prompt_id)
    if existing_like is not None:
        raise ResourceConflictError("Shared prompt already liked")

    like = PromptLike(
        id=uuid4(),
        user_id=user.id,
        shared_prompt_id=shared_prompt_id,
        created_at=datetime.now(timezone.utc),
    )
    _ = await shared_prompt_repo.save_like(like)
    await shared_prompt_repo.increment_like_count(shared_prompt_id)

    updated = await shared_prompt_repo.find_by_id(shared_prompt_id)
    if updated is None:
        raise ResourceNotFoundError("Shared prompt not found")
    return updated


async def handle_unlike_prompt(
    shared_prompt_id: UUID,
    user: User,
    shared_prompt_repo: SharedPromptRepository,
) -> SharedPrompt:
    shared_prompt = await shared_prompt_repo.find_by_id(shared_prompt_id)
    if shared_prompt is None:
        raise ResourceNotFoundError("Shared prompt not found")

    existing_like = await shared_prompt_repo.find_like(user.id, shared_prompt_id)
    if existing_like is None:
        raise ResourceNotFoundError("Like not found")

    await shared_prompt_repo.delete_like(user.id, shared_prompt_id)
    await shared_prompt_repo.decrement_like_count(shared_prompt_id)

    updated = await shared_prompt_repo.find_by_id(shared_prompt_id)
    if updated is None:
        raise ResourceNotFoundError("Shared prompt not found")
    return updated
