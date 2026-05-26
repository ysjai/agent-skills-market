from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.handlers.shared_prompt_handlers import (
    handle_share_prompt,
    handle_unshare_prompt,
)
from src.domain.exceptions import (
    ForbiddenError,
    ResourceConflictError,
    ResourceNotFoundError,
)


@pytest.mark.asyncio
async def test_share_prompt_success():
    prompt_id = uuid4()
    user_id = uuid4()

    prompt = MagicMock()
    prompt.id = prompt_id
    prompt.user_id = user_id

    user = MagicMock()
    user.id = user_id

    prompt_repo = AsyncMock()
    prompt_repo.get_by_id.return_value = prompt

    shared_prompt_repo = AsyncMock()
    shared_prompt_repo.find_by_user_and_prompt.return_value = None
    shared_prompt_repo.save.side_effect = lambda sp: sp

    result = await handle_share_prompt(
        prompt_id=prompt_id,
        user=user,
        prompt_repo=prompt_repo,
        shared_prompt_repo=shared_prompt_repo,
        share_message="Check this out!",
    )
    assert result.prompt_id == prompt_id
    assert result.user_id == user_id
    assert result.status == "active"
    assert result.share_message == "Check this out!"


@pytest.mark.asyncio
async def test_share_prompt_not_owner():
    prompt = MagicMock()
    prompt.id = uuid4()
    prompt.user_id = uuid4()

    user = MagicMock()
    user.id = uuid4()  # different user

    prompt_repo = AsyncMock()
    prompt_repo.get_by_id.return_value = prompt

    shared_prompt_repo = AsyncMock()

    with pytest.raises(ForbiddenError):
        await handle_share_prompt(
            prompt_id=prompt.id,
            user=user,
            prompt_repo=prompt_repo,
            shared_prompt_repo=shared_prompt_repo,
        )


@pytest.mark.asyncio
async def test_share_prompt_already_shared():
    prompt_id = uuid4()
    user_id = uuid4()

    prompt = MagicMock()
    prompt.id = prompt_id
    prompt.user_id = user_id

    user = MagicMock()
    user.id = user_id

    existing = MagicMock()
    existing.status = "active"

    prompt_repo = AsyncMock()
    prompt_repo.get_by_id.return_value = prompt

    shared_prompt_repo = AsyncMock()
    shared_prompt_repo.find_by_user_and_prompt.return_value = existing

    with pytest.raises(ResourceConflictError):
        await handle_share_prompt(
            prompt_id=prompt_id,
            user=user,
            prompt_repo=prompt_repo,
            shared_prompt_repo=shared_prompt_repo,
        )


@pytest.mark.asyncio
async def test_share_prompt_not_found():
    prompt_repo = AsyncMock()
    prompt_repo.get_by_id.return_value = None

    shared_prompt_repo = AsyncMock()
    user = MagicMock()
    user.id = uuid4()

    with pytest.raises(ResourceNotFoundError):
        await handle_share_prompt(
            prompt_id=uuid4(),
            user=user,
            prompt_repo=prompt_repo,
            shared_prompt_repo=shared_prompt_repo,
        )


@pytest.mark.asyncio
async def test_unshare_prompt_success():
    prompt_id = uuid4()
    user_id = uuid4()

    prompt = MagicMock()
    prompt.id = prompt_id
    prompt.user_id = user_id

    user = MagicMock()
    user.id = user_id

    shared_prompt = MagicMock()
    shared_prompt.id = uuid4()
    shared_prompt.user_id = user_id
    shared_prompt.prompt_id = prompt_id
    shared_prompt.status = "active"

    prompt_repo = AsyncMock()
    prompt_repo.get_by_id.return_value = prompt

    shared_prompt_repo = AsyncMock()
    shared_prompt_repo.find_by_prompt_id.return_value = shared_prompt
    shared_prompt_repo.save.side_effect = lambda sp: sp

    favorite_repo = AsyncMock()

    await handle_unshare_prompt(
        prompt_id=prompt_id,
        user=user,
        prompt_repo=prompt_repo,
        shared_prompt_repo=shared_prompt_repo,
        favorite_repo=favorite_repo,
    )
    shared_prompt.withdraw.assert_called_once()
    favorite_repo.update_batch_status.assert_called_once()


@pytest.mark.asyncio
async def test_unshare_prompt_not_owner():
    prompt = MagicMock()
    prompt.id = uuid4()
    prompt.user_id = uuid4()

    user = MagicMock()
    user.id = uuid4()

    prompt_repo = AsyncMock()
    prompt_repo.get_by_id.return_value = prompt

    shared_prompt_repo = AsyncMock()

    with pytest.raises(ForbiddenError):
        await handle_unshare_prompt(
            prompt_id=prompt.id,
            user=user,
            prompt_repo=prompt_repo,
            shared_prompt_repo=shared_prompt_repo,
        )
