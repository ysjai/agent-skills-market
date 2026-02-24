import hashlib
import io

import pytest
from httpx import AsyncClient


class TestUploadBlob:
    @pytest.mark.asyncio
    async def test_should_return_201_when_upload_blob_given_text_content(self, auth_client: AsyncClient):
        files = {"file": ("test.txt", io.BytesIO(b"Hello, World!"), "text/plain")}
        response = await auth_client.post("/api/blobs", files=files)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "content_hash" in data
        assert "size" in data
        assert "compressed" in data
        assert "created_at" in data
        assert data["size"] == 13

    @pytest.mark.asyncio
    async def test_should_return_201_when_upload_blob_given_binary_content(
        self, auth_client: AsyncClient
    ):
        binary_content = bytes(range(256))
        files = {"file": ("test.bin", io.BytesIO(binary_content), "application/octet-stream")}
        response = await auth_client.post("/api/blobs", files=files)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["size"] == 256

    @pytest.mark.asyncio
    async def test_should_return_compressed_blob_when_upload_with_compress_flag(
        self, auth_client: AsyncClient
    ):
        compressible_content = b"A" * 1000
        files = {"file": ("test.txt", io.BytesIO(compressible_content), "text/plain")}
        response = await auth_client.post("/api/blobs?compress=true", files=files)
        assert response.status_code == 201
        data = response.json()
        assert data["compressed"] is True

    @pytest.mark.asyncio
    async def test_should_return_uncompressed_blob_when_upload_with_compress_false(
        self, auth_client: AsyncClient
    ):
        files = {"file": ("test.txt", io.BytesIO(b"Hello"), "text/plain")}
        response = await auth_client.post("/api/blobs?compress=false", files=files)
        assert response.status_code == 201
        data = response.json()
        assert data["compressed"] is False

    @pytest.mark.asyncio
    async def test_should_return_same_id_when_upload_duplicate_content(self, auth_client: AsyncClient):
        files = {"file": ("test.txt", io.BytesIO(b"Duplicate content"), "text/plain")}
        response1 = await auth_client.post("/api/blobs", files=files)
        assert response1.status_code == 201
        data1 = response1.json()
        blob_id1 = data1["id"]

        response2 = await auth_client.post("/api/blobs", files=files)
        assert response2.status_code == 201
        data2 = response2.json()
        blob_id2 = data2["id"]

        assert blob_id1 == blob_id2

    @pytest.mark.asyncio
    async def test_should_return_401_when_upload_blob_given_no_auth(self, client: AsyncClient):
        files = {"file": ("test.txt", io.BytesIO(b"Hello"), "text/plain")}
        response = await client.post("/api/blobs", files=files)
        assert response.status_code == 401


class TestDownloadBlob:
    @pytest.mark.asyncio
    async def test_should_return_content_when_download_blob_given_valid_id(
        self, auth_client: AsyncClient
    ):
        upload_files = {"file": ("test.txt", io.BytesIO(b"Download test content"), "text/plain")}
        upload_response = await auth_client.post("/api/blobs", files=upload_files)
        assert upload_response.status_code == 201
        blob_id = upload_response.json()["id"]

        download_response = await auth_client.get(f"/api/blobs/{blob_id}")
        assert download_response.status_code == 200
        assert download_response.content == b"Download test content"

    @pytest.mark.asyncio
    async def test_should_return_decompressed_content_when_download_compressed_blob(
        self, auth_client: AsyncClient
    ):
        upload_files = {"file": ("test.txt", io.BytesIO(b"A" * 1000), "text/plain")}
        upload_response = await auth_client.post("/api/blobs?compress=true", files=upload_files)
        assert upload_response.status_code == 201
        blob_id = upload_response.json()["id"]

        download_response = await auth_client.get(f"/api/blobs/{blob_id}")
        assert download_response.status_code == 200
        assert download_response.content == b"A" * 1000

    @pytest.mark.asyncio
    async def test_should_return_404_when_download_blob_given_nonexistent_id(
        self, auth_client: AsyncClient
    ):
        response = await auth_client.get("/api/blobs/00000000-0000-0000-0000-000000000001")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_401_when_download_blob_given_no_auth(self, client: AsyncClient):
        response = await client.get("/api/blobs/00000000-0000-0000-0000-000000000001")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_should_return_404_when_download_blob_given_invalid_id_format(
        self, auth_client: AsyncClient
    ):
        response = await auth_client.get("/api/blobs/00000000-0000-0000-0000-000000000099")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_octet_stream_when_download_blob_given_default_content_type(
        self, auth_client: AsyncClient
    ):
        upload_files = {"file": ("test.pdf", io.BytesIO(b"PDF content"), "application/pdf")}
        upload_response = await auth_client.post("/api/blobs", files=upload_files)
        assert upload_response.status_code == 201
        blob_id = upload_response.json()["id"]

        download_response = await auth_client.get(f"/api/blobs/{blob_id}")
        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "application/octet-stream"

    @pytest.mark.asyncio
    async def test_should_return_custom_content_type_when_download_with_content_type_param(
        self, auth_client: AsyncClient
    ):
        upload_files = {"file": ("test.pdf", io.BytesIO(b"PDF content"), "application/pdf")}
        upload_response = await auth_client.post("/api/blobs", files=upload_files)
        assert upload_response.status_code == 201
        blob_id = upload_response.json()["id"]

        download_response = await auth_client.get(
            f"/api/blobs/{blob_id}?content_type=application/pdf"
        )
        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "application/pdf"


