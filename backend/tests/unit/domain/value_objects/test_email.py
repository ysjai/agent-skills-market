"""Email Value Object 单元测试套件。

本模块测试 Email 值对象的所有功能，包括：
- 有效邮箱创建
- 无效邮箱验证
- 邮箱解析（local_part 和 domain）
- 相等性比较
- 字符串表示

测试设计遵循 Given-When-Then 模式，并使用 pytest.mark.parametrize 减少重复代码。
"""

import pytest

from src.domain.exceptions import ValidationError
from src.domain.value_objects.email import Email


class TestValidEmailCreation:
    """1.3.1 有效邮箱创建测试场景。"""

    @pytest.mark.parametrize(
        "input_email",
        [
            "test@example.com",
            "test+tag@example.com",
            "test@mail.example.com",
            "test-user@example-site.com",
        ],
    )
    def should_create_email_successfully_with_valid_format(self, input_email: str):
        """测试：使用标准格式、带加号、带子域、带连字符创建邮箱。"""
        # When
        email = Email(input_email)

        # Then
        assert email.value == input_email

    def should_normalize_uppercase_to_lowercase(self):
        """测试：使用大写邮箱创建会自动转小写。"""
        # Given / When
        email = Email("Test@Example.COM")

        # Then
        assert email.value == "test@example.com"

    def should_trim_whitespace_from_input(self):
        """测试：自动去除首尾空格。"""
        # Given / When
        email = Email("  test@example.com  ")

        # Then
        assert email.value == "test@example.com"

    def should_create_email_with_maximum_length(self):
        """测试：使用最大长度（255字符）创建邮箱。"""
        # Given: 250 + @ + x.co = 255 字符
        local_part = "a" * 250
        long_email = f"{local_part}@x.co"

        # When
        email = Email(long_email)

        # Then
        assert email.value == long_email
        assert len(email.value) == 255


class TestInvalidEmailValidation:
    """1.3.2 无效邮箱验证测试场景。"""

    def should_raise_validation_error_when_given_empty_string(self):
        """测试：使用空字符串创建 Email 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Email("")

        assert "Email cannot be empty" in str(exc_info.value)

    def should_raise_validation_error_when_given_invalid_format(self):
        """测试：使用无效格式创建 Email 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Email("not-an-email")

        assert "Invalid email format" in str(exc_info.value)

    def should_raise_validation_error_when_missing_at_symbol(self):
        """测试：使用缺少 @ 的邮箱创建 Email 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Email("testexample.com")

        assert "Invalid email format" in str(exc_info.value)

    def should_raise_validation_error_when_missing_domain(self):
        """测试：使用缺少域名的邮箱创建 Email 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Email("test@")

        assert "Invalid email format" in str(exc_info.value)

    def should_raise_validation_error_when_missing_local_part(self):
        """测试：使用缺少用户名的邮箱创建 Email 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Email("@example.com")

        assert "Invalid email format" in str(exc_info.value)

    def should_raise_validation_error_when_given_whitespace_in_middle(self):
        """测试：使用带空格的邮箱创建 Email 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Email("test user@example.com")

        assert "Invalid email format" in str(exc_info.value)

    def should_raise_validation_error_when_exceeding_max_length(self):
        """测试：使用超长邮箱创建 Email 应该抛出 ValidationError。

        验证：总长度超过 255 字符应该被拒绝。
        """
        # Given: 249 + @ + example.com = 262 字符
        local_part = "a" * 249
        too_long_email = f"{local_part}@example.com"

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Email(too_long_email)

        assert "cannot exceed 255 characters" in str(exc_info.value)

    def should_raise_validation_error_when_given_multiple_at_symbols(self):
        """测试：使用多个 @ 的邮箱创建 Email 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Email("test@user@example.com")

        assert "Invalid email format" in str(exc_info.value)

    def should_raise_validation_error_when_given_invalid_characters(self):
        """测试：使用无效字符的邮箱创建 Email 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Email("test<user>@example.com")

        assert "Invalid email format" in str(exc_info.value)

    def should_raise_validation_error_when_domain_has_no_dot(self):
        """测试：domain 缺少点号应该抛出 ValidationError（边界场景）。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Email("test@nodot")

        assert "Invalid email format" in str(exc_info.value)


class TestEmailParsing:
    """1.3.3 邮箱解析测试场景。"""

    def should_return_local_part_when_accessing_local_part_property(self):
        """测试：获取本地部分（用户名）。"""
        # Given
        email = Email("test+tag@example.com")

        # When / Then
        assert email.local_part == "test+tag"

    def should_return_domain_when_accessing_domain_property(self):
        """测试：获取域名部分。"""
        # Given
        email = Email("test@mail.example.com")

        # When / Then
        assert email.domain == "mail.example.com"


class TestEmailEquality:
    """Email 相等性比较测试场景。"""

    def should_be_equal_when_emails_have_same_value(self):
        """测试：相同值的 Email 应该相等。"""
        # Given
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")

        # When / Then
        assert email1 == email2
        assert hash(email1) == hash(email2)

    def should_be_equal_when_emails_normalize_to_same_value(self):
        """测试：规范化后相同的 Email 应该相等。"""
        # Given
        email1 = Email("Test@Example.COM")
        email2 = Email("test@example.com")

        # When / Then
        assert email1 == email2
        assert hash(email1) == hash(email2)

    def should_not_be_equal_when_emails_have_different_values(self):
        """测试：不同值的 Email 不应该相等。"""
        # Given
        email1 = Email("test1@example.com")
        email2 = Email("test2@example.com")

        # When / Then
        assert email1 != email2

    def should_not_be_equal_when_comparing_with_non_email_object(self):
        """测试：与非 Email 对象比较应该返回 NotImplemented（由 Python 转换为 False）。"""
        # Given
        email = Email("test@example.com")

        # When / Then
        assert email != "test@example.com"
        assert email != 123
        assert email != None  # noqa: E711

    def should_have_consistent_string_representation(self):
        """测试：字符串表示应该与值一致。"""
        # Given
        email = Email("test@example.com")

        # When / Then
        assert str(email) == "test@example.com"
        assert str(email) == email.value


class TestEmailImmutability:
    """Email 不可变性测试场景。"""

    def should_be_immutable_frozen_dataclass(self):
        """测试：Email 是不可变的 frozen dataclass。"""
        # Given
        email = Email("test@example.com")

        # When / Then
        with pytest.raises(AttributeError):
            email.value = "other@example.com"

    def should_be_hashable_and_usable_as_dict_key(self):
        """测试：Email 是可哈希的，可用作字典键。"""
        # Given
        email = Email("test@example.com")

        # When
        email_dict = {email: "user_data"}

        # Then
        assert email_dict[email] == "user_data"
