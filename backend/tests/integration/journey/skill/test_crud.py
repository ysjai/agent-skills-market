from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_override_get_db


class TestSkillCRUD:
    @pytest_asyncio.fixture
    async def crud_user(self, db_session: AsyncSession):
        import uuid

        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"crud_{unique_id}@example.com"
        username = f"cruduser_{unique_id}"

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
    async def crud_client(
        self,
        db_session: AsyncSession,
        crud_user,
    ) -> AsyncGenerator[AsyncClient, None]:
        from src.auth import create_access_token
        from src.infra.persistence.db.session import get_db
        from src.main import app

        app.dependency_overrides[get_db] = create_override_get_db(db_session)
        token = create_access_token({"sub": str(crud_user.id)})

        async with AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": f"Bearer {token}"},
        ) as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_should_create_skill_with_files_when_complete_flow_given_valid_inputs(
        self, crud_client: AsyncClient
    ):
        # Step 1: 创建技能
        response = await crud_client.post(
            "/api/skills",
            json={
                "name": "test-skill",
                "slug": "test-skill-journey1",
                "description": "Test skill for journey 1",
            },
        )
        assert response.status_code == 201, f"创建技能失败: {response.text}"
        skill_data = response.json()
        skill_id = skill_data["id"]
        tree_id = skill_data["tree_id"]
        assert tree_id is not None, "技能创建时应自动创建 tree"

        # Step 2: 上传文件1 (hello)
        response = await crud_client.post(
            "/api/blobs",
            files={"file": ("hello.txt", b"hello", "text/plain")},
        )
        assert response.status_code == 201, f"上传文件1失败: {response.text}"
        blob1_data = response.json()
        blob1_id = blob1_data["id"]

        # Step 3: 上传文件2 (world)
        response = await crud_client.post(
            "/api/blobs",
            files={"file": ("world.txt", b"world", "text/plain")},
        )
        assert response.status_code == 201, f"上传文件2失败: {response.text}"
        blob2_data = response.json()
        blob2_id = blob2_data["id"]

        # Step 4: 添加文件1到树
        response = await crud_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "hello.txt",
                "type": "blob",
                "blob_id": blob1_id,
            },
        )
        assert response.status_code == 200, f"添加文件1失败: {response.text}"

        # Step 5: 添加文件2到树
        response = await crud_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "world.txt",
                "type": "blob",
                "blob_id": blob2_id,
            },
        )
        assert response.status_code == 200, f"添加文件2失败: {response.text}"

        # Step 6: 验证技能
        response = await crud_client.get(f"/api/skills/{skill_id}")
        assert response.status_code == 200, f"验证技能失败: {response.text}"
        skill_verify = response.json()
        assert skill_verify["tree_id"] == tree_id

        # Step 7: 获取文件列表
        response = await crud_client.get(f"/api/skills/{skill_id}/files")
        assert response.status_code == 200, f"获取文件列表失败: {response.text}"
        files = response.json()
        assert len(files) >= 2, "应该有至少2个文件"

        # Step 8: 下载验证内容
        response = await crud_client.get(f"/api/blobs/{blob1_id}")
        assert response.status_code == 200, f"下载文件1失败: {response.text}"
        assert b"hello" in response.content, "文件1内容应为 hello"

        # Step 9: 修改文件内容（手动保存测试）
        response = await crud_client.post(
            "/api/blobs",
            files={"file": ("hello.txt", b"hello updated", "text/plain")},
        )
        assert response.status_code == 201, f"上传新版本文件失败: {response.text}"
        new_blob_id = response.json()["id"]
        response = await crud_client.put(
            f"/api/trees/{tree_id}/files/content",
            json={
                "path": "hello.txt",
                "content": "hello updated",
            },
        )
        assert response.status_code == 200, f"修改文件内容失败: {response.text}"

        # Step 10: 验证文件内容已更新
        response = await crud_client.get(f"/api/skills/{skill_id}/files")
        assert response.status_code == 200
        files_data = response.json()
        files = files_data.get("files", [])
        updated_file = next((f for f in files if f["path"] == "hello.txt"), None)
        assert updated_file is not None, "找不到 hello.txt"

        # 下载并验证内容
        response = await crud_client.get(f"/api/blobs/{updated_file['blob_id']}")
        assert response.status_code == 200
        assert b"hello updated" in response.content, "文件内容应该已更新"

    @pytest.mark.asyncio
    async def test_should_cleanup_resources_when_delete_skill_given_existing_skill(
        self, crud_client: AsyncClient
    ):
        # Step 1: 创建技能
        response = await crud_client.post(
            "/api/skills",
            json={
                "name": "delete-skill",
                "slug": "delete-skill-journey5",
                "description": "Skill to be deleted",
            },
        )
        assert response.status_code == 201, "创建技能失败"
        skill_data = response.json()
        skill_id = skill_data["id"]
        tree_id = skill_data["tree_id"]

        # Step 2: 上传 blob
        response = await crud_client.post(
            "/api/blobs",
            files={"file": ("test.txt", b"content", "text/plain")},
        )
        assert response.status_code == 201, "上传blob失败"
        blob_id = response.json()["id"]
        response = await crud_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "test.txt",
                "type": "blob",
                "blob_id": blob_id,
            },
        )
        assert response.status_code == 200

        # Step 3: 删除技能
        response = await crud_client.delete(f"/api/skills/{skill_id}")
        assert response.status_code == 204, f"删除技能失败: {response.status_code}"

        # Step 4: 验证技能 404
        response = await crud_client.get(f"/api/skills/{skill_id}")
        assert response.status_code == 404, "技能应该返回404"

        # Step 5: 验证树 404
        response = await crud_client.get(f"/api/trees/{tree_id}")
        assert response.status_code == 404, "树应该返回404"

        # Step 6: 验证 blob 也被清理（引用计数为0时 blob 会被删除）
        response = await crud_client.get(f"/api/blobs/{blob_id}")
        assert response.status_code == 404, "blob引用计数为0应该被删除"
