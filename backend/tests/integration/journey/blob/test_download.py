from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_override_get_db

class TestDownloadFlow:
    @pytest_asyncio.fixture
    async def download_user(self, db_session: AsyncSession):
        import uuid

        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"journey7_{unique_id}@example.com"
        username = f"journey7user_{unique_id}"

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
    async def download_client(
        self,
        db_session: AsyncSession,
        download_user,
    ) -> AsyncGenerator[AsyncClient, None]:
        from src.auth import create_access_token
        from src.infra.persistence.db.session import get_db
        from src.main import app

        app.dependency_overrides[get_db] = create_override_get_db(db_session)
        token = create_access_token({"sub": str(download_user.id)})

        async with AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": f"Bearer {token}"},
        ) as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_should_download_all_files_when_import_skill_given_multiple_files(
        self, download_client: AsyncClient
    ):
        # Step 1: 创建技能
        response = await download_client.post(
            "/api/skills",
            json={
                "name": "download-skill",
                "slug": "download-skill-journey7",
                "description": "Skill for download test",
            },
        )
        assert response.status_code == 201, "创建技能失败"
        skill_data = response.json()
        skill_id = skill_data["id"]
        tree_id = skill_data["tree_id"]

        # Step 2: 上传多个文件
        files_content = {
            "src/main.py": b"def main():\n    print('hello')",
            "src/utils.py": b"def helper():\n    return 42",
            "config.json": b'{"debug": true}',
            "README.md": b"# Download Test Skill",
        }

        blob_map = {}
        for path, content in files_content.items():
            response = await download_client.post(
                "/api/blobs",
                files={"file": (path, content, "text/plain")},
            )
            assert response.status_code == 201, f"上传 {path} 失败"
            blob_map[path] = response.json()["id"]

        # Step 3: 添加文件夹和文件结构
        response = await download_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "src", "type": "tree"},
        )
        assert response.status_code == 200
        response = await download_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "src/main.py",
                "type": "blob",
                "blob_id": blob_map["src/main.py"],
            },
        )
        assert response.status_code == 200
        response = await download_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "src/utils.py",
                "type": "blob",
                "blob_id": blob_map["src/utils.py"],
            },
        )
        assert response.status_code == 200
        response = await download_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "config.json",
                "type": "blob",
                "blob_id": blob_map["config.json"],
            },
        )
        assert response.status_code == 200
        response = await download_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "README.md",
                "type": "blob",
                "blob_id": blob_map["README.md"],
            },
        )
        assert response.status_code == 200


        # Step 4: 获取文件列表
        response = await download_client.get(f"/api/skills/{skill_id}/files")
        assert response.status_code == 200, "获取文件列表失败"
        skill_files = response.json()

        # Step 5: 逐个下载文件并验证内容
        for path, expected_content in files_content.items():
            blob_id = blob_map[path]
            response = await download_client.get(f"/api/blobs/{blob_id}")
            assert response.status_code == 200, f"下载 {path} 失败"
            actual_content = response.content
            assert actual_content == expected_content, f"{path} 内容不匹配"

        # Step 6: 测试下载 ZIP
        response = await download_client.get(
            f"/api/skills/{skill_id}/download",
            params={"platform": "opencode"},
        )
        assert response.status_code == 200, "下载ZIP失败"
        assert "application/zip" in response.headers.get("content-type", "")

        # 测试下载 Markdown
        response = await download_client.get(
            f"/api/skills/{skill_id}/download",
            params={"platform": "claude"},
        )
        assert response.status_code == 200, "下载Markdown失败"

