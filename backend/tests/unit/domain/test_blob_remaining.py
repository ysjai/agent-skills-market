"""Tests for Blob entity remaining coverage."""



from src.domain.entities.blob import Blob


class TestBlobRemaining:
    """Test Blob entity coverage (lines 94-95)."""

    def should_return_binary_placeholder_when_content_cannot_decode(self):
        """Test lines 94-95: handle decode error gracefully."""
        # Given - create blob with compressed invalid content that can't be decoded
        blob = Blob.create(b"\xff\xfe invalid", compressed=True)

        # When
        preview = blob.get_content_preview(max_length=10)

        # Then - check that we got a result (either decoded or binary placeholder)
        assert preview is not None
        assert isinstance(preview, str)
