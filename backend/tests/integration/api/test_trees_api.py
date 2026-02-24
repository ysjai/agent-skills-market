import io

import pytest
from httpx import AsyncClient

class TestCreateTree:
    @pytest.mark.asyncio
    async def test_should_return_201_when_create_tree_given_valid_input(self, auth_client: AsyncClient):
        response = await auth_client.post(
            "/api/trees",
            json={
                "entries": [
                    {
                        "path": "README.md",
                        "type": "blob",
                        "blob_id": "7318cec3-d2e4-4117-816e-ca12e361f762",
                    }
                ]
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "entries" in data

    @pytest.mark.asyncio
    async def test_should_return_tree_with_entries_when_create_tree_given_entries(
        self, auth_client: AsyncClient
    ):
        entries = [
            {"path": "SKILL.md", "type": "blob", "blob_id": "7318cec3-d2e4-4117-816e-ca12e361f762"},
            {"path": "templates/", "type": "tree"},
            {"path": "examples/", "type": "tree"},
        ]
        response = await auth_client.post("/api/trees", json={"entries": entries})
        assert response.status_code == 201
        data = response.json()
        assert len(data["entries"]) == 3

    @pytest.mark.asyncio
    async def test_should_return_401_when_create_tree_given_no_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/trees",
            json={
                "entries": [
                    {
                        "path": "test.txt",
                        "type": "blob",
                        "blob_id": "7318cec3-d2e4-4117-816e-ca12e361f762",
                    }
                ]
            },
        )
        assert response.status_code == 401

class TestGetTree:
    @pytest.mark.asyncio
    async def test_should_return_tree_when_get_tree_given_valid_id(self, auth_client: AsyncClient):
        create_response = await auth_client.post(
            "/api/trees",
            json={
                "entries": [
                    {
                        "path": "test.txt",
                        "type": "blob",
                        "blob_id": "7318cec3-d2e4-4117-816e-ca12e361f762",
                    }
                ]
            },
        )
        assert create_response.status_code == 201
        tree_id = create_response.json()["id"]

        get_response = await auth_client.get(f"/api/trees/{tree_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == tree_id

    @pytest.mark.asyncio
    async def test_should_return_404_when_get_tree_given_nonexistent_id(self, auth_client: AsyncClient):
        response = await auth_client.get("/api/trees/00000000-0000-0000-0000-000000000001")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_401_when_get_tree_given_no_auth(self, client: AsyncClient):
        response = await client.get("/api/trees/00000000-0000-0000-0000-000000000001")
        assert response.status_code == 401

class TestAddFiles:
    @pytest.mark.asyncio
    async def test_should_add_text_file_when_add_file_given_valid_path(self, auth_client: AsyncClient):
        create_response = await auth_client.post("/api/trees", json={"entries": []})
        assert create_response.status_code == 201
        tree_id = create_response.json()["id"]

        add_response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "hello.txt", "type": "blob", "content": "Hello World"},
        )
        assert add_response.status_code == 200
        data = add_response.json()
        assert len(data["entries"]) == 1
        assert data["entries"][0]["path"] == "hello.txt"

    @pytest.mark.asyncio
    async def test_should_add_binary_file_when_add_file_given_valid_blob(self, auth_client: AsyncClient):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        blob_response = await auth_client.post(
            "/api/blobs",
            files={"file": ("image.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")},
        )
        blob_id = blob_response.json()["id"]

        add_response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "image.png", "type": "blob", "blob_id": blob_id},
        )
        assert add_response.status_code == 200
        data = add_response.json()
        assert any(e["path"] == "image.png" for e in data["entries"])

    @pytest.mark.asyncio
    async def test_should_add_folder_when_add_file_given_tree_type(self, auth_client: AsyncClient):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        add_response = await auth_client.post(
            f"/api/trees/{tree_id}/files", json={"path": "docs/", "type": "tree"}
        )
        assert add_response.status_code == 200
        data = add_response.json()
        assert any(e["path"] == "docs/" and e["type"] == "tree" for e in data["entries"])

    @pytest.mark.asyncio
    async def test_should_add_file_to_nested_path_when_add_file_given_nested_path(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        await auth_client.post(f"/api/trees/{tree_id}/files", json={"path": "src/", "type": "tree"})

        add_response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "src/main.py", "type": "blob", "content": "print('hello')"},
        )
        assert add_response.status_code == 200

    @pytest.mark.asyncio
    async def test_should_return_409_when_add_file_given_duplicate_path(self, auth_client: AsyncClient):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "test.txt", "type": "blob", "content": "first"},
        )

        add_response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "test.txt", "type": "blob", "content": "second"},
        )
        assert add_response.status_code == 409

    @pytest.mark.asyncio
    async def test_should_return_401_when_add_file_given_no_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/trees/00000000-0000-0000-0000-000000000001/files",
            json={"path": "test.txt", "type": "blob", "content": "hello"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_should_upload_all_files_when_batch_upload_given_valid_entries(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        batch_response = await auth_client.post(
            f"/api/trees/{tree_id}/files/batch",
            json={
                "entries": [
                    {"path": "a.txt", "type": "blob", "content": "content a"},
                    {"path": "b.txt", "type": "blob", "content": "content b"},
                ]
            },
        )
        assert batch_response.status_code == 200
        data = batch_response.json()
        assert data["uploaded"] == 2
        assert data["failed"] == 0

    @pytest.mark.asyncio
    async def test_should_create_folder_structure_when_folder_upload_given_valid_entries(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        blob_response = await auth_client.post(
            "/api/blobs", files={"file": ("f.txt", io.BytesIO(b"folder content"), "text/plain")}
        )
        blob_id = blob_response.json()["id"]

        folder_response = await auth_client.post(
            f"/api/trees/{tree_id}/files/folder",
            json={
                "base_path": "myfolder",
                "entries": [{"path": "file.txt", "type": "blob", "blob_id": blob_id}],
            },
        )
        assert folder_response.status_code == 200

    @pytest.mark.asyncio
    async def test_should_update_content_when_update_file_given_valid_path(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "update.txt", "type": "blob", "content": "original"},
        )

        update_response = await auth_client.put(
            f"/api/trees/{tree_id}/files/content",
            json={"path": "update.txt", "content": "updated content"},
        )
        assert update_response.status_code == 200
        data = update_response.json()
        entry = next(e for e in data["entries"] if e["path"] == "update.txt")
        assert entry["blob_id"] is not None

    @pytest.mark.asyncio
    async def test_should_preserve_old_blobs_when_update_file_given_new_content(
        self, auth_client: AsyncClient
    ):
        import uuid

        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        unique_v1 = f"version1_{uuid.uuid4()}"
        add_response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "test.txt", "type": "blob", "content": unique_v1},
        )
        assert add_response.status_code == 200
        data = add_response.json()
        blob_v1_id = next(e["blob_id"] for e in data["entries"] if e["path"] == "test.txt")

        unique_v2 = f"version2_{uuid.uuid4()}"
        update_response = await auth_client.put(
            f"/api/trees/{tree_id}/files/content",
            json={"path": "test.txt", "content": unique_v2},
        )
        assert update_response.status_code == 200
        data = update_response.json()
        blob_v2_id = next(e["blob_id"] for e in data["entries"] if e["path"] == "test.txt")

        assert blob_v1_id != blob_v2_id

        blob_v2_get = await auth_client.get(f"/api/blobs/{blob_v2_id}")
        assert blob_v2_get.status_code == 200

        blob_v1_get = await auth_client.get(f"/api/blobs/{blob_v1_id}")
        assert blob_v1_get.status_code == 200

