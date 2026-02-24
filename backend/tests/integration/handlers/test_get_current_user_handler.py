"""Tests for get_current_user_handler to cover remaining lines."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.application.handlers.get_current_user_handler import handle_get_current_user
from src.domain.aggregates.user import User
from src.domain.repositories.user_repository import UserRepository


class TestGetCurrentUserHandler:
    """Test get_current_user_handler coverage gaps (lines 12-14)."""

    @pytest.mark.asyncio
    async def test_should_return_user_when_found(self):
        """Test lines 12-15: user found and returned."""
        # Given
        user_repo = AsyncMock(spec=UserRepository)
        user_id = uuid4()
        expected_user = Mock(spec=User)
        user_repo.get_by_id.return_value = expected_user

        # When
        result = await handle_get_current_user(user_id, user_repo)

        # Then
        assert result == expected_user
        user_repo.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_user_missing(self):
        """Test line 14: user not found raises error."""
        # Given
        user_repo = AsyncMock(spec=UserRepository)
        user_id = uuid4()
        user_repo.get_by_id.return_value = None

        # When/Then
        with pytest.raises(Exception) as exc_info:
            await handle_get_current_user(user_id, user_repo)

        assert "not found" in str(exc_info.value).lower()
