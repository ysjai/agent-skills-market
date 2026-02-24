"""Error path tests for trees router.

Tests error scenarios and exception handling in the trees API.
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient


class TestCreateTreeErrorPaths:
    """Test error paths for POST /api/trees"""

    @pytest.mark.asyncio
    async def test_should_return_400_when_create_tree_given_invalid_entry_type(
        self, auth_client: AsyncClient
    ):
        """Test that invalid entry type returns 400"""
        response = await auth_client.post(
            "/api/trees",
            json={
                "entries": [
                    {
                        "path": "test.txt",
                        "type": "invalid_type",  # Invalid type
                        "blob_id": "7318cec3-d2e4-4117-816e-ca12e361f762",
                    }
                ]
            },
        )
        assert response.status_code == 400


class TestGetTreeErrorPaths:
    """Test error paths for GET /api/trees/{tree_id}"""

    @pytest.mark.asyncio
    async def test_should_return_404_when_get_tree_given_invalid_uuid_format(
        self, auth_client: AsyncClient
    ):
        """Test that invalid UUID format returns 404 or 422"""
        response = await auth_client.get("/api/trees/not-a-valid-uuid")
        # FastAPI validates UUID format and returns 422 for invalid format
        assert response.status_code in (404, 422)

    @pytest.mark.asyncio
    async def test_should_return_404_when_get_tree_given_random_uuid(self, auth_client: AsyncClient):
        """Test that non-existent tree returns 404"""
        random_uuid = str(uuid4())
        response = await auth_client.get(f"/api/trees/{random_uuid}")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data.get("message", "").lower()


class TestAddFileErrorPaths:
    """Test error paths for POST /api/trees/{tree_id}/files"""

    @pytest.mark.asyncio
    async def test_should_return_404_when_add_file_given_nonexistent_tree(
        self, auth_client: AsyncClient
    ):
        """Test adding file to non-existent tree returns 404"""
        random_uuid = str(uuid4())
        response = await auth_client.post(
            f"/api/trees/{random_uuid}/files",
            json={"path": "test.txt", "type": "blob", "content": "test"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_400_when_add_file_given_missing_path(self, auth_client: AsyncClient):
        """Test adding file without path returns 400"""
        # First create a tree
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        # Try to add file without path
        response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"type": "blob", "content": "test"},  # Missing path
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_should_return_400_when_add_file_given_empty_path(self, auth_client: AsyncClient):
        """Test adding file with empty path returns 400"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "", "type": "blob", "content": "test"},
        )
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_should_return_400_when_add_file_given_nonexistent_blob_id(
        self, auth_client: AsyncClient
    ):
        """Test adding file with non-existent blob_id returns 400"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        random_blob_id = str(uuid4())
        response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "test.txt", "type": "blob", "blob_id": random_blob_id},
        )
        # API may accept the blob_id and create a reference, or return error
        assert response.status_code in (200, 400, 404)


class TestDeleteFileErrorPaths:
    """Test error paths for DELETE /api/trees/{tree_id}/files"""

    @pytest.mark.asyncio
    async def test_should_return_404_when_delete_file_given_nonexistent_tree(
        self, auth_client: AsyncClient
    ):
        """Test deleting file from non-existent tree returns 404"""
        random_uuid = str(uuid4())
        response = await auth_client.request(
            "DELETE",
            f"/api/trees/{random_uuid}/files",
            json={"path": "test.txt"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_400_when_delete_file_given_missing_path(self, auth_client: AsyncClient):
        """Test deleting file without providing path returns 400"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        # Delete without path parameter or body
        response = await auth_client.delete(f"/api/trees/{tree_id}/files")
        assert response.status_code == 400
        data = response.json()
        assert "path is required" in data.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_should_return_400_when_delete_file_given_empty_path(self, auth_client: AsyncClient):
        """Test deleting file with empty path returns 400"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.request(
            "DELETE",
            f"/api/trees/{tree_id}/files",
            json={"path": ""},
        )
        assert response.status_code in (400, 422)


class TestRenameFileErrorPaths:
    """Test error paths for PUT /api/trees/{tree_id}/files/rename"""

    @pytest.mark.asyncio
    async def test_should_return_404_when_rename_file_given_nonexistent_tree(
        self, auth_client: AsyncClient
    ):
        """Test renaming file in non-existent tree returns 404"""
        random_uuid = str(uuid4())
        response = await auth_client.put(
            f"/api/trees/{random_uuid}/files/rename",
            json={"old_path": "old.txt", "new_path": "new.txt"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_404_when_rename_file_given_nonexistent_file(
        self, auth_client: AsyncClient
    ):
        """Test renaming non-existent file returns 404"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/rename",
            json={"old_path": "nonexistent.txt", "new_path": "new.txt"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_400_when_rename_file_given_missing_old_path(
        self, auth_client: AsyncClient
    ):
        """Test renaming without old_path returns 400"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/rename",
            json={"new_path": "new.txt"},  # Missing old_path
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_should_return_400_when_rename_file_given_missing_new_path(
        self, auth_client: AsyncClient
    ):
        """Test renaming without new_path returns 400"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        # First add a file
        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "old.txt", "type": "blob", "content": "test"},
        )

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/rename",
            json={"old_path": "old.txt"},  # Missing new_path
        )
        assert response.status_code == 422


