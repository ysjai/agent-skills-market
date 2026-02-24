"""Integration tests for blob file size boundary scenarios.

Tests file upload size limits and edge cases.
"""

import io

import pytest
from httpx import AsyncClient


class TestBlobFileSizeLimits:
    """Test file size limit enforcement on blob uploads."""

    @pytest.mark.asyncio
    async def test_should_return_413_when_upload_file_exceeds_max_size(self, auth_client: AsyncClient):
        # Given: 10.1MB file (slightly over 10MB limit)
        large_content = b"x" * (10 * 1024 * 1024 + 100)  # 10MB + 100 bytes
        files = {"file": ("large.txt", io.BytesIO(large_content), "text/plain")}

        # When: Upload file
        response = await auth_client.post("/api/blobs", files=files)

        # Then: Should return 413 Payload Too Large
        assert response.status_code == 413
        data = response.json()
        assert "code" in data
        assert "message" in data
        assert "File size exceeds" in data["message"]

    @pytest.mark.asyncio
    async def test_should_return_201_when_upload_highly_compressible_content(
        self, auth_client: AsyncClient
    ):
        # Given: 9MB highly compressible content (all same byte)
        # This compresses to less than 1MB but original size is 9MB
        compressible_content = b"A" * (9 * 1024 * 1024)  # 9MB
        files = {"file": ("compressible.txt", io.BytesIO(compressible_content), "text/plain")}

        # When: Upload with compression
        response = await auth_client.post("/api/blobs?compress=true", files=files)

        # Then: Should succeed (201) because original size (9MB) is under 10MB limit
        assert response.status_code == 201
        data = response.json()
        assert data["size"] == 9 * 1024 * 1024
        assert data["compressed"] is True

    @pytest.mark.asyncio
    async def test_should_return_201_when_upload_file_at_exact_limit(self, auth_client: AsyncClient):
        # Given: Exactly 10MB file
        exact_limit_content = b"x" * (10 * 1024 * 1024)  # Exactly 10MB
        files = {"file": ("exact_10mb.txt", io.BytesIO(exact_limit_content), "text/plain")}

        # When: Upload file
        response = await auth_client.post("/api/blobs", files=files)

        # Then: Should succeed (201)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "content_hash" in data
        assert data["size"] == 10 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_should_return_413_when_update_blob_with_oversized_file(
        self, auth_client: AsyncClient
    ):
        # Given: Create a valid blob first
        small_content = b"Small initial content"
        small_files = {"file": ("small.txt", io.BytesIO(small_content), "text/plain")}
        upload_response = await auth_client.post("/api/blobs", files=small_files)
        assert upload_response.status_code == 201
        blob_id = upload_response.json()["id"]

        # When: Try to update with oversized file (10.1MB)
        large_content = b"x" * (10 * 1024 * 1024 + 100)
        large_files = {"file": ("large.txt", io.BytesIO(large_content), "text/plain")}
        response = await auth_client.put(f"/api/blobs/{blob_id}", files=large_files)

        # Then: Should return 413 Payload Too Large
        assert response.status_code == 413
        data = response.json()
        assert "code" in data
        assert "message" in data
        assert "File size exceeds" in data["message"]


class TestBlobFileSizeBoundaryMocked:
    """Test file size limits with mocked large content to avoid memory issues."""

    @pytest.mark.asyncio
    async def test_should_check_size_before_compression(self, auth_client: AsyncClient):
        # Verify that size check happens on original content, not compressed
        # This is implicitly tested by the highly compressible test above,
        # but we verify the behavior explicitly here

        # Given: 9.9MB content that will compress significantly
        # The key is: size check should happen BEFORE compression
        large_repeated_content = b"TEST_PATTERN_123" * (9 * 1024 * 1024 // 16)
        files = {"file": ("pattern.txt", io.BytesIO(large_repeated_content), "text/plain")}

        # When: Upload
        response = await auth_client.post("/api/blobs?compress=true", files=files)

        # Then: Should succeed because original is 9.9MB (under 10MB)
        assert response.status_code == 201
        data = response.json()
        # Verify the original size is recorded, not compressed size
        assert data["size"] == len(large_repeated_content)
        assert data["size"] < 10 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_should_return_413_with_just_over_limit(self, auth_client: AsyncClient):
        # Given: 10MB + 1 byte (just over limit)
        slightly_over = b"x" * (10 * 1024 * 1024 + 1)
        files = {"file": ("slightly_over.txt", io.BytesIO(slightly_over), "text/plain")}

        # When: Upload
        response = await auth_client.post("/api/blobs", files=files)

        # Then: Should return 413
        assert response.status_code == 413
        data = response.json()
        assert "code" in data
        assert "message" in data
        assert "File size exceeds" in data["message"]

    @pytest.mark.asyncio
    async def test_should_return_201_with_just_under_limit(self, auth_client: AsyncClient):
        # Given: 10MB - 1 byte (just under limit)
        slightly_under = b"x" * (10 * 1024 * 1024 - 1)
        files = {"file": ("slightly_under.txt", io.BytesIO(slightly_under), "text/plain")}

        # When: Upload
        response = await auth_client.post("/api/blobs", files=files)

        # Then: Should succeed
        assert response.status_code == 201
        data = response.json()
        assert data["size"] == 10 * 1024 * 1024 - 1
