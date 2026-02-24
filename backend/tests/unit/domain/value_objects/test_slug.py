"""Slug Value Object 单元测试套件。

本模块测试 Slug 值对象的所有功能，包括：
- 有效 slug 创建
- 无效 slug 验证
- from_name 工厂方法
- 相等性比较

测试设计遵循 Given-When-Then 模式，并使用 pytest.mark.parametrize 减少重复代码。
"""

import pytest

from app.domain.exceptions import ValidationError
from app.domain.value_objects.slug import Slug


class TestValidSlugCreation:
    """1.1.1 有效 Slug 创建测试场景。"""

    def should_create_slug_successfully_with_standard_format(self):
        """测试：使用标准格式创建 Slug。"""
        # Given / When
        slug = Slug("my-test-slug")

        # Then
        assert slug.value == "my-test-slug"

    def should_normalize_uppercase_to_lowercase(self):
        """测试：使用大写字母创建 Slug 会自动转小写。

        注意：当前实现有 bug，大写字母会在验证阶段失败。
        期望行为：Slug("My-Test-Slug").value == "my-test-slug"
        实际行为：抛出 ValidationError
        """
        # Given / When
        slug = Slug("My-Test-Slug")

        # Then
        assert slug.value == "my-test-slug"

    def should_create_slug_with_single_character(self):
        """测试：使用单字符创建 Slug。"""
        # Given / When
        slug = Slug("a")

        # Then
        assert slug.value == "a"

    def should_create_slug_with_pure_numbers(self):
        """测试：使用纯数字创建 Slug。"""
        # Given / When
        slug = Slug("123")

        # Then
        assert slug.value == "123"

    def should_create_slug_with_maximum_length(self):
        """测试：使用最大长度（128字符）创建 Slug。"""
        # Given
        long_slug = "a" * 128

        # When
        slug = Slug(long_slug)

        # Then
        assert slug.value == long_slug
        assert len(slug.value) == 128


class TestInvalidSlugValidation:
    """1.1.2 无效 Slug 验证测试场景。"""

    def should_raise_validation_error_when_given_empty_string(self):
        """测试：使用空字符串创建 Slug 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug("")

        assert "Slug cannot be empty" in str(exc_info.value)

    def should_raise_validation_error_when_given_whitespace_only(self):
        """测试：使用空格创建 Slug 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug("   ")

        assert "only lowercase letters, numbers, and hyphens" in str(exc_info.value)

    def should_raise_validation_error_when_given_underscore(self):
        """测试：使用下划线创建 Slug 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug("my_test_slug")

        assert "only lowercase letters, numbers, and hyphens" in str(exc_info.value)

    def should_raise_validation_error_when_given_space(self):
        """测试：使用空格创建 Slug 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug("my test slug")

        assert "only lowercase letters, numbers, and hyphens" in str(exc_info.value)

    def should_raise_validation_error_when_given_special_characters(self):
        """测试：使用特殊字符创建 Slug 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug("test@slug!")

        assert "only lowercase letters, numbers, and hyphens" in str(exc_info.value)

    def should_raise_validation_error_when_starting_with_hyphen(self):
        """测试：使用连字符开头创建 Slug 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug("-test-slug")

        assert "only lowercase letters, numbers, and hyphens" in str(exc_info.value)

    def should_raise_validation_error_when_ending_with_hyphen(self):
        """测试：使用连字符结尾创建 Slug 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug("test-slug-")

        assert "only lowercase letters, numbers, and hyphens" in str(exc_info.value)

    def should_raise_validation_error_when_given_consecutive_hyphens(self):
        """测试：使用连续连字符创建 Slug 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug("test--slug")

        assert "only lowercase letters, numbers, and hyphens" in str(exc_info.value)

    def should_raise_validation_error_when_exceeding_max_length(self):
        """测试：使用超长字符串创建 Slug 应该抛出 ValidationError。"""
        # Given
        too_long_slug = "a" * 129

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug(too_long_slug)

        assert "cannot exceed 128 characters" in str(exc_info.value)

    def should_raise_validation_error_when_given_single_hyphen_only(self):
        """测试：使用单个连字符创建 Slug 应该抛出 ValidationError（边界情况）。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug("-")

        assert "only lowercase letters, numbers, and hyphens" in str(exc_info.value)


class TestFromNameFactory:
    """1.1.3 from_name 工厂方法测试场景。"""

    def should_generate_slug_from_simple_name(self):
        """测试：从简单名称生成 Slug。"""
        # Given / When
        slug = Slug.from_name("My Test Skill")

        # Then
        assert slug.value == "my-test-skill"

    def should_generate_slug_from_name_with_special_characters(self):
        """测试：从带特殊字符的名称生成 Slug（移除特殊字符）。"""
        # Given / When
        slug = Slug.from_name("Skill @ Home #1!")

        # Then
        assert slug.value == "skill-home-1"

    def should_normalize_consecutive_whitespace_to_single_hyphen(self):
        """测试：从连续空格名称生成 Slug（合并为单个连字符）。"""
        # Given / When
        slug = Slug.from_name("My   Skill")

        # Then
        assert slug.value == "my-skill"

    def should_normalize_hyphens_and_spaces_correctly(self):
        """测试：从带连字符和空格的名称生成 Slug。"""
        # Given / When
        slug = Slug.from_name("My - Test - Skill")

        # Then
        assert slug.value == "my-test-skill"

    def should_raise_validation_error_when_given_empty_name(self):
        """测试：从空名称生成 Slug 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug.from_name("")

        assert "Cannot generate slug from empty name" in str(exc_info.value)

    def should_raise_validation_error_when_name_contains_only_special_characters(self):
        """测试：从仅含特殊字符的名称生成 Slug 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug.from_name("@#$%")

        assert "Cannot generate slug from empty name" in str(exc_info.value)

    def should_raise_validation_error_when_name_contains_only_whitespace(self):
        """测试：从纯空格名称生成 Slug 应该抛出 ValidationError（边界情况）。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Slug.from_name("   ")

        assert "Cannot generate slug from empty name" in str(exc_info.value)


class TestSlugEquality:
    """1.1.4 相等性比较测试场景。"""

    def should_be_equal_when_slugs_have_same_value(self):
        """测试：相同值的 Slug 应该相等。"""
        # Given
        slug1 = Slug("test-slug")
        slug2 = Slug("test-slug")

        # When / Then
        assert slug1 == slug2
        assert hash(slug1) == hash(slug2)

    def should_not_be_equal_when_slugs_have_different_values(self):
        """测试：不同值的 Slug 不应该相等。"""
        # Given
        slug1 = Slug("test-slug-1")
        slug2 = Slug("test-slug-2")

        # When / Then
        assert slug1 != slug2

    def should_not_be_equal_when_comparing_with_string(self):
        """测试：Slug 与字符串比较应该返回 False（类型不同）。"""
        # Given
        slug = Slug("test-slug")

        # When / Then
        assert slug != "test-slug"
