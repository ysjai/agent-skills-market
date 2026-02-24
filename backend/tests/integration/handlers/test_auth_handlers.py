"""
Auth Handlers Integration Tests

测试认证相关的 Handler，提升覆盖率到 90%+

需覆盖场景:
- login_handler: 邮箱不存在、密码错误、用户被停用
- register_user_handler: 邮箱已存在、带 phone 参数注册
- refresh_token_handler: 非 refresh token 类型、Token 中无 sub、无效的 user_id 格式、用户被停用
"""

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, create_refresh_token
from app.infra.persistence.models.user_model import UserModel

AUTH_PREFIX = "/api/auth"

class TestLoginHandler:
    """登录 Handler 测试"""

    @pytest.mark.asyncio
    async def test_login_fails_when_email_not_found(self, client: AsyncClient):
        """场景1: 邮箱不存在时返回 UnauthorizedError"""
        response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 401, f"期望401，实际{response.status_code}"
        data = response.json()
        assert data["code"] == "UNAUTHORIZED"
        assert "Incorrect email or password" in data["message"]

    @pytest.mark.asyncio
    async def test_login_fails_when_password_incorrect(
        self,
        client: AsyncClient,
        test_user: UserModel,
    ):
        """场景2: 密码错误时返回 UnauthorizedError"""
        response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword123",
            },
        )
        assert response.status_code == 401, f"期望401，实际{response.status_code}"
        data = response.json()
        assert data["code"] == "UNAUTHORIZED"
        assert "Incorrect email or password" in data["message"]

    @pytest.mark.asyncio
    async def test_login_fails_when_user_is_inactive(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        """场景3: 用户被停用时返回 UnauthorizedError"""
        unique_id = str(uuid.uuid4())[:8]
        email = f"inactive_{unique_id}@example.com"
        username = f"inactiveuser_{unique_id}"
        password = "password123"

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        inactive_user = UserModel(
            email=email,
            username=username,
            password_hash=password_hash,
            is_active=False,  # 被停用
            email_verified=True,
        )
        db_session.add(inactive_user)
        await db_session.flush()
        await db_session.refresh(inactive_user)

        response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={
                "email": email,
                "password": password,
            },
        )
        assert response.status_code == 401, f"期望401，实际{response.status_code}"
        data = response.json()
        assert data["code"] == "UNAUTHORIZED"
        assert "User account is inactive" in data["message"]

class TestRegisterUserHandler:
    """注册用户 Handler 测试"""

    @pytest.mark.asyncio
    async def test_register_fails_when_email_already_exists(
        self,
        client: AsyncClient,
        test_user: UserModel,
    ):
        """场景1: 邮箱已存在时返回 ResourceConflictError"""
        response = await client.post(
            f"{AUTH_PREFIX}/register",
            json={
                "email": test_user.email,
                "username": "newuser123",
                "password": "password123",
            },
        )
        assert response.status_code == 409, f"期望409，实际{response.status_code}"
        data = response.json()
        assert data["code"] == "RESOURCE_CONFLICT"
        assert "Email already registered" in data["message"]

    @pytest.mark.asyncio
    async def test_register_with_phone_parameter(
        self,
        db_session: AsyncSession,
    ):
        """场景2: 带 phone 参数注册，phone 保存成功"""
        from app.application.handlers.register_user_handler import (
            handle_register_user,
        )
        from app.infra.persistence.repositories.sql_user_repository import (
            SqlUserRepository,
        )

        unique_id = str(uuid.uuid4())[:8]
        email = f"phone_test_{unique_id}@example.com"
        username = f"phoneuser_{unique_id}"
        phone = "+86-13800138000"
        password = "password123"

        user_repo = SqlUserRepository(db_session)
        user, access_token, refresh_token = await handle_register_user(
            email=email,
            username=username,
            password=password,
            user_repo=user_repo,
            phone=phone,
        )

        await db_session.flush()

        assert user is not None
        assert str(user.email) == email
        assert user.username == username
        assert user.phone == phone
        assert access_token is not None
        assert refresh_token is not None

        saved_user = await user_repo.get_by_id(user.id)
        assert saved_user is not None
        assert saved_user.phone == phone

class TestRefreshTokenHandler:
    """刷新 Token Handler 测试"""

    @pytest.mark.asyncio
    async def test_refresh_fails_with_non_refresh_token(
        self,
        client: AsyncClient,
        test_user: UserModel,
    ):
        """场景1: 使用非 refresh token 类型（如 access token）时返回 UnauthorizedError"""
        access_token = create_access_token(data={"sub": str(test_user.id)})

        response = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 401, f"期望401，实际{response.status_code}"
        data = response.json()
        assert data["code"] == "UNAUTHORIZED"
        assert "Invalid token type" in data["message"]

    @pytest.mark.asyncio
    async def test_refresh_fails_when_no_sub_in_token(self, client: AsyncClient):
        """场景2: Token 中无 sub 字段时返回 UnauthorizedError"""
        from app.core.config import get_settings

        settings = get_settings()
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        token = jwt.encode(
            {"exp": expire, "type": "refresh"},  # 缺少 sub
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        response = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401, f"期望401，实际{response.status_code}"
        data = response.json()
        assert data["code"] == "UNAUTHORIZED"
        assert "Invalid token payload" in data["message"]

    @pytest.mark.asyncio
    async def test_refresh_fails_with_invalid_user_id_format(self, client: AsyncClient):
        """场景3: Token 中包含无效的 user_id 格式时返回 UnauthorizedError"""
        from app.core.config import get_settings

        settings = get_settings()
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        token = jwt.encode(
            {"exp": expire, "type": "refresh", "sub": "invalid-uuid-format"},
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        response = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401, f"期望401，实际{response.status_code}"
        data = response.json()
        assert data["code"] == "UNAUTHORIZED"
        assert "Invalid user ID in token" in data["message"]

    @pytest.mark.asyncio
    async def test_refresh_fails_when_user_is_inactive(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        """场景4: 用户被停用时返回 UnauthorizedError"""
        unique_id = str(uuid.uuid4())[:8]
        email = f"inactive_refresh_{unique_id}@example.com"
        username = f"inactiverefresh_{unique_id}"

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(b"password123", salt).decode()

        inactive_user = UserModel(
            email=email,
            username=username,
            password_hash=password_hash,
            is_active=False,  # 被停用
            email_verified=True,
        )
        db_session.add(inactive_user)
        await db_session.flush()
        await db_session.refresh(inactive_user)
        refresh_token = create_refresh_token(data={"sub": str(inactive_user.id)})

        response = await client.post(
            f"{AUTH_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert response.status_code == 401, f"期望401，实际{response.status_code}"
        data = response.json()
        assert data["code"] == "UNAUTHORIZED"
        assert "User account is inactive" in data["message"]
