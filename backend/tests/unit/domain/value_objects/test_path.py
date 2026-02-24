"""Path Value Object 单元测试套件。

本模块测试 Path 值对象的所有功能，包括：
- 有效路径创建
- 无效路径验证（路径遍历攻击防护）
- 路径操作（扩展名、文件名、父目录等）
- 相等性比较

测试设计遵循 Given-When-Then 模式，并使用 pytest.mark.parametrize 减少重复代码。
"""

import pytest

from app.domain.exceptions import ValidationError
from app.domain.value_objects.path import Path


class TestValidPathCreation:
    """1.2.1 有效路径创建测试场景。"""

    @pytest.mark.parametrize(
        ("input_path", "expected_value", "is_file", "is_directory"),
        [
            ("file.txt", "file.txt", True, False),
            ("src/", "src/", False, True),
            ("src/components/Button.tsx", "src/components/Button.tsx", True, False),
            ("", "", False, False),
        ],
    )
    def should_create_path_successfully_when_given_valid_input(
        self,
        input_path: str,
        expected_value: str,
        is_file: bool,
        is_directory: bool,
    ):
        """测试：创建简单文件、目录、嵌套路径和空路径。"""
        # When
        path = Path(input_path)

        # Then
        assert path.value == expected_value
        assert path.is_file() == is_file
        assert path.is_directory() == is_directory

    def should_create_path_with_max_length(self):
        """测试：使用最大长度（512字符）创建路径。"""
        # Given
        long_path = "a" * 512

        # When
        path = Path(long_path)

        # Then
        assert path.value == long_path
        assert len(path.value) == 512

    @pytest.mark.parametrize(
        ("input_path", "expected_normalized"),
        [
            ("src//components///file.txt", "src/components/file.txt"),
            ("./src/file.txt", "src/file.txt"),
        ],
    )
    def should_normalize_path_when_given_excess_slashes_or_dot_prefix(
        self,
        input_path: str,
        expected_normalized: str,
    ):
        """测试：路径自动规范化（去除多余斜杠、处理点前缀）。"""
        # When
        path = Path(input_path)

        # Then
        assert path.value == expected_normalized