class TestUpdateBlob:
    @pytest.mark.asyncio
    async def test_should_return_200_when_update_blob_given_valid_id(self, auth_client: AsyncClient):
        upload_files = {"file": ("old.txt", io.BytesIO(b"Old content"), "text/plain")}
        upload_response = await auth_client.post("/api/blobs", files=upload_files)
        assert upload_response.status_code == 201
        original_blob_id = upload_response.json()["id"]

        update_files = {"file": ("new.txt", io.BytesIO(b"New content"), "text/plain")}
        update_response = await auth_client.put(
            f"/api/blobs/{original_blob_id}", files=update_files
        )
        assert update_response.status_code == 200
        data = update_response.json()
        assert "id" in data
        assert data["id"] != original_blob_id

    @pytest.mark.asyncio
    async def test_should_return_401_when_update_blob_given_no_auth(self, client: AsyncClient):
        files = {"file": ("test.txt", io.BytesIO(b"New content"), "text/plain")}
        response = await client.put("/api/blobs/some-blob-id", files=files)
        assert response.status_code == 401


class TestBlobEdgeCases:
    @pytest.mark.asyncio
    async def test_should_return_201_when_upload_blob_given_empty_file(self, auth_client: AsyncClient):
        files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
        response = await auth_client.post("/api/blobs", files=files)
        assert response.status_code == 201
        data = response.json()
        assert data["size"] == 0

    @pytest.mark.asyncio
    async def test_should_preserve_content_when_upload_and_download_given_special_chars(
        self, auth_client: AsyncClient
    ):
        special_content = "Hello 🌍 Emoji and special chars: 你好世界 🚀".encode()
        files = {"file": ("special.txt", io.BytesIO(special_content), "text/plain")}
        response = await auth_client.post("/api/blobs", files=files)
        assert response.status_code == 201
        data = response.json()
        blob_id = data["id"]

        download_response = await auth_client.get(f"/api/blobs/{blob_id}")
        assert download_response.status_code == 200
        assert download_response.content == special_content

    @pytest.mark.asyncio
    async def test_should_match_hash_when_download_blob_given_uploaded_content(
        self, auth_client: AsyncClient
    ):
        test_content = b"Hash verification test content"
        expected_hash = hashlib.sha256(test_content).hexdigest()

        files = {"file": ("hash_test.txt", io.BytesIO(test_content), "text/plain")}
        upload_response = await auth_client.post("/api/blobs", files=files)
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        assert upload_data["content_hash"] == expected_hash

        blob_id = upload_data["id"]
        download_response = await auth_client.get(f"/api/blobs/{blob_id}")
        assert download_response.status_code == 200

        downloaded_content = download_response.content
        actual_hash = hashlib.sha256(downloaded_content).hexdigest()
        assert actual_hash == expected_hash
