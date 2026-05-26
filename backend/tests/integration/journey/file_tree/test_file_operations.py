from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_override_get_db


class TestFileOperations:
    @pytest_asyncio.fixture
    async def fileops_user(self, db_session: AsyncSession):
        import uuid

        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"journey3_{unique_id}@example.com"
        username = f"journey3user_{unique_id}"

        password = "password123"
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        from src.infra.persistence.models.user_model import UserModel

        user = UserModel(
            email=email,
            username=username,
            password_hash=password_hash,
            is_active=True,
            email_verified=True,
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)
        return user

    @pytest_asyncio.fixture
    async def fileops_client(
        self,
        db_session: AsyncSession,
        fileops_user,
    ) -> AsyncGenerator[AsyncClient, None]:
        from src.auth import create_access_token
        from src.infra.persistence.db.session import get_db
        from src.main import app

        app.dependency_overrides[get_db] = create_override_get_db(db_session)
        token = create_access_token({"sub": str(fileops_user.id)})

        async with AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": f"Bearer {token}"},
        ) as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_should_complete_file_operations_when_manage_tree(self, fileops_client: AsyncClient):
        # Step 1: 创建技能
        response = await fileops_client.post(
            "/api/skills",
            json={
                "name": "fileops-skill",
                "slug": "fileops-skill-journey3",
                "description": "Skill for file ops test",
            },
        )
        assert response.status_code == 201, f"创建技能失败: {response.text}"
        skill_data = response.json()
        tree_id = skill_data["tree_id"]

        # Step 2: 创建文件夹
        response = await fileops_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "src",
                "type": "tree",
            },
        )
        assert response.status_code == 200, "创建文件夹失败"

        # Step 3: 创建文件
        response = await fileops_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "test.txt",
                "type": "blob",
                "content": "hello",
            },
        )
        assert response.status_code == 200, "创建文件失败"
        response = await fileops_client.get(f"/api/trees/{tree_id}")
        tree_data = response.json()
        entries = tree_data.get("entries", [])
        paths = [e["path"] for e in entries]
        assert "src" in paths, f"src 文件夹应该存在, got: {paths}"
        assert "test.txt" in paths, "test.txt 应该存在"

        # Step 4: 重命名文件
        response = await fileops_client.put(
            f"/api/trees/{tree_id}/files/rename",
            json={
                "old_path": "test.txt",
                "new_path": "hello.txt",
            },
        )
        assert response.status_code == 200, f"重命名失败: {response.text}"
        response = await fileops_client.get(f"/api/trees/{tree_id}")
        tree_data = response.json()
        entries = tree_data.get("entries", [])
        paths = [e["path"] for e in entries]
        assert "hello.txt" in paths, "hello.txt 应该存在"
        assert "test.txt" not in paths, "test.txt 不应该存在"

        # Step 5: 移动文件到文件夹
        response = await fileops_client.put(
            f"/api/trees/{tree_id}/files/move",
            json={
                "source": "hello.txt",
                "target": "src/hello.txt",
            },
        )
        assert response.status_code == 200, f"移动文件失败: {response.text}"
        response = await fileops_client.get(f"/api/trees/{tree_id}")
        tree_data = response.json()
        entries = tree_data.get("entries", [])
        paths = [e["path"] for e in entries]
        assert "src/hello.txt" in paths, "src/hello.txt 应该存在"
        assert "hello.txt" not in paths, "hello.txt 不应该存在"

        # Step 6: 删除文件
        import json

        response = await fileops_client.request(
            "DELETE",
            f"/api/trees/{tree_id}/files",
            content=json.dumps({"path": "src/hello.txt"}),
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200, "删除文件失败"
        response = await fileops_client.get(f"/api/trees/{tree_id}")
        tree_data = response.json()
        entries = tree_data.get("entries", [])
        paths = [e["path"] for e in entries]
        assert "src/hello.txt" not in paths, "src/hello.txt 不应该存在"