class TestTreeEdgeCases:
    @pytest.mark.asyncio
    async def test_should_return_400_when_add_file_given_path_traversal_double_dot(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        add_response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "../etc/passwd", "type": "blob", "content": "malicious"},
        )
        assert add_response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_return_400_when_add_file_given_path_traversal_tilde(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        add_response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "~/.ssh/id_rsa", "type": "blob", "content": "private key"},
        )
        assert add_response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_accept_path_when_add_file_given_unicode_path(self, auth_client: AsyncClient):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        add_response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "文档/中文.txt", "type": "blob", "content": "中文内容"},
        )
        assert add_response.status_code == 200

    @pytest.mark.asyncio
    async def test_should_create_deep_structure_when_add_file_given_deeply_nested_path(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        deep_path = "/".join([f"dir{i}" for i in range(15)]) + "/file.txt"
        add_response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": deep_path, "type": "blob", "content": "deep"},
        )
        assert add_response.status_code == 200

    @pytest.mark.asyncio
    async def test_should_return_400_when_delete_root_path_given_root_path(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        delete_response = await auth_client.delete(f"/api/trees/{tree_id}/files?path=/")
        assert delete_response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_upload_and_verify_content_when_upload_files_given_various_content(
        self, auth_client: AsyncClient
    ):
        import io
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]
        folders = ["src/", "tests/", "docs/", "assets/"]
        for folder in folders:
            add_response = await auth_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": folder, "type": "tree"},
            )
            assert add_response.status_code == 200, f"创建 {folder} 失败"

        # 准备文件内容 - 使用实际内容便于比对
        file_contents = {
            "src/main.py": b"def main():\n    print('hello world')",
            "src/utils.py": b"def helper():\n    return 42",
            "src/__init__.py": b"",
            "tests/test_main.py": b"def test_main():\n    assert True",
            "tests/__init__.py": b"",
            "docs/README.md": b"# Documentation\n\nThis is a test.",
            "docs/API.md": b"# API\n\n## Endpoints",
            "config.json": b'{"name": "test", "version": "1.0.0"}',
            "requirements.txt": b"pytest>=7.0.0\nrequests>=2.28.0",
        }

        # 上传文件并获取 blob_id
        uploaded_files = {}
        for filename, content in file_contents.items():
            blob_response = await auth_client.post(
                "/api/blobs",
                files={"file": (filename, io.BytesIO(content), "application/octet-stream")},
            )
            assert blob_response.status_code == 201, f"上传 blob {filename} 失败"
            blob_id = blob_response.json()["id"]
            uploaded_files[filename] = {"content": content, "blob_id": blob_id}

        # 将所有文件添加到树
        for filename, data in uploaded_files.items():
            add_response = await auth_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": filename, "type": "blob", "blob_id": data["blob_id"]},
            )
            assert add_response.status_code == 200, f"添加文件 {filename} 到树失败"
        get_response = await auth_client.get(f"/api/trees/{tree_id}")
        assert get_response.status_code == 200
        tree_data = get_response.json()
        entries = tree_data.get("entries", [])
        paths = [e["path"] for e in entries]
        for filename in file_contents.keys():
            assert filename in paths, f"文件 {filename} 不在目录树中"
        for folder in folders:
            assert folder in paths, f"目录 {folder} 不在目录树中"
        for filename, data in uploaded_files.items():
            # 找到对应的 entry
            entry = next((e for e in entries if e["path"] == filename), None)
            assert entry is not None, f"找不到文件 {filename}"
            assert entry.get("blob_id") == data["blob_id"], "blob_id 不匹配"

            # 下载并验证内容
            download_response = await auth_client.get(f"/api/blobs/{data['blob_id']}")
            assert download_response.status_code == 200, f"下载 {filename} 失败"
            assert download_response.content == data["content"], f"内容比对失败: {filename}"

