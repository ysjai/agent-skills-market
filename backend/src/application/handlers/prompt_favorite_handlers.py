from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.aggregates.prompt_favorite import PromptFavorite
from src.domain.aggregates.user import User
from src.domain.exceptions import ResourceConflictError, ResourceNotFoundError
from src.domain.factories.prompt_favorite_factory import PromptFavoriteFactory
from src.domain.repositories.shared_prompt_repository import SharedPromptRepository


class PromptFavoriteRepo(Protocol):
    async def save(self, favorite: PromptFavorite) -> PromptFavorite: ...
    async def delete(self, user_id: UUID, shared_prompt_id: UUID) -> None: ...
    async def find_by_user_and_shared_prompt(
        self, user_id: UUID, shared_prompt_id: UUID
    ) -> PromptFavorite | None: ...
    async def find_by_user(self, user_id: UUID, skip: int, limit: int) -> list[PromptFavorite]: ...
    async def count_by_user(self, user_id: UUID) -> int: ...


async def handle_favorite_prompt(
    shared_prompt_id: UUID,
    user: User,
    shared_prompt_repo: SharedPromptRepository,
    favorite_repo: PromptFavoriteRepo,
    prompt_repo,
    user_repo,
) -> PromptFavorite:
    shared_prompt = await shared_prompt_repo.find_by_id(shared_prompt_id)
    if shared_prompt is None or shared_prompt.status != "active":
        raise ResourceNotFoundError("Shared prompt not found or not active")

    existing = await favorite_repo.find_by_user_and_shared_prompt(user.id, shared_prompt_id)
    if existing is not None:
        raise ResourceConflictError("Prompt already favorited")

    prompt = None
    author = None
    if shared_prompt.prompt_id is not None:
        prompt = await prompt_repo.get_by_id(shared_prompt.prompt_id)
        author = await user_repo.get_by_id(shared_prompt.user_id)

    if prompt is None or author is None:
        raise ResourceNotFoundError("Original prompt or author not found")

    favorite = PromptFavoriteFactory.create(
        user_id=user.id,
        shared_prompt_id=shared_prompt_id,
        prompt=prompt,
        author=author,
    )
    saved = await favorite_repo.save(favorite)
    await shared_prompt_repo.increment_favorite_count(shared_prompt_id)
    return saved


async def handle_unfavorite_prompt(
    shared_prompt_id: UUID,
    user: User,
    shared_prompt_repo: SharedPromptRepository,
    favorite_repo: PromptFavoriteRepo,
) -> None:
    favorite = await favorite_repo.find_by_user_and_shared_prompt(user.id, shared_prompt_id)
    if favorite is None:
        raise ResourceNotFoundError("Favorite not found")

    await favorite_repo.delete(user.id, shared_prompt_id)
    await shared_prompt_repo.decrement_favorite_count(shared_prompt_id)


async def handle_list_prompt_favorites(
    user: User,
    favorite_repo: PromptFavoriteRepo,
    skip: int,
    limit: int,
) -> tuple[list[PromptFavorite], int]:
    favorites = await favorite_repo.find_by_user(user.id, skip, limit)
    total = await favorite_repo.count_by_user(user.id)
    return favorites, total


async def handle_check_favorite_version(
    favorite: PromptFavorite,
    prompt_repo,
    shared_prompt_repo: SharedPromptRepository,
) -> dict:
    """Check if a prompt favorite's snapshot is stale."""
    if favorite.shared_prompt_id is None:
        return {"is_stale": False, "current_version": favorite.snapshot_version}

    shared_prompt = await shared_prompt_repo.find_by_id(favorite.shared_prompt_id)
    if shared_prompt is None or shared_prompt.prompt_id is None:
        return {"is_stale": False, "current_version": favorite.snapshot_version}

    prompt = await prompt_repo.get_by_id(shared_prompt.prompt_id)
    if prompt is None:
        return {"is_stale": False, "current_version": favorite.snapshot_version}

    return {
        "is_stale": favorite.is_version_stale(prompt.version),
        "current_version": prompt.version,
    }


async def handle_refresh_favorite(
    favorite: PromptFavorite,
    prompt_repo,
    shared_prompt_repo: SharedPromptRepository,
    favorite_repo: PromptFavoriteRepo,
) -> PromptFavorite:
    """Refresh a prompt favorite's snapshot with latest data."""
    if favorite.shared_prompt_id is None:
        raise ResourceNotFoundError("Cannot refresh: prompt was withdrawn or deleted")

    shared_prompt = await shared_prompt_repo.find_by_id(favorite.shared_prompt_id)
    if shared_prompt is None or shared_prompt.prompt_id is None:
        raise ResourceNotFoundError("Shared prompt no longer available")

    prompt = await prompt_repo.get_by_id(shared_prompt.prompt_id)
    if prompt is None:
        raise ResourceNotFoundError("Original prompt not found")

    favorite.refresh_snapshot(
        title=prompt.title,
        content=prompt.content,
        description=prompt.description,
        tags=list(prompt.tags),
        version=prompt.version,
    )
    return await favorite_repo.save(favorite)
