"""Tests for database session management."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.persistence.db.session import MAX_OVERFLOW, POOL_SIZE, get_db


class TestDatabaseSession:
    """Test database session management."""

    @pytest.mark.asyncio
    async def test_get_db_successful_commit(self):
        """Test session commits on successful completion (L38-39)."""
        mock_session = AsyncMock(spec=AsyncSession)

        async_mock_context = AsyncMock()
        async_mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        async_mock_context.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "src.infra.persistence.db.session.AsyncSessionLocal", return_value=async_mock_context
        ):
            async for session in get_db():
                assert session == mock_session

            # Verify commit was called
            mock_session.commit.assert_called_once()
            mock_session.rollback.assert_not_called()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_db_exception_rollback(self):
        """Test session rolls back on exception (L40-42)."""
        mock_session = AsyncMock(spec=AsyncSession)
        test_exception = ValueError("Test exception")

        async_mock_context = AsyncMock()
        async_mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        async_mock_context.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "src.infra.persistence.db.session.AsyncSessionLocal", return_value=async_mock_context
        ):
            generator = get_db()
            session = await anext(generator)
            assert session == mock_session

            with pytest.raises(ValueError, match="Test exception"):
                await generator.athrow(test_exception)

            # Verify rollback was called
            mock_session.rollback.assert_called_once()
            mock_session.commit.assert_not_called()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_db_session_closed_in_finally(self):
        """Test session is closed in finally block (L43-44)."""
        mock_session = AsyncMock(spec=AsyncSession)

        async_mock_context = AsyncMock()
        async_mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        async_mock_context.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "src.infra.persistence.db.session.AsyncSessionLocal", return_value=async_mock_context
        ):
            async for session in get_db():
                pass

            # Verify close was called
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_db_exception_re_raised(self):
        """Test exception is re-raised after rollback (L42)."""
        mock_session = AsyncMock(spec=AsyncSession)
        test_exception = ValueError("Test rollback")

        async_mock_context = AsyncMock()
        async_mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        async_mock_context.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "src.infra.persistence.db.session.AsyncSessionLocal", return_value=async_mock_context
        ):
            generator = get_db()
            session = await anext(generator)
            assert session == mock_session

            with pytest.raises(ValueError, match="Test rollback"):
                await generator.athrow(test_exception)

    @pytest.mark.asyncio
    async def test_get_db_multiple_yields_not_allowed(self):
        """Test generator yields session only once."""
        mock_session = AsyncMock(spec=AsyncSession)

        async_mock_context = AsyncMock()
        async_mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        async_mock_context.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "src.infra.persistence.db.session.AsyncSessionLocal", return_value=async_mock_context
        ):
            count = 0
            async for session in get_db():
                count += 1
                if count > 1:
                    break

            # Generator should yield only once
            assert count == 1


class TestEngineConfiguration:
    """Test database engine configuration."""

    def test_engine_pool_constants(self):
        """Test engine pool constants are configured correctly (L18-24)."""
        assert POOL_SIZE == 10
        assert MAX_OVERFLOW == 20

    def test_async_session_local_is_callable(self):
        """Test AsyncSessionLocal is properly configured (L26-32)."""
        from src.infra.persistence.db.session import AsyncSessionLocal

        # Verify it's a session maker that returns AsyncSession
        assert AsyncSessionLocal is not None
        assert callable(AsyncSessionLocal)
