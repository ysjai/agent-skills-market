"""Tests for get_blob_handler to cover remaining lines."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.application.handlers.get_blob_handler import handle_get_blob
from src.domain.entities.blob import Blob
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.blob_repository import BlobRepository


class TestGetBlobHandler:
    """Test get_blob_handler coverage gaps (lines 14-16)."""

    @pytest.mark.asyncio
    async def test_should_return_blob_when_found(self):
        """Test line 14: blob found and returned."""
        # Given
        blob_repo = AsyncMock(spec=BlobRepository)
        blob_id = uuid4()
        expected_blob = Mock(spec=Blob)
        blob_repo.get_by_id.return_value = expected_blob

        # When
        result = await handle_get_blob(blob_id, blob_repo)

        # Then
        assert result == expected_blob
        blob_repo.get_by_id.assert_called_once_with(blob_id)

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_blob_missing(self):
        """Test lines 15-16: blob not found raises error."""
        # Given
        blob_repo = AsyncMock(spec=BlobRepository)
        blob_id = uuid4()
        blob_repo.get_by_id.return_value = None

        # When/Then
        with pytest.raises(ResourceNotFoundError):
            await handle_get_blob(blob_id, blob_repo)