class TestDeleteFiles:
    @pytest.mark.asyncio
    async def test_should_delete_file_when_delete_file_given_valid_path(self, auth_client: AsyncClient):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "delete_me.txt", "type": "blob", "content": "to be deleted"},
        )

        delete_response = await auth_client.request(
            "DELETE",
            f"/api/trees/{tree_id}/files",
            json={"path": "delete_me.txt"},
        )
        assert delete_response.status_code == 200
        data = delete_response.json()
        paths = [e["path"] for e in data["entries"]]
        assert "delete_me.txt" not in paths

    @pytest.mark.asyncio
    async def test_should_delete_folder_when_delete_file_given_folder_path(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files", json={"path": "folder/", "type": "tree"}
        )
        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "folder/file.txt", "type": "blob", "content": "content"},
        )

        delete_response = await auth_client.request(
            "DELETE",
            f"/api/trees/{tree_id}/files",
            json={"path": "folder/"},
        )
        assert delete_response.status_code == 200

    @pytest.mark.asyncio
    async def test_should_return_400_when_delete_file_given_nonexistent_path(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        delete_response = await auth_client.request(
            "DELETE",
            f"/api/trees/{tree_id}/files",
            json={"path": "nonexistent.txt"},
        )
        assert delete_response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_return_401_when_delete_file_given_no_auth(self, client: AsyncClient):
        response = await client.request(
            "DELETE",
            "/api/trees/00000000-0000-0000-0000-000000000001/files",
            json={"path": "test.txt"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_should_return_400_when_delete_skill_md_given_skill_md_path(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        # Create SKILL.md file
        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "SKILL.md", "type": "blob", "content": "# Skill\n"},
        )

        # Try to delete SKILL.md - should be forbidden
        delete_response = await auth_client.request(
            "DELETE",
            f"/api/trees/{tree_id}/files",
            json={"path": "SKILL.md"},
        )
        assert delete_response.status_code == 400
        assert "Cannot delete SKILL.md" in delete_response.json()["message"]

    @pytest.mark.asyncio
    async def test_should_keep_blob_when_delete_file_given_shared_blob(self, auth_client: AsyncClient):
        import io

        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        blob_response = await auth_client.post(
            "/api/blobs",
            files={"file": ("to_delete.txt", io.BytesIO(b"delete me"), "text/plain")},
        )
        blob_id = blob_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "to_delete.txt", "type": "blob", "blob_id": blob_id},
        )

        delete_response = await auth_client.request(
            "DELETE",
            f"/api/trees/{tree_id}/files",
            json={"path": "to_delete.txt"},
        )
        assert delete_response.status_code == 200

        blob_get_response = await auth_client.get(f"/api/blobs/{blob_id}")
        assert blob_get_response.status_code == 200, (
            "blob 应该保留（blob是共享存储，不会被级联删除）"
        )

    @pytest.mark.asyncio
    async def test_should_delete_blob_when_delete_file_given_no_references(
        self, auth_client: AsyncClient
    ):
        import io
        import uuid

        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        unique_content = f"orphan content {uuid.uuid4()}".encode()
        blob_response = await auth_client.post(
            "/api/blobs",
            files={"file": ("orphan.txt", io.BytesIO(unique_content), "text/plain")},
        )
        orphan_blob_id = blob_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "orphan.txt", "type": "blob", "blob_id": orphan_blob_id},
        )

        delete_response = await auth_client.request(
            "DELETE",
            f"/api/trees/{tree_id}/files",
            json={"path": "orphan.txt"},
        )
        assert delete_response.status_code == 200

        blob_get_response = await auth_client.get(f"/api/blobs/{orphan_blob_id}")
        assert blob_get_response.status_code == 404, "blob 引用数为0应该被删除"

    @pytest.mark.asyncio
    async def test_should_keep_blob_when_delete_one_reference_given_shared_blob(
        self, auth_client: AsyncClient
    ):
        import io
        import uuid

        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        unique_content = f"shared content {uuid.uuid4()}".encode()
        blob_response = await auth_client.post(
            "/api/blobs",
            files={"file": ("shared.txt", io.BytesIO(unique_content), "text/plain")},
        )
        shared_blob_id = blob_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file1.txt", "type": "blob", "blob_id": shared_blob_id},
        )
        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file2.txt", "type": "blob", "blob_id": shared_blob_id},
        )

        delete_response = await auth_client.delete(f"/api/trees/{tree_id}/files?path=file1.txt")
        assert delete_response.status_code == 200

        blob_get_response = await auth_client.get(f"/api/blobs/{shared_blob_id}")
        assert blob_get_response.status_code == 200, "blob 还有引用应该保留"

