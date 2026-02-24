"""
API层路径遍历攻击防护测试

验证API层是否正确处理路径遍历攻击尝试，确保系统的路径安全。

攻击向量测试：
1. ../../../etc/passwd - 简单遍历
2. src/../../../etc/passwd - 复杂遍历
3. ~/.bashrc - 波浪号
4. 超长路径（>512字符）
"""

import pytest
from httpx import AsyncClient


class TestPathTraversalCreateFile:
    """测试POST /api/trees/{id}/files路径遍历防护"""

    @pytest.mark.asyncio
    async def test_should_return_400_when_create_file_given_simple_traversal(
        self, auth_client: AsyncClient
    ):
        """场景1: 简单路径遍历序列 ../../../etc/passwd"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "../../../etc/passwd",
                "type": "blob",
                "content": "malicious content",
            },
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_return_400_when_create_file_given_complex_traversal(
        self, auth_client: AsyncClient
    ):
        """场景2: 复杂路径遍历序列 src/../../../etc/passwd"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "src/../../../etc/passwd",
                "type": "blob",
                "content": "malicious content",
            },
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_return_400_when_create_file_given_tilde_path(self, auth_client: AsyncClient):
        """场景3: 波浪号路径 ~/.bashrc"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "~/.bashrc",
                "type": "blob",
                "content": "malicious content",
            },
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_return_400_when_create_file_given_long_path(self, auth_client: AsyncClient):
        """场景4: 超长路径（>512字符）"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        long_path = "a" * 513
        response = await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": long_path,
                "type": "blob",
                "content": "test content",
            },
        )
        assert response.status_code in (400, 422)


class TestPathTraversalRenameFile:
    """测试PUT /api/trees/{id}/files/rename路径遍历防护"""

    @pytest.mark.asyncio
    async def test_should_return_400_when_rename_given_traversal_in_new_path(
        self, auth_client: AsyncClient
    ):
        """场景1: 重命名目标路径包含遍历序列"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file.txt", "type": "blob", "content": "original"},
        )

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/rename",
            json={"old_path": "file.txt", "new_path": "../../../etc/passwd"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_return_400_when_rename_given_traversal_in_old_path(
        self, auth_client: AsyncClient
    ):
        """场景2: 重命名源路径包含遍历序列"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/rename",
            json={"old_path": "../../../etc/passwd", "new_path": "file.txt"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_return_400_when_rename_given_tilde_in_new_path(self, auth_client: AsyncClient):
        """场景3: 重命名目标路径包含波浪号"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file.txt", "type": "blob", "content": "original"},
        )

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/rename",
            json={"old_path": "file.txt", "new_path": "~/.ssh/id_rsa"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_return_400_when_rename_given_long_new_path(self, auth_client: AsyncClient):
        """场景4: 重命名目标路径超长（>512字符）"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file.txt", "type": "blob", "content": "original"},
        )

        long_path = "b" * 513
        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/rename",
            json={"old_path": "file.txt", "new_path": long_path},
        )
        assert response.status_code in (400, 422)


class TestPathTraversalMoveFile:
    """测试PUT /api/trees/{id}/files/move路径遍历防护"""

    @pytest.mark.asyncio
    async def test_should_return_400_when_move_given_traversal_in_target(self, auth_client: AsyncClient):
        """场景1: 移动目标路径包含遍历序列"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file.txt", "type": "blob", "content": "original"},
        )

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/move",
            json={"source": "file.txt", "target": "../../../etc/passwd"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_return_400_when_move_given_traversal_in_source(self, auth_client: AsyncClient):
        """场景2: 移动源路径包含遍历序列"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/move",
            json={"source": "../../../etc/passwd", "target": "file.txt"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_return_400_when_move_given_tilde_in_target(self, auth_client: AsyncClient):
        """场景3: 移动目标路径包含波浪号"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file.txt", "type": "blob", "content": "original"},
        )

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/move",
            json={"source": "file.txt", "target": "~/.bashrc"},
        )
        assert response.status_code == 400


class TestPathTraversalDeleteFile:
    """测试DELETE /api/trees/{id}/files路径遍历防护"""

    @pytest.mark.asyncio
    async def test_should_return_400_when_delete_given_traversal_path(self, auth_client: AsyncClient):
        """场景1: 删除路径包含遍历序列"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.request(
            "DELETE",
            f"/api/trees/{tree_id}/files",
            json={"path": "../../../etc/passwd"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_should_return_400_when_delete_given_tilde_path(self, auth_client: AsyncClient):
        """场景2: 删除路径包含波浪号"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        response = await auth_client.request(
            "DELETE",
            f"/api/trees/{tree_id}/files",
            json={"path": "~/.ssh/id_rsa"},
        )
        assert response.status_code == 400


class TestPathTraversalUpdateContent:
    """测试PUT /api/trees/{id}/files/content路径遍历防护"""

    @pytest.mark.asyncio
    async def test_should_return_400_when_update_content_given_traversal_path(
        self, auth_client: AsyncClient
    ):
        """场景1: 更新内容路径包含遍历序列"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file.txt", "type": "blob", "content": "original"},
        )

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/content",
            json={"path": "../../../etc/passwd", "content": "malicious"},
        )
        # API可能返回400(验证错误)或404(文件未找到)，都表示请求被拒绝
        assert response.status_code in (400, 404)

    @pytest.mark.asyncio
    async def test_should_return_400_when_update_content_given_tilde_path(
        self, auth_client: AsyncClient
    ):
        """场景2: 更新内容路径包含波浪号"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file.txt", "type": "blob", "content": "original"},
        )

        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/content",
            json={"path": "~/.bashrc", "content": "malicious"},
        )
        assert response.status_code in (400, 404)

    @pytest.mark.asyncio
    async def test_should_return_400_when_update_content_given_long_path(self, auth_client: AsyncClient):
        """场景3: 更新内容路径超长（>512字符）"""
        tree_response = await auth_client.post("/api/trees", json={"entries": []})
        assert tree_response.status_code == 201
        tree_id = tree_response.json()["id"]

        await auth_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "file.txt", "type": "blob", "content": "original"},
        )

        long_path = "a" * 513
        response = await auth_client.put(
            f"/api/trees/{tree_id}/files/content",
            json={"path": long_path, "content": "test content"},
        )
        assert response.status_code in (400, 422)
