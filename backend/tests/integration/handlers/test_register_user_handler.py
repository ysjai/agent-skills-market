"""Tests for register_user_handler."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.application.handlers.register_user_handler import handle_register_user
from src.domain.aggregates.user import User
from src.domain.exceptions import ResourceConflictError
from src.domain.repositories.user_repository import UserRepository


class TestRegisterUserHandler:
    """Test register_user_handler coverage (line 21)."""

    @pytest.mark.asyncio
    async def test_should_raise_conflict_when_email_exists(self):
        """Test line 21: raise error when email already registered."""
        # Given
        user_repo = AsyncMock(spec=UserRepository)
        user_repo.exists_by_email.return_value = True

        # When/Then
        with pytest.raises(ResourceConflictError) as exc_info:
            await handle_register_user(
                email="existing@example.com",
                username="testuser",
                password="password123",
                user_repo=user_repo
            )

        assert "already registered" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_should_register_new_user_successfully(self):
        """Test successful user registration."""
        # Given
        user_repo = AsyncMock(spec=UserRepository)
        user_repo.exists_by_email.return_value = False

        mock_user = Mock(spec=User)
        mock_user.id = "test-id"

        with patch('app.application.handlers.register_user_handler.UserFactory') as MockFactory:
            with patch('app.application.handlers.register_user_handler.create_access_token') as mock_access:
                with patch('app.application.handlers.register_user_handler.create_refresh_token') as mock_refresh:
                    MockFactory.create.return_value = mock_user
                    mock_access.return_value = "access-token"
                    mock_refresh.return_value = "refresh-token"

                    # When
                    user, access, refresh = await handle_register_user(
                        email="new@example.com",
                        username="newuser",
                        password="password123",
                        user_repo=user_repo
                    )

                    # Then
                    assert user == mock_user
                    assert access == "access-token"
                    assert refresh == "refresh-token"
