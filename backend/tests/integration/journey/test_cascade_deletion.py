"""Skill-Tree级联删除测试

验证删除Skill时是否正确级联删除关联的Tree和Blob引用计数。
"""

from uuid import UUID

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.persistence.db.session import get_db
from src.infra.persistence.models.blob_model import BlobModel
from src.infra.persistence.models.tree_model import TreeModel
from src.main import app
from tests.conftest import create_override_get_db

class TestCascadeDeletion:
    """测试Skill删除时的级联行为"""

    @pytest_asyncio.fixture
    async def cascade_user(self, db_session: AsyncSession):
        """创建测试用户"""
        import uuid

        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"cascade_{unique_id}@example.com"
        username = f"cascadeuser_{unique_id}"

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
    async def cascade_client(
        self,
        db_session: AsyncSession,
        cascade_user,
    ) -> AsyncClient:
        """创建认证客户端"""
        from src.auth import create_access_token

        app.dependency_overrides[get_db] = create_override_get_db(db_session)
        token = create_access_token({"sub": str(cascade_user.id)})

        async with AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": f"Bearer {token}"},
        ) as ac:
            yield ac

    async def _get_tree(self, db_session: AsyncSession, tree_id: UUID) -> TreeModel | None:
        """查询Tree是否存在"""
        result = await db_session.execute(
            select(TreeModel).where(TreeModel.id == tree_id)
        )
        return result.scalar_one_or_none()

    async def _get_blob(self, db_session: AsyncSession, blob_id: UUID) -> BlobModel | None:
        """查询Blob是否存在"""
        result = await db_session.execute(
            select(BlobModel).where(BlobModel.id == blob_id)
        )
        return result.scalar_one_or_none()

    async def _get_blob_ref_count(self, db_session: AsyncSession, blob_id: UUID) -> int:
        """查询Blob的引用计数"""
        result = await db_session.execute(
            select(BlobModel.reference_count).where(BlobModel.id == blob_id)
        )
        return result.scalar() or 0

    @pytest.mark.asyncio
    async def test_tree_is_cleaned_up_after_skill_deletion(
        self, cascade_client: AsyncClient, db_session: AsyncSession
    ):
        """场景1: 删除Skill后Tree被清理"""

        # Given: 创建Skill（会自动创建Tree）
        response = await cascade_client.post(
            "/api/skills",
            json={
                "name": "cascade-test-skill-1",
                "slug": "cascade-test-skill-1",
                "description": "Test skill for cascade deletion",
            },
        )
        assert response.status_code == 201, f"创建Skill失败: {response.text}"
        skill_data = response.json()
        skill_id = skill_data["id"]
        tree_id = skill_data["tree_id"]
        assert tree_id is not None, "Skill应该关联一个Tree"
        tree = await self._get_tree(db_session, UUID(tree_id))
        assert tree is not None, "Tree应该存在"

        # When: 删除Skill
        response = await cascade_client.delete(f"/api/skills/{skill_id}")
        assert response.status_code == 204, f"删除Skill失败: {response.status_code}"

        # Then: Tree应该被删除
        tree = await self._get_tree(db_session, UUID(tree_id))
        assert tree is None, f"Tree {tree_id} 应该被级联删除"


    @pytest.mark.asyncio
    async def test_blob_ref_count_decreases_after_skill_deletion(
        self, cascade_client: AsyncClient, db_session: AsyncSession
    ):
        """场景2: 删除Skill后Blob引用计数减少"""

        # Given: 创建Skill
        response = await cascade_client.post(
            "/api/skills",
            json={
                "name": "cascade-test-skill-2",
                "slug": "cascade-test-skill-2",
                "description": "Test skill for blob ref count",
            },
        )
        assert response.status_code == 201
        skill_data = response.json()
        skill_id = skill_data["id"]
        tree_id = skill_data["tree_id"]

        # 上传Blob文件
        response = await cascade_client.post(
            "/api/blobs",
            files={"file": ("test.txt", b"test content for ref count", "text/plain")},
        )
        assert response.status_code == 201
        blob_data = response.json()
        blob_id = blob_data["id"]
        response = await cascade_client.post(
            f"/api/trees/{tree_id}/files",
            json={
                "path": "test.txt",
                "type": "blob",
                "blob_id": blob_id,
            },
        )
        assert response.status_code == 200

        # 刷新Blob引用计数
        await db_session.flush()
        initial_ref_count = await self._get_blob_ref_count(db_session, UUID(blob_id))
        assert initial_ref_count > 0, "Blob引用计数应该大于0"

        # When: 删除Skill
        response = await cascade_client.delete(f"/api/skills/{skill_id}")
        assert response.status_code == 204

        # Then: Blob引用计数应该减少
        # 我们需要检查Blob是否仍然存在，如果存在则引用计数应该正确
        blob = await self._get_blob(db_session, UUID(blob_id))
        if blob is not None:
            new_ref_count = await self._get_blob_ref_count(db_session, UUID(blob_id))
        else:


    @pytest.mark.asyncio
    async def test_shared_blob_ref_count_accuracy(
        self, cascade_client: AsyncClient, db_session: AsyncSession
    ):
        """场景3: 多Skill共享Blob的引用计数准确性"""

        # Given: 上传一个共享的Blob
        response = await cascade_client.post(
            "/api/blobs",
            files={"file": ("shared.txt", b"shared content", "text/plain")},
        )
        assert response.status_code == 201
        blob_data = response.json()
        shared_blob_id = blob_data["id"]
        response = await cascade_client.post(
            "/api/skills",
            json={
                "name": "cascade-test-skill-3a",
                "slug": "cascade-test-skill-3a",
                "description": "First skill with shared blob",
            },
        )
        assert response.status_code == 201
        skill1_data = response.json()
        skill1_id = skill1_data["id"]
        tree1_id = skill1_data["tree_id"]
        response = await cascade_client.post(
            f"/api/trees/{tree1_id}/files",
            json={
                "path": "shared.txt",
                "type": "blob",
                "blob_id": shared_blob_id,
            },
        )
        assert response.status_code == 200
        response = await cascade_client.post(
            "/api/skills",
            json={
                "name": "cascade-test-skill-3b",
                "slug": "cascade-test-skill-3b",
                "description": "Second skill with shared blob",
            },
        )
        assert response.status_code == 201
        skill2_data = response.json()
        skill2_id = skill2_data["id"]
        tree2_id = skill2_data["tree_id"]
        response = await cascade_client.post(
            f"/api/trees/{tree2_id}/files",
            json={
                "path": "shared.txt",
                "type": "blob",
                "blob_id": shared_blob_id,
            },
        )
        assert response.status_code == 200

        # 刷新并获取初始引用计数
        await db_session.flush()
        initial_ref_count = await self._get_blob_ref_count(db_session, UUID(shared_blob_id))
        assert initial_ref_count >= 2, f"共享Blob引用计数应该至少为2，实际为{initial_ref_count}"

        # When 1: 删除第一个Skill
        response = await cascade_client.delete(f"/api/skills/{skill1_id}")
        assert response.status_code == 204

        # Then 1: Blob应该仍然存在，引用计数减少
        blob = await self._get_blob(db_session, UUID(shared_blob_id))
        assert blob is not None, "共享Blob应该仍然存在"
        ref_count_after_skill1 = await self._get_blob_ref_count(db_session, UUID(shared_blob_id))
        assert ref_count_after_skill1 == initial_ref_count - 1, \
            f"引用计数应该减少1，从{initial_ref_count}变为{initial_ref_count - 1}，实际为{ref_count_after_skill1}"

        # Tree 1应该被删除
        tree1 = await self._get_tree(db_session, UUID(tree1_id))
        assert tree1 is None, "Tree 1应该被删除"

        # When 2: 删除第二个Skill
        response = await cascade_client.delete(f"/api/skills/{skill2_id}")
        assert response.status_code == 204

        # Then 2: Blob应该被删除（引用计数为0）
        blob = await self._get_blob(db_session, UUID(shared_blob_id))
        assert blob is None, f"共享Blob {shared_blob_id} 应该被删除（引用计数归零）"

        # Tree 2应该也被删除
        tree2 = await self._get_tree(db_session, UUID(tree2_id))
        assert tree2 is None, "Tree 2应该被删除"

