"""Authentication 单元测试套件。

本模块测试 app.core.auth 模块的 get_current_user FastAPI 依赖函数，
覆盖所有认证场景，包括：
- 无 Authorization Header
- 无效 JWT Token
- Token 中无 sub 字段
- Token 对应的用户不存在
- 用户 is_active=False
- 缺少 "Bearer " 前缀的 Token
- 有效 Token + 活跃用户

测试设计遵循 Given-When-Then 模式，使用 pytest-asyncio 测试异步函数，
使用 unittest.mock 创建 Mock 对象。
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError as JWTError

from src.core.auth import get_current_user
from src.domain.aggregates.user import User
from src.domain.value_objects.email import Email


class TestGetCurrentUserAuthenticationScenarios:
    """get_current_user 认证场景测试套件。"""

    @pytest.fixture
    def mock_db(self):
        """创建 Mock 的 AsyncSession。"""
        return MagicMock()

    @pytest.fixture
    def valid_user_id(self):
        """创建有效的用户 ID。"""
        return uuid.uuid4()

    @pytest.fixture
    def active_user(self, valid_user_id):
        """创建活跃的测试用户。"""
        return User(
            id=valid_user_id,
            email=Email("test@example.com"),
            username="testuser",
            phone=None,
            password_hash="hashed_password",
            is_active=True,
            email_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @pytest.fixture
    def inactive_user(self, valid_user_id):
        """创建非活跃的测试用户。"""
        return User(
            id=valid_user_id,
            email=Email("inactive@example.com"),
            username="inactiveuser",
            phone=None,
            password_hash="hashed_password",
            is_active=False,
            email_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    async def should_return_401_when_no_authorization_header(self, mock_db):
        """测试：无 Authorization Header → 返回 401。

        Given: 没有提供 authorization header
        When: 调用 get_current_user
        Then: 抛出 HTTPException，状态码 401，detail "Not authenticated"
        """
        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=mock_db, authorization=None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in str(exc_info.value.detail)

    async def should_return_401_when_invalid_jwt_token(self, mock_db):
        """测试：无效 JWT Token → 返回 401。

        Given: 提供了无效的 JWT token
        When: 调用 get_current_user
        Then: 抛出 HTTPException，状态码 401，detail "Invalid authentication credentials"
        """
        # Given
        invalid_token = "invalid_token"

        with patch("app.core.auth.verify_token") as mock_verify:
            mock_verify.side_effect = JWTError("Invalid token signature")

            # When / Then
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db=mock_db, authorization=f"Bearer {invalid_token}")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid authentication credentials" in str(exc_info.value.detail)

    async def should_return_401_when_token_has_no_sub_field(self, mock_db):
        """测试：Token 中无 sub 字段 → 返回 401。

        Given: JWT token 中没有 sub 字段
        When: 调用 get_current_user
        Then: 抛出 HTTPException，状态码 401，detail "Invalid token payload"
        """
        # Given
        token_without_sub = "valid_token_but_no_sub"
        payload_without_sub = {"exp": 1234567890, "type": "access"}

        with patch("app.core.auth.verify_token") as mock_verify:
            mock_verify.return_value = payload_without_sub

            # When / Then
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db=mock_db, authorization=f"Bearer {token_without_sub}")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token payload" in str(exc_info.value.detail)

    async def should_return_401_when_user_not_found(self, mock_db, valid_user_id):
        """测试：Token 对应的用户不存在 → 返回 401。

        Given: JWT token 有效且有 sub 字段，但用户不存在
        When: 调用 get_current_user
        Then: 抛出 HTTPException，状态码 401，detail "User not found"
        """
        # Given
        valid_token = "valid_token_with_user_id"
        payload = {"sub": str(valid_user_id), "exp": 1234567890, "type": "access"}

        with patch("app.core.auth.verify_token") as mock_verify:
            mock_verify.return_value = payload

            with patch("app.core.auth.user") as mock_user_crud:
                mock_user_crud.get = AsyncMock(return_value=None)

                # When / Then
                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(db=mock_db, authorization=f"Bearer {valid_token}")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "User not found" in str(exc_info.value.detail)

    async def should_return_401_when_user_is_inactive(self, mock_db, valid_user_id, inactive_user):
        """测试：用户 is_active=False → 返回 401。

        Given: JWT token 有效且用户存在，但用户 is_active=False
        When: 调用 get_current_user
        Then: 抛出 HTTPException，状态码 401，detail "Inactive user"
        """
        # Given
        valid_token = "valid_token_with_inactive_user"
        payload = {"sub": str(valid_user_id), "exp": 1234567890, "type": "access"}

        with patch("app.core.auth.verify_token") as mock_verify:
            mock_verify.return_value = payload

            with patch("app.core.auth.user") as mock_user_crud:
                mock_user_crud.get = AsyncMock(return_value=inactive_user)

                # When / Then
                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(db=mock_db, authorization=f"Bearer {valid_token}")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Inactive user" in str(exc_info.value.detail)

    async def should_parse_token_without_bearer_prefix(self, mock_db, valid_user_id, active_user):
        """测试：缺少 "Bearer " 前缀的 Token → 正常解析。

        Given: Token 没有 "Bearer " 前缀
        When: 调用 get_current_user
        Then: 正常解析 Token 并返回 User 对象
        """
        # Given
        raw_token = "raw_token_without_bearer_prefix"
        payload = {"sub": str(valid_user_id), "exp": 1234567890, "type": "access"}

        with patch("app.core.auth.verify_token") as mock_verify:
            mock_verify.return_value = payload

            with patch("app.core.auth.user") as mock_user_crud:
                mock_user_crud.get = AsyncMock(return_value=active_user)

                # When
                result = await get_current_user(db=mock_db, authorization=raw_token)

        # Then
        assert result == active_user
        mock_verify.assert_called_once_with(raw_token)

    async def should_return_user_when_valid_token_and_active_user(
        self, mock_db, valid_user_id, active_user
    ):
        """测试：有效 Token + 活跃用户 → 返回 User 对象。

        Given: 有效的 JWT token 且用户存在且活跃
        When: 调用 get_current_user
        Then: 返回 User 对象
        """
        # Given
        valid_token = "valid_token"
        payload = {"sub": str(valid_user_id), "exp": 1234567890, "type": "access"}

        with patch("app.core.auth.verify_token") as mock_verify:
            mock_verify.return_value = payload

            with patch("app.core.auth.user") as mock_user_crud:
                mock_user_crud.get = AsyncMock(return_value=active_user)

                # When
                result = await get_current_user(db=mock_db, authorization=f"Bearer {valid_token}")

        # Then
        assert result == active_user
        assert result.id == valid_user_id
        assert result.is_active is True
        mock_verify.assert_called_once_with(valid_token)
        mock_user_crud.get.assert_called_once_with(mock_db, id=str(valid_user_id))


class TestGetCurrentUserEdgeCases:
    """get_current_user 边界情况测试套件。"""

    @pytest.fixture
    def mock_db(self):
        """创建 Mock 的 AsyncSession。"""
        return MagicMock()

    async def should_handle_empty_authorization_header(self, mock_db):
        """测试：空 Authorization Header → 返回 401。

        Given: Authorization header 为空字符串
        When: 调用 get_current_user
        Then: 抛出 HTTPException，状态码 401
        """
        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=mock_db, authorization="")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def should_strip_bearer_prefix_correctly(self, mock_db):
        """测试：正确去除 "Bearer " 前缀。

        Given: Token 带有 "Bearer " 前缀
        When: 调用 get_current_user
        Then: verify_token 接收到去除前缀后的 token
        """
        # Given
        token = "actual_token_value"
        authorization = f"Bearer {token}"
        valid_user_id = uuid.uuid4()
        payload = {"sub": str(valid_user_id), "exp": 1234567890, "type": "access"}

        with patch("app.core.auth.verify_token") as mock_verify:
            mock_verify.return_value = payload

            with patch("app.core.auth.user") as mock_user_crud:
                mock_user_crud.get = AsyncMock(return_value=None)

                try:
                    await get_current_user(db=mock_db, authorization=authorization)
                except HTTPException:
                    pass  # 我们只需要验证 verify_token 被正确调用

        # Then
        mock_verify.assert_called_once_with(token)

    async def should_include_www_authenticate_header_for_auth_failures(self, mock_db):
        """测试：认证失败时包含 WWW-Authenticate Header。

        Given: 没有提供 authorization header
        When: 调用 get_current_user
        Then: HTTPException 包含 WWW-Authenticate header
        """
        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=mock_db, authorization=None)

        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    async def should_include_www_authenticate_header_for_invalid_token(self, mock_db):
        """测试：无效 token 时包含 WWW-Authenticate Header。

        Given: 提供了无效的 JWT token
        When: 调用 get_current_user
        Then: HTTPException 包含 WWW-Authenticate header
        """
        # Given
        invalid_token = "invalid_token"

        with patch("app.core.auth.verify_token") as mock_verify:
            mock_verify.side_effect = JWTError("Invalid token")

            # When / Then
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db=mock_db, authorization=f"Bearer {invalid_token}")

        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


class TestGetCurrentUserTokenVariations:
    """get_current_user Token 变体测试套件。"""

    @pytest.fixture
    def mock_db(self):
        """创建 Mock 的 AsyncSession。"""
        return MagicMock()

    @pytest.fixture
    def valid_user(self):
        """创建有效的测试用户。"""
        return User(
            id=uuid.uuid4(),
            email=Email("test@example.com"),
            username="testuser",
            phone=None,
            password_hash="hashed_password",
            is_active=True,
            email_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @pytest.mark.parametrize(
        "authorization_header",
        [
            "token_without_bearer",
            "Basic token_value",
            "Token some_value",
        ],
    )
    async def should_accept_various_token_prefixes(self, mock_db, valid_user, authorization_header):
        """测试：接受各种没有 "Bearer " 前缀的 token 格式。

        Given: Token 没有 "Bearer " 前缀
        When: 调用 get_current_user
        Then: 整个字符串作为 token 被解析
        """
        # Given
        valid_user_id = valid_user.id
        payload = {"sub": str(valid_user_id), "exp": 1234567890, "type": "access"}

        with patch("app.core.auth.verify_token") as mock_verify:
            mock_verify.return_value = payload

            with patch("app.core.auth.user") as mock_user_crud:
                mock_user_crud.get = AsyncMock(return_value=valid_user)

                # When
                result = await get_current_user(db=mock_db, authorization=authorization_header)

        # Then
        assert result == valid_user
        mock_verify.assert_called_once_with(authorization_header)

    async def should_handle_whitespace_only_authorization(self, mock_db):
        """测试：仅包含空白的 Authorization → 返回 401。

        Given: Authorization header 只包含空白字符
        When: 调用 get_current_user
        Then: 抛出 HTTPException
        """
        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=mock_db, authorization="   ")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def should_handle_bearer_with_empty_token(self, mock_db):
        """测试："Bearer " 后没有 token → 返回 401。

        Given: Authorization header 只有 "Bearer " 没有实际 token
        When: 调用 get_current_user
        Then: 抛出 HTTPException
        """
        # Given
        with patch("app.core.auth.verify_token") as mock_verify:
            mock_verify.side_effect = JWTError("Empty token")

            # When / Then
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db=mock_db, authorization="Bearer ")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCurrentUserLogging:
    """get_current_user 日志记录测试套件。"""

    @pytest.fixture
    def mock_db(self):
        """创建 Mock 的 AsyncSession。"""
        return MagicMock()

    async def should_log_warning_when_jwt_verification_fails(self, mock_db, caplog):
        """测试：JWT 验证失败时记录警告日志。

        Given: JWT token 验证失败
        When: 调用 get_current_user
        Then: 记录警告日志包含 JWT 错误信息
        """
        # Given
        import logging

        # 设置日志级别为 WARNING
        with caplog.at_level(logging.WARNING, logger="app.core.auth"):
            invalid_token = "invalid_token"

            with patch("app.core.auth.verify_token") as mock_verify:
                mock_verify.side_effect = JWTError("Invalid signature")

                # When
                with pytest.raises(HTTPException):
                    await get_current_user(db=mock_db, authorization=f"Bearer {invalid_token}")

        # Then
        assert "JWT verification failed" in caplog.text
        assert "Invalid signature" in caplog.text