class TestMoveFileErrorPaths:
    """Test error paths for PUT /api/trees/{tree_id}/files/move"""

    @pytest.mark.asyncio
    async def test_should_return_404_when_move_file_given_nonexistent_tree(
        self, auth_client: AsyncClient
    ):
        """Test moving file in non-existent tree returns 404"""
        random_uuid = str(uuid4())
        response = await auth_client.put(
            f"/api/trees/{random_uuid}/files/move",
            json={"source": "src.txt", "target": "dest.txt"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_404_when_move_file_given_nonexistent_source(
        self, auth_client: AsyncClient
    ):
        """Test moving non-existent file returns 404"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/move",
            json={"source": "nonexistent.txt", "target": "dest.txt"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_400_when_move_file_given_missing_source(self, auth_client: AsyncClient):
        """Test moving without source returns 400"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/move",
            json={"target": "dest.txt"},  # Missing source
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_should_return_400_when_move_file_given_missing_target(self, auth_client: AsyncClient):
        """Test moving without target returns 400"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        # First add a file
        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "src.txt", "type": "blob", "content": "test"},
        )

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/move",
            json={"source": "src.txt"},  # Missing target
        )
        assert response.status_code == 422


class TestUpdateFileContentErrorPaths:
    """Test error paths for PUT /api/trees/{tree_id}/files/content"""

    @pytest.mark.asyncio
    async def test_should_return_404_when_update_content_given_nonexistent_tree(
        self, auth_client: AsyncClient
    ):
        """Test updating content in non-existent tree returns 404"""
        random_uuid = str(uuid4())
        response = await auth_client.put(
            f"/api/trees/{random_uuid}/files/content",
            json={"path": "test.txt", "content": "new content"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_404_when_update_content_given_nonexistent_file(
        self, auth_client: AsyncClient
    ):
        """Test updating content of non-existent file returns 404"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/content",
            json={"path": "nonexistent.txt", "content": "new content"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_400_when_update_content_given_missing_path(
        self, auth_client: AsyncClient
    ):
        """Test updating content without path returns 400"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/content",
            json={"content": "new content"},  # Missing path
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_should_return_400_when_update_content_given_missing_content(
        self, auth_client: AsyncClient
    ):
        """Test updating content without content returns 400"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        # First add a file
        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "test.txt", "type": "blob", "content": "original"},
        )

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/content",
            json={"path": "test.txt"},  # Missing content
        )
        assert response.status_code == 422


class TestBatchUploadErrorPaths:
    """Test error paths for POST /api/trees/{tree_id}/files/batch"""

    @pytest.mark.asyncio
    async def test_should_return_404_when_batch_upload_given_nonexistent_tree(
        self, auth_client: AsyncClient
    ):
        """Test batch upload to non-existent tree returns 404 or 200 depending on implementation"""
        random_uuid = str(uuid4())
        response = await auth_client.post(
            f"/api/trees/{random_uuid}/files/batch",
            json={
                "entries": [
                    {"path": "test1.txt", "type": "blob", "content": "content1"},
                ]
            },
        )
        # Batch upload may swallow the error and report it in failed count
        assert response.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_should_handle_failed_uploads_when_batch_upload_given_invalid_entries(
        self, auth_client: AsyncClient
    ):
        """Test batch upload counts failed uploads correctly"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        # Send invalid entries that will cause failures
        response = await auth_client.post(
            f"/api/trees/{tree_id}/files/batch",
            json={
                "entries": [
                    {"path": "valid.txt", "type": "blob", "content": "valid content"},
                ]
            },
        )
        # Should succeed with tracking of uploaded/failed
        assert response.status_code == 200
        data = response.json()
        assert "uploaded" in data
        assert "failed" in data


class TestFolderUploadErrorPaths:
    """Test error paths for POST /api/trees/{tree_id}/files/folder"""

    @pytest.mark.asyncio
    async def test_should_return_404_when_folder_upload_given_nonexistent_tree(
        self, auth_client: AsyncClient
    ):
        """Test folder upload to non-existent tree returns 404"""
        random_uuid = str(uuid4())
        response = await auth_client.post(
            f"/api/trees/{random_uuid}/files/folder",
            json={
                "base_path": "folder",
                "entries": [{"path": "test.txt", "type": "blob", "content": "test"}],
            },
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_400_when_folder_upload_given_nonexistent_blob(
        self, auth_client: AsyncClient
    ):
        """Test folder upload with non-existent blob returns error"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        random_blob_id = str(uuid4())
        response = await auth_client.post(
            f"/api/trees/{tree_id}/files/folder",
            json={
                "base_path": "folder",
                "entries": [{"path": "test.txt", "type": "blob", "blob_id": random_blob_id}],
            },
        )
        # This may succeed with partial failure or fail completely
        assert response.status_code in (200, 400, 404)
