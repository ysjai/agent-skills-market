"""
Login Handler Integration Tests

Tests the handle_login function to cover:
- Successful login with valid credentials
- Login with non-existent email
- Login with incorrect password
"""

import bcrypt
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.handlers.login_handler import handle_login
from app.domain.exceptions import UnauthorizedError
from app.infra.persistence.models.user_model import UserModel
from app.infra.persistence.repositories.sql_user_repository import SqlUserRepository


@pytest_asyncio.fixture
async def test_user_with_password(db_session: AsyncSession) -> tuple[UserModel, str]:
    """Create a test user with known password."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    email = f"login_test_{unique_id}@example.com"
    username = f"loginuser_{unique_id}"
    password = "secure_password_123"

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode(), salt).decode()

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

    return user, password


class TestLoginHandler:
    """Login Handler integration tests."""

    @pytest.mark.asyncio
    async def test_should_successfully_login_with_valid_credentials(
        self,
        db_session: AsyncSession,
        test_user_with_password: tuple[UserModel, str],
    ):
        """Given valid email and password, when logging in, then user and tokens are returned."""
        # Given
        user_repo = SqlUserRepository(db_session)
        test_user, password = test_user_with_password

        # When
        result_user, access_token, refresh_token = await handle_login(
            email=test_user.email,
            password=password,
            user_repo=user_repo,
        )

        # Then
        assert result_user is not None
        assert str(result_user.email) == test_user.email
        assert result_user.id == test_user.id
        assert access_token is not None
        assert isinstance(access_token, str)
        assert len(access_token) > 0
        assert refresh_token is not None
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0

    @pytest.mark.asyncio
    async def test_should_raise_unauthorized_when_email_not_found(
        self,
        db_session: AsyncSession,
    ):
        """Given non-existent email, when logging in, then UnauthorizedError is raised."""
        # Given
        user_repo = SqlUserRepository(db_session)
        non_existent_email = "nonexistent@example.com"

        # When / Then
        with pytest.raises(UnauthorizedError) as exc_info:
            await handle_login(
                email=non_existent_email,
                password="any_password",
                user_repo=user_repo,
            )

        assert exc_info.value.code == "UNAUTHORIZED"
        assert "Incorrect email or password" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_should_raise_unauthorized_when_password_is_incorrect(
        self,
        db_session: AsyncSession,
        test_user_with_password: tuple[UserModel, str],
    ):
        """Given incorrect password, when logging in, then UnauthorizedError is raised."""
        # Given
        user_repo = SqlUserRepository(db_session)
        test_user, _ = test_user_with_password
        wrong_password = "wrong_password_123"

        # When / Then
        with pytest.raises(UnauthorizedError) as exc_info:
            await handle_login(
                email=test_user.email,
                password=wrong_password,
                user_repo=user_repo,
            )

        assert exc_info.value.code == "UNAUTHORIZED"
        assert "Incorrect email or password" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_should_raise_unauthorized_when_user_is_inactive(
        self,
        db_session: AsyncSession,
    ):
        """Given inactive user, when logging in, then UnauthorizedError is raised."""
        # Given
        user_repo = SqlUserRepository(db_session)
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        email = f"inactive_{unique_id}@example.com"
        username = f"inactiveuser_{unique_id}"
        password = "secure_password_123"

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        inactive_user = UserModel(
            email=email,
            username=username,
            password_hash=password_hash,
            is_active=False,  # User is inactive
            email_verified=True,
        )
        db_session.add(inactive_user)
        await db_session.flush()
        await db_session.refresh(inactive_user)

        # When / Then
        with pytest.raises(UnauthorizedError) as exc_info:
            await handle_login(
                email=email,
                password=password,
                user_repo=user_repo,
            )

        assert exc_info.value.code == "UNAUTHORIZED"
        assert "User account is inactive" in exc_info.value.message
