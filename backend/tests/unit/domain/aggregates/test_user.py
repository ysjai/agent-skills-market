"""User Aggregate 单元测试套件。

本模块测试 User 聚合根的所有功能，包括：
- verify_email → email_verified=True
- deactivate → is_active=False
- activate → is_active=True
- change_password → password_hash 更新
- change_password 空值 → ValueError
- update_profile 更新 username
- is_authenticated → is_active && email_verified

测试设计遵循 Given-When-Then 模式。
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from src.domain.aggregates.user import User
from src.domain.value_objects.email import Email


class TestUserEmailVerification:
    """邮箱验证测试场景。"""

    def test_should_set_verified_when_verify_email_called_given_unverified_user(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            email_verified=False,
        )
        original_updated_at = user.updated_at

        # When
        user.verify_email()

        # Then
        assert user.email_verified is True
        assert user.updated_at >= original_updated_at

    def test_should_not_change_when_verify_email_called_given_already_verified(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            email_verified=True,
        )
        original_updated_at = user.updated_at

        # When
        user.verify_email()

        # Then - 不应抛出异常
        assert user.email_verified is True
        # updated_at 应该更新（因为 _touch 被调用）
        assert user.updated_at >= original_updated_at


class TestUserActivation:
    """账户激活/停用测试场景。"""

    def test_should_set_inactive_when_deactivate_called_given_active_user(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            is_active=True,
        )
        original_updated_at = user.updated_at

        # When
        user.deactivate()

        # Then
        assert user.is_active is False
        assert user.updated_at >= original_updated_at

    def test_should_not_change_when_deactivate_called_given_already_inactive(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            is_active=False,
        )
        original_updated_at = user.updated_at

        # When
        user.deactivate()

        # Then - 不应抛出异常
        assert user.is_active is False
        assert user.updated_at >= original_updated_at

    def test_should_set_active_when_activate_called_given_inactive_user(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            is_active=False,
        )
        original_updated_at = user.updated_at

        # When
        user.activate()

        # Then
        assert user.is_active is True
        assert user.updated_at >= original_updated_at

    def test_should_not_change_when_activate_called_given_already_active(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            is_active=True,
        )
        original_updated_at = user.updated_at

        # When
        user.activate()

        # Then - 不应抛出异常
        assert user.is_active is True
        assert user.updated_at >= original_updated_at


class TestUserPasswordChange:
    """密码修改测试场景。"""

    def test_should_update_hash_when_change_password_called_given_valid_password(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            password_hash="old_hash",
        )
        original_updated_at = user.updated_at

        # When
        user.change_password("new_hash_123")

        # Then
        assert user.password_hash == "new_hash_123"
        assert user.updated_at >= original_updated_at

    def test_should_raise_error_when_change_password_called_given_empty_password(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            password_hash="old_hash",
        )

        # When / Then
        with pytest.raises(ValueError) as exc_info:
            user.change_password("")

        assert "cannot be empty" in str(exc_info.value)

    def test_should_accept_whitespace_when_change_password_called_given_whitespace_only(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            password_hash="old_hash",
        )

        # When - 空白字符不被视为空
        user.change_password("   ")

        # Then - 被接受（注意：实际应用中可能需要更严格的验证）
        assert user.password_hash == "   "


class TestUserProfileUpdate:
    """资料更新测试场景。"""

    def test_should_update_username_when_update_profile_called_given_valid_name(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="oldname",
        )
        original_updated_at = user.updated_at

        # When
        user.update_profile(username="newname")

        # Then
        assert user.username == "newname"
        assert user.updated_at >= original_updated_at

    def test_should_strip_whitespace_when_update_profile_called_given_username_with_spaces(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="oldname",
        )

        # When
        user.update_profile(username="  newname  ")

        # Then
        assert user.username == "newname"

    def test_should_raise_error_when_update_profile_called_given_empty_username(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="oldname",
        )

        # When / Then
        with pytest.raises(ValueError) as exc_info:
            user.update_profile(username="")

        assert "cannot be empty" in str(exc_info.value)

    def test_should_raise_error_when_update_profile_called_given_whitespace_only_username(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="oldname",
        )

        # When / Then
        with pytest.raises(ValueError) as exc_info:
            user.update_profile(username="   ")

        assert "cannot be empty" in str(exc_info.value)

    def test_should_update_phone_when_update_profile_called_given_valid_phone(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            phone=None,
        )

        # When
        user.update_profile(phone="1234567890")

        # Then
        assert user.phone == "1234567890"

    def test_should_strip_whitespace_when_update_profile_called_given_phone_with_spaces(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            phone=None,
        )

        # When
        user.update_profile(phone="  1234567890  ")

        # Then
        assert user.phone == "1234567890"

    def test_should_set_none_when_update_profile_called_given_none_phone(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            phone="1234567890",
        )

        # When
        user.update_profile(phone=None)

        # Then
        assert user.phone is None

    def test_should_set_none_when_update_profile_called_given_empty_phone(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            phone="1234567890",
        )

        # When
        user.update_profile(phone="")

        # Then - 空字符串会被视为 falsy，结果设为 None
        assert user.phone is None

    def test_should_update_both_when_update_profile_called_given_username_and_phone(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="oldname",
            phone=None,
        )

        # When
        user.update_profile(username="newname", phone="1234567890")

        # Then
        assert user.username == "newname"
        assert user.phone == "1234567890"

    def test_should_update_timestamp_when_update_profile_called_given_no_changes(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            phone="1234567890",
        )
        original_updated_at = user.updated_at

        # When
        user.update_profile()

        # Then - phone 会被设为 None（因为实现中 phone.strip() if phone else None）
        # 但 updated_at 仍会更新
        assert user.updated_at >= original_updated_at


class TestUserAuthenticationStatus:
    """认证状态检查测试场景。"""

    def test_should_return_true_when_is_authenticated_called_given_active_and_verified(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            is_active=True,
            email_verified=True,
        )

        # When / Then
        assert user.is_authenticated() is True

    def test_should_return_false_when_is_authenticated_called_given_inactive_and_verified(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            is_active=False,
            email_verified=True,
        )

        # When / Then
        assert user.is_authenticated() is False

    def test_should_return_false_when_is_authenticated_called_given_active_and_unverified(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            is_active=True,
            email_verified=False,
        )

        # When / Then
        assert user.is_authenticated() is False

    def test_should_return_false_when_is_authenticated_called_given_inactive_and_unverified(self):
        # Given
        user = User(
            email=Email("test@example.com"),
            username="testuser",
            is_active=False,
            email_verified=False,
        )

        # When / Then
        assert user.is_authenticated() is False


class TestUserCreation:
    """User 创建测试场景。"""

    def test_should_create_with_defaults_when_instantiate_given_minimal_values(self):
        # When
        user = User(email=Email("test@example.com"))

        # Then
        assert isinstance(user.id, UUID)
        assert isinstance(user.email, Email)
        assert user.username == ""
        assert user.phone is None
        assert user.password_hash == ""
        assert user.is_active is True
        assert user.email_verified is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_should_create_with_custom_values_when_instantiate_given_full_args(self):
        # Given
        user_id = uuid4()
        created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        updated_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # When
        user = User(
            id=user_id,
            email=Email("custom@example.com"),
            username="customuser",
            phone="1234567890",
            password_hash="hashed_password",
            is_active=False,
            email_verified=True,
            created_at=created_at,
            updated_at=updated_at,
        )

        # Then
        assert user.id == user_id
        assert str(user.email) == "custom@example.com"
        assert user.username == "customuser"
        assert user.phone == "1234567890"
        assert user.password_hash == "hashed_password"
        assert user.is_active is False
        assert user.email_verified is True
        assert user.created_at == created_at
        assert user.updated_at == updated_at


class TestUserWorkflow:
    """完整工作流测试场景。"""

    def test_should_complete_full_lifecycle_when_all_operations_called_given_new_user(self):
        # Given - 新注册用户
        user = User(
            email=Email("newuser@example.com"),
            username="newuser",
            password_hash="initial_hash",
        )

        # Then - 初始状态
        assert user.is_active is True
        assert user.email_verified is False
        assert user.is_authenticated() is False

        # When - 验证邮箱
        user.verify_email()

        # Then
        assert user.email_verified is True
        assert user.is_authenticated() is True

        # When - 更新资料
        user.update_profile(username="updateduser", phone="9876543210")

        # Then
        assert user.username == "updateduser"
        assert user.phone == "9876543210"

        # When - 修改密码
        user.change_password("new_password_hash")

        # Then
        assert user.password_hash == "new_password_hash"

        # When - 停用账户
        user.deactivate()

        # Then
        assert user.is_active is False
        assert user.is_authenticated() is False

        # When - 重新激活账户
        user.activate()

        # Then
        assert user.is_active is True
        # 邮箱已验证，所以应该可以认证
        assert user.is_authenticated() is True
