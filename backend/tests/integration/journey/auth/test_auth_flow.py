
import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_override_get_db


class TestAuthFlow:
    @pytest_asyncio.fixture
    async def token_user(self, db_session: AsyncSession):
        import uuid

        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"journey6_{unique_id}@example.com"
        username = f"journey6user_{unique_id}"

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
    async def token_info(
        self,
        db_session: AsyncSession,
        token_user,
    ):
        from app.auth import create_access_token, create_refresh_token
        from app.infra.persistence.db.session import get_db
        from app.main import app

        app.dependency_overrides[get_db] = create_override_get_db(db_session)
        access_token = create_access_token({"sub": str(token_user.id)})
        refresh_token_str = create_refresh_token({"sub": str(token_user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "app": app,
            "user_email": token_user.email,
        }

    @pytest.mark.asyncio
    async def test_should_refresh_token_when_use_refresh_endpoint_given_valid_refresh_token(
        self, token_info
    ):

        access_token = token_info["access_token"]
        refresh_token = token_info["refresh_token"]
        app = token_info["app"]
        user_email = token_info["user_email"]

        async with AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": f"Bearer {access_token}"},
        ) as client:
            # Step 1: GET /auth/me (正常)
            response = await client.get("/api/auth/me")
            assert response.status_code == 200, f"获取当前用户失败: {response.text}"
            user_data = response.json()
            assert user_data["email"] == user_email

            # Step 2: POST /auth/refresh (使用 refresh_token)
            response = await client.post(
                "/api/auth/refresh",
                headers={"Authorization": f"Bearer {refresh_token}"},
            )
            assert response.status_code == 200, f"刷新token失败: {response.text}"
            token_data = response.json()
            assert "access_token" in token_data, "响应应该包含 access_token"
            new_token = token_data["access_token"]

            # Step 3: 使用新 token 获取 /auth/me
            response = await client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {new_token}"},
            )
            assert response.status_code == 200, f"新token获取用户失败: {response.text}"
            user_data_new = response.json()
            assert user_data_new["email"] == user_email

