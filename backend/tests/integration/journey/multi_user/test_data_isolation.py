from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_override_get_db


class TestDataIsolation:
    @pytest_asyncio.fixture
    async def user_a(self, db_session: AsyncSession):
        import uuid

        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"usera_{unique_id}@example.com"
        username = f"usera_{unique_id}"

        password = "password123"
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        from app.infra.persistence.models.user_model import UserModel

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
    async def user_b(self, db_session: AsyncSession):
        import uuid

        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"userb_{unique_id}@example.com"
        username = f"userb_{unique_id}"

        password = "password123"
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        from app.infra.persistence.models.user_model import UserModel

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
    async def client_a(
        self,
        db_session: AsyncSession,
        user_a,
    ) -> AsyncGenerator[AsyncClient, None]:
        from app.auth import create_access_token
        from app.infra.persistence.db.session import get_db
        from app.main import app

        app.dependency_overrides[get_db] = create_override_get_db(db_session)
        token = create_access_token({"sub": str(user_a.id)})

        async with AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": f"Bearer {token}"},
        ) as ac:
            yield ac

    @pytest_asyncio.fixture
    async def client_b(
        self,
        db_session: AsyncSession,
        user_b,
    ) -> AsyncGenerator[AsyncClient, None]:
        from app.auth import create_access_token
        from app.infra.persistence.db.session import get_db
        from app.main import app

        app.dependency_overrides[get_db] = create_override_get_db(db_session)
        token = create_access_token({"sub": str(user_b.id)})

        async with AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": f"Bearer {token}"},
        ) as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_should_isolate_data_when_multiuser_access_given_different_users(
        self,
        client_a: AsyncClient,
        client_b: AsyncClient,
    ):
        # Step 1: 用户A创建技能A
        response = await client_a.post(
            "/api/skills",
            json={
                "name": "skill-a",
                "slug": "skill-a-journey4",
                "description": "Skill from user A",
            },
        )
        assert response.status_code == 201, "用户A创建技能失败"
        skill_a_id = response.json()["id"]

        # Step 2: 用户B创建技能B
        response = await client_b.post(
            "/api/skills",
            json={
                "name": "skill-b",
                "slug": "skill-b-journey4",
                "description": "Skill from user B",
            },
        )
        assert response.status_code == 201, "用户B创建技能失败"
        skill_b_id = response.json()["id"]

        # Step 3: 各自列表验证只能看到自己的
        response = await client_a.get("/api/skills")
        assert response.status_code == 200
        skills_a = response.json()
        skills_a_list = skills_a.get("items", skills_a)
        skill_ids_a = [s["id"] for s in skills_a_list]
        assert skill_a_id in skill_ids_a, "用户A应该看到自己的技能"
        assert skill_b_id not in skill_ids_a, "用户A不应该看到用户B的技能"

        response = await client_b.get("/api/skills")
        assert response.status_code == 200
        skills_b = response.json()
        skills_b_list = skills_b.get("items", skills_b)
        skill_ids_b = [s["id"] for s in skills_b_list]
        assert skill_b_id in skill_ids_b, "用户B应该看到自己的技能"
        assert skill_a_id not in skill_ids_b, "用户B不应该看到用户A的技能"

        # Step 4: 交叉访问 → 403
        response = await client_a.get(f"/api/skills/{skill_b_id}")
        assert response.status_code == 403, "用户A访问用户B的技能应该返回403"

        response = await client_b.get(f"/api/skills/{skill_a_id}")
        assert response.status_code == 403, "用户B访问用户A的技能应该返回403"

        # 额外验证: 跨用户修改也应该是403
        response = await client_a.put(
            f"/api/skills/{skill_b_id}",
            json={"description": "Trying to modify"},
        )
        assert response.status_code == 403, "跨用户修改应该返回403"

        response = await client_a.delete(f"/api/skills/{skill_b_id}")
        assert response.status_code == 403, "跨用户删除应该返回403"

