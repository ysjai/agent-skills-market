"""Tests for User CRUD operations."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import UserCRUD, user
from app.infra.persistence.models.user_model import UserModel


class TestUserCRUD:
    """Test User CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self):
        """Test getting user by ID successfully (L19-34)."""
        # Create mock user model
        user_id = str(uuid.uuid4())
        mock_user_model = MagicMock(spec=UserModel)
        mock_user_model.to_domain.return_value = MagicMock()

        # Create mock result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user_model

        # Create mock session
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.return_value = mock_result

        # Call the method
        crud = UserCRUD()
        result = await crud.get(mock_session, id=user_id)

        # Verify the result
        assert result is not None
        mock_user_model.to_domain.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Test getting user by ID returns None when not found (L34)."""
        user_id = str(uuid.uuid4())

        # Create mock result that returns None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        # Create mock session
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.return_value = mock_result

        # Call the method
        crud = UserCRUD()
        result = await crud.get(mock_session, id=user_id)

        # Verify None is returned
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_executes_correct_query(self):
        """Test get method executes correct SQL query (L31)."""
        user_id = str(uuid.uuid4())

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.return_value = mock_result

        crud = UserCRUD()
        await crud.get(mock_session, id=user_id)

        # Verify execute was called
        mock_session.execute.assert_called_once()

        # Get the passed statement
        call_args = mock_session.execute.call_args
        stmt = call_args[0][0]

        # Verify it's a select statement
        assert "SELECT" in str(stmt).upper()


class TestUserCRUDSingleton:
    """Test UserCRUD singleton instance."""

    def test_user_singleton_exists(self):
        """Test user singleton instance exists (L38)."""
        assert user is not None
        assert isinstance(user, UserCRUD)

    def test_user_singleton_is_same_instance(self):
        """Test user singleton is same instance on multiple imports."""
        from app.crud.user import user as user2

        assert user is user2
