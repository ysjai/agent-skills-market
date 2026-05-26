from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.handlers.prompt_like_handlers import (
    handle_like_prompt,
    handle_unlike_prompt,
)
from src.domain.exceptions import ResourceConflictError, ResourceNotFoundError


@pytest.mark.asyncio
async def test_like_prompt_success():
    shared_prompt_id = uuid4()
    user = MagicMock()
    user.id = uuid4()

    shared_prompt = MagicMock()
    shared_prompt.id = shared_prompt_id

    repo = AsyncMock()
    repo.find_by_id.return_value = shared_prompt
    repo.find_like.return_value = None
    repo.save_like.side_effect = lambda like: like

    await handle_like_prompt(shared_prompt_id, user, repo)
    repo.save_like.assert_called_once()
    repo.increment_like_count.assert_called_once_with(shared_prompt_id)


@pytest.mark.asyncio
async def test_like_prompt_not_found():
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    user = MagicMock()
    user.id = uuid4()

    with pytest.raises(ResourceNotFoundError):
        await handle_like_prompt(uuid4(), user, repo)


@pytest.mark.asyncio
async def test_like_prompt_already_liked():
    shared_prompt_id = uuid4()
    user = MagicMock()
    user.id = uuid4()

    repo = AsyncMock()
    repo.find_by_id.return_value = MagicMock()
    repo.find_like.return_value = MagicMock()  # already liked

    with pytest.raises(ResourceConflictError):
        await handle_like_prompt(shared_prompt_id, user, repo)


@pytest.mark.asyncio
async def test_unlike_prompt_success():
    shared_prompt_id = uuid4()
    user = MagicMock()
    user.id = uuid4()

    repo = AsyncMock()
    repo.find_by_id.return_value = MagicMock()
    repo.find_like.return_value = MagicMock()

    await handle_unlike_prompt(shared_prompt_id, user, repo)
    repo.delete_like.assert_called_once_with(user.id, shared_prompt_id)
    repo.decrement_like_count.assert_called_once_with(shared_prompt_id)


@pytest.mark.asyncio
async def test_unlike_prompt_not_liked():
    repo = AsyncMock()
    repo.find_by_id.return_value = MagicMock()
    repo.find_like.return_value = None

    user = MagicMock()
    user.id = uuid4()

    with pytest.raises(ResourceNotFoundError):
        await handle_unlike_prompt(uuid4(), user, repo)
