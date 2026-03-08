"""Tests for create_blob_handler to cover remaining lines (24-27)."""

from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from src.application.handlers.create_blob_handler import handle_create_blob
from src.domain.entities.blob import Blob
from src.domain.repositories.blob_repository import BlobRepository


class TestCreateBlobHandler:
    """Test create_blob_handler exception handling."""

    @pytest.mark.asyncio
    async def test_should_return_existing_blob_when_checksum_matches(self):
        """Test line 24-25: return existing blob when checksum found."""
        # Given
        blob_repo = AsyncMock(spec=BlobRepository)
        content = b"test content"

        existing_blob = Mock(spec=Blob)
        existing_blob.id = uuid4()
        blob_repo.get_by_checksum.return_value = existing_blob

        # When
        result = await handle_create_blob(content, blob_repo)

        # Then
        assert result == existing_blob

    @pytest.mark.asyncio
    async def test_should_save_and_return_new_blob_when_no_checksum_match(self):
        """Test lines 26-27: save and return new blob."""
        # Given
        blob_repo = AsyncMock(spec=BlobRepository)
        blob_repo.get_by_checksum.return_value = None
        content = b"test content"

        expected_blob = Mock(spec=Blob)
        expected_blob.id = uuid4()

        with patch("src.application.handlers.create_blob_handler.BlobFactory") as MockFactory:
            MockFactory.create_from_content.return_value = expected_blob

            # When
            result = await handle_create_blob(content, blob_repo)

            # Then
            assert result == expected_blob
            blob_repo.save.assert_called_once_with(expected_blob)