class TestInvalidPathValidation:
    """1.2.2 无效路径验证测试场景（路径遍历攻击防护）。"""

    def should_raise_validation_error_when_given_absolute_path(self):
        """测试：使用绝对路径创建 Path 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Path("/etc/passwd")

        assert "Path must be relative" in str(exc_info.value)

    def should_raise_validation_error_when_given_simple_traversal_sequence(self):
        """测试：使用路径遍历序列创建 Path 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Path("../secret.txt")

        assert "Path contains traversal sequences" in str(exc_info.value)

    def should_raise_validation_error_when_given_complex_traversal_sequence(self):
        """测试：使用复杂遍历序列创建 Path 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Path("src/../../../etc/passwd")

        assert "Path contains traversal sequences" in str(exc_info.value)

    def should_raise_validation_error_when_given_tilde_path(self):
        """测试：使用波浪号路径创建 Path 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Path("~/.bashrc")

        assert "Path contains traversal sequences" in str(exc_info.value)

    def should_raise_validation_error_when_given_traversal_in_middle_of_path(self):
        """测试：路径中间包含遍历序列应该抛出 ValidationError。

        验证：即使 os.path.normpath() 可以规范化路径，包含 .. 的输入也应被拒绝。
        """
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Path("foo/../secret.txt")

        assert "Path contains traversal sequences" in str(exc_info.value)

    def should_accept_path_with_single_dot(self):
        """测试：单独的点号路径应该被接受（表示当前目录）。"""
        # When
        path = Path(".")

        # Then
        assert path.value == "."

    def should_raise_validation_error_when_given_double_dot_only(self):
        """测试：单独的双点号路径应该被拒绝（表示父目录，构成遍历）。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Path("..")

        assert "Path contains traversal sequences" in str(exc_info.value)

    def should_accept_url_encoded_path_that_does_not_decode_to_traversal(self):
        """测试：Path 类接受 URL 编码但不解码的路径。

        注意：当前实现不 URL 解码输入，因此 %2e%2e%2f（解码后为 ../）
        被视为普通字符序列。这是实现限制，调用方应在创建 Path 前解码。
        """
        # When
        path = Path("%2e%2e%2fsecret.txt")

        # Then
        assert path.value == "%2e%2e%2fsecret.txt"

    def should_raise_validation_error_when_given_path_exceeding_max_length(self):
        """测试：使用超长路径创建 Path 应该抛出 ValidationError。"""
        # Given
        too_long_path = "a" * 513

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            Path(too_long_path)

        assert "cannot exceed 512 characters" in str(exc_info.value)

    def should_accept_path_with_null_byte_as_valid_input(self):
        """测试：Path 类接受包含 null 字节的路径。

        注意：当前实现不检查 null 字节，它们被视为普通字符。
        这是实现限制，调用方应在创建 Path 前清理输入。
        """
        # When
        path = Path("file.txt\x00.sh")

        # Then
        assert "\x00" in path.value


class TestPathOperations:
    """1.2.3 路径操作测试场景。"""

    # ========== 扩展名操作 ==========

    def should_return_extension_when_file_has_extension(self):
        """测试：获取文件扩展名。"""
        # Given
        path = Path("src/components/Button.tsx")

        # When / Then
        assert path.extension() == "tsx"
        assert path.has_extension() is True

    def should_return_none_when_file_has_no_extension(self):
        """测试：获取无扩展名文件的扩展名。"""
        # Given
        path = Path("Makefile")

        # When / Then
        assert path.extension() is None
        assert path.has_extension() is False

    def should_return_none_when_path_is_directory(self):
        """测试：获取目录的扩展名应该返回 None。"""
        # Given
        path = Path("src/")

        # When / Then
        assert path.extension() is None

    # ========== 文件名操作 ==========

    @pytest.mark.parametrize(
        ("input_path", "expected_filename"),
        [
            ("src/components/Button.tsx", "Button.tsx"),
            ("file.txt", "file.txt"),
            ("deep/nested/path/file.py", "file.py"),
        ],
    )
    def should_return_filename_when_given_valid_path(
        self,
        input_path: str,
        expected_filename: str,
    ):
        """测试：获取文件名（包括嵌套路径和根目录文件）。"""
        # Given
        path = Path(input_path)

        # When / Then
        assert path.filename() == expected_filename

    # ========== 父目录操作 ==========

    def should_return_parent_directory_when_given_nested_file_path(self):
        """测试：获取父目录。"""
        # Given
        path = Path("src/components/Button.tsx")

        # When
        parent = path.parent()

        # Then
        assert parent == Path("src/components")

    def should_return_grandparent_when_chaining_parent_calls(self):
        """测试：获取多级父目录。"""
        # Given
        path = Path("src/components/Button.tsx")

        # When
        grandparent = path.parent().parent()

        # Then
        assert grandparent == Path("src")

    def should_return_empty_path_when_parent_of_root_level_file(self):
        """测试：根目录级别文件的父目录应该是空路径。"""
        # Given
        path = Path("file.txt")

        # When
        parent = path.parent()

        # Then
        assert parent == Path("")

    def should_return_empty_path_when_parent_of_empty_path(self):
        """测试：空路径的父目录应该是空路径。"""
        # Given
        path = Path("")

        # When
        parent = path.parent()

        # Then
        assert parent == Path("")

    # ========== 路径连接操作 ==========

    def should_join_paths_when_using_join_method(self):
        """测试：使用 join 方法连接路径。"""
        # Given
        path = Path("src/")

        # When
        result = path.join("components")

        # Then
        assert result == Path("src/components")

    def should_join_paths_when_using_division_operator(self):
        """测试：使用 / 运算符连接路径。"""
        # Given
        path = Path("src/")

        # When
        result = path / "components" / "Button.tsx"

        # Then
        assert result == Path("src/components/Button.tsx")

    def should_join_with_empty_path_when_using_join_from_empty(self):
        """测试：从空路径开始使用 join 方法。"""
        # Given
        path = Path("")

        # When
        result = path.join("file.txt")

        # Then
        assert result == Path("file.txt")


class TestPathEquality:
    """1.2.4 相等性比较测试场景。"""

    def should_be_equal_when_paths_have_same_value(self):
        """测试：相同值的路径应该相等。"""
        # Given
        path1 = Path("src/file.txt")
        path2 = Path("src/file.txt")

        # When / Then
        assert path1 == path2
        assert hash(path1) == hash(path2)

    def should_be_equal_when_paths_are_normalized_to_same_value(self):
        """测试：规范化后相同的路径应该相等。"""
        # Given
        path1 = Path("src//file.txt")
        path2 = Path("src/file.txt")

        # When / Then
        assert path1 == path2
        assert hash(path1) == hash(path2)

    def should_not_be_equal_when_paths_have_different_values(self):
        """测试：不同值的路径不应该相等。"""
        # Given
        path1 = Path("src/file.txt")
        path2 = Path("src/other.txt")

        # When / Then
        assert path1 != path2

    def should_not_be_equal_when_comparing_with_non_path_object(self):
        """测试：与非 Path 对象比较应该返回 NotImplemented（由 Python 转换为 False）。"""
        # Given
        path = Path("src/file.txt")

        # When / Then
        assert path != "src/file.txt"
        assert path != 123
        assert path != None  # noqa: E711

    def should_have_consistent_string_representation(self):
        """测试：字符串表示应该与值一致。"""
        # Given
        path = Path("src/components/Button.tsx")

        # When / Then
        assert str(path) == "src/components/Button.tsx"
        assert str(path) == path.value
