"""Tests for API schemas remaining coverage."""

from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

from src.api.schemas.blob import GetBlobResp
from src.domain.entities.blob import Blob


class TestGetBlobResp:
    """Test GetBlobResp schema coverage (line 36)."""

    def should_create_from_domain_blob(self):
        """Test line 36: from_domain method for GetBlobResp."""
        # Given
        mock_blob = Mock(spec=Blob)
        mock_blob.id = uuid4()
        mock_blob.checksum = "a" * 64
        mock_blob.size = 1024
        mock_blob.compressed = True
        mock_blob.created_at = datetime.now()

        # When
        resp = GetBlobResp.from_domain(mock_blob)

        # Then
        assert resp.id == mock_blob.id
        assert resp.content_hash == mock_blob.checksum
        assert resp.compressed is True
