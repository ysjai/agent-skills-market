import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from src.application.handlers.prompt_favorite_handlers import (
    handle_favorite_prompt,
    handle_unfavorite_prompt,
    handle_list_prompt_favorites,
    handle_check_favorite_version,
    handle_refresh_favorite,
)
from src.domain.exceptions import ResourceConflictError, ResourceNotFoundError


@pytest.mark.asyncio
async def test_favorite_prompt_success():
    shared_prompt_id = uuid4()
    user = MagicMock()
    user.id = uuid4()

    shared_prompt = MagicMock()
    shared_prompt.id = shared_prompt_id
    shared_prompt.status = "active"
    shared_prompt.prompt_id = uuid4()
    shared_prompt.user_id = uuid4()

    prompt = MagicMock()
    prompt.title = "Test Prompt"
    prompt.content = "# Hello"
    prompt.description = "A test"
    prompt.tags = ["python"]
    prompt.version = 2

    author = MagicMock()
    author.username = "testuser"

    shared_prompt_repo = AsyncMock()
    shared_prompt_repo.find_by_id.return_value = shared_prompt

    favorite_repo = AsyncMock()
    favorite_repo.find_by_user_and_shared_prompt.return_value = None
    favorite_repo.save.side_effect = lambda f: f

    prompt_repo = AsyncMock()
    prompt_repo.get_by_id.return_value = prompt

    user_repo = AsyncMock()
    user_repo.find_by_id.return_value = author

    result = await handle_favorite_prompt(
        shared_prompt_id, user, shared_prompt_repo, favorite_repo, prompt_repo, user_repo
    )
    assert result.snapshot_title == "Test Prompt"
    assert result.snapshot_version == 2
    shared_prompt_repo.increment_favorite_count.assert_called_once_with(shared_prompt_id)


@pytest.mark.asyncio
async def test_favorite_prompt_already_favorited():
    shared_prompt_id = uuid4()
    user = MagicMock()
    user.id = uuid4()

    shared_prompt = MagicMock()
    shared_prompt.status = "active"

    shared_prompt_repo = AsyncMock()
    shared_prompt_repo.find_by_id.return_value = shared_prompt

    favorite_repo = AsyncMock()
    favorite_repo.find_by_user_and_shared_prompt.return_value = MagicMock()

    with pytest.raises(ResourceConflictError):
        await handle_favorite_prompt(
            shared_prompt_id, user, shared_prompt_repo, favorite_repo, AsyncMock(), AsyncMock()
        )


@pytest.mark.asyncio
async def test_unfavorite_prompt_success():
    shared_prompt_id = uuid4()
    user = MagicMock()
    user.id = uuid4()

    shared_prompt_repo = AsyncMock()
    favorite_repo = AsyncMock()
    favorite_repo.find_by_user_and_shared_prompt.return_value = MagicMock()

    await handle_unfavorite_prompt(shared_prompt_id, user, shared_prompt_repo, favorite_repo)
    favorite_repo.delete.assert_called_once_with(user.id, shared_prompt_id)
    shared_prompt_repo.decrement_favorite_count.assert_called_once_with(shared_prompt_id)


@pytest.mark.asyncio
async def test_unfavorite_prompt_not_found():
    shared_prompt_repo = AsyncMock()
    favorite_repo = AsyncMock()
    favorite_repo.find_by_user_and_shared_prompt.return_value = None

    user = MagicMock()
    user.id = uuid4()

    with pytest.raises(ResourceNotFoundError):
        await handle_unfavorite_prompt(uuid4(), user, shared_prompt_repo, favorite_repo)


@pytest.mark.asyncio
async def test_list_prompt_favorites():
    user = MagicMock()
    user.id = uuid4()

    favorites = [MagicMock(), MagicMock()]
    favorite_repo = AsyncMock()
    favorite_repo.find_by_user.return_value = favorites
    favorite_repo.count_by_user.return_value = 2

    result, total = await handle_list_prompt_favorites(user, favorite_repo, skip=0, limit=20)
    assert len(result) == 2
    assert total == 2


@pytest.mark.asyncio
async def test_check_favorite_version_stale():
    favorite = MagicMock()
    favorite.shared_prompt_id = uuid4()
    favorite.snapshot_version = 1
    favorite.is_version_stale.return_value = True

    shared_prompt = MagicMock()
    shared_prompt.prompt_id = uuid4()

    prompt = MagicMock()
    prompt.version = 5

    shared_prompt_repo = AsyncMock()
    shared_prompt_repo.find_by_id.return_value = shared_prompt

    prompt_repo = AsyncMock()
    prompt_repo.get_by_id.return_value = prompt

    result = await handle_check_favorite_version(favorite, prompt_repo, shared_prompt_repo)
    assert result["is_stale"] is True
    assert result["current_version"] == 5


@pytest.mark.asyncio
async def test_refresh_favorite_success():
    favorite = MagicMock()
    favorite.shared_prompt_id = uuid4()

    shared_prompt = MagicMock()
    shared_prompt.prompt_id = uuid4()

    prompt = MagicMock()
    prompt.title = "Updated Title"
    prompt.content = "Updated Content"
    prompt.description = "Updated Desc"
    prompt.tags = ["new"]
    prompt.version = 5

    shared_prompt_repo = AsyncMock()
    shared_prompt_repo.find_by_id.return_value = shared_prompt

    prompt_repo = AsyncMock()
    prompt_repo.get_by_id.return_value = prompt

    favorite_repo = AsyncMock()
    favorite_repo.save.side_effect = lambda f: f

    result = await handle_refresh_favorite(favorite, prompt_repo, shared_prompt_repo, favorite_repo)
    favorite.refresh_snapshot.assert_called_once_with(
        title="Updated Title",
        content="Updated Content",
        description="Updated Desc",
        tags=["new"],
        version=5,
    )
    favorite_repo.save.assert_called_once()