class TestRenameMove:
    @pytest.mark.asyncio
    async def test_should_rename_file_when_rename_given_valid_paths(self, auth_client: AsyncClient):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "old_name.txt", "type": "blob", "content": "content"},
        )

        rename_response = await auth_client.put(
            f"/api/trees/{tree_id}/files/rename",
            json={"old_path": "old_name.txt", "new_path": "new_name.txt"},
        )
        assert rename_response.status_code == 200
        data = rename_response.json()
        paths = [e["path"] for e in data["entries"]]
        assert "new_name.txt" in paths
        assert "old_name.txt" not in paths

    @pytest.mark.asyncio
    async def test_should_move_file_when_move_given_valid_source_and_target(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        await auth_client.post(f"/api/trees/{tree_id}/files", json={"path": "src/", "type": "tree"})
        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file.txt", "type": "blob", "content": "content"},
        )

        move_response = await auth_client.put(
            f"/api/trees/{tree_id}/files/move",
            json={"source": "file.txt", "target": "src/file.txt"},
        )
        assert move_response.status_code == 200
        data = move_response.json()
        paths = [e["path"] for e in data["entries"]]
        assert "src/file.txt" in paths, "新路径应该有文件"
        assert "file.txt" not in paths, "原路径应该已移除"

    @pytest.mark.asyncio
    async def test_should_return_409_when_rename_given_existing_target_name(
        self, auth_client: AsyncClient
    ):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file1.txt", "type": "blob", "content": "content1"},
        )
        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file2.txt", "type": "blob", "content": "content2"},
        )

        rename_response = await auth_client.put(
            f"/api/trees/{tree_id}/files/rename",
            json={"old_path": "file1.txt", "new_path": "file2.txt"},
        )
        assert rename_response.status_code == 409

    @pytest.mark.asyncio
    async def test_should_return_400_when_move_given_invalid_target(self, auth_client: AsyncClient):
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file.txt", "type": "blob", "content": "content"},
        )

        move_response = await auth_client.put(
            f"/api/trees/{tree_id}/files/move",
            json={"source": "file.txt", "target": "/absolute/path.txt"},
        )
        assert move_response.status_code == 400
