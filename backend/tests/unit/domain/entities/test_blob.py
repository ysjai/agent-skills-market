"""Blob Entity 单元测试套件。

本模块测试 Blob 实体的所有功能，包括：
- __post_init__ 计算 size
- __post_init__ 计算 checksum
- create 空内容 → ValueError
- compress 已压缩 → 直接返回
- decompress 未压缩 → 直接返回
- increment_reference → +1
- decrement_reference → -1 (最小0)
- is_orphaned → reference_count == 0

测试设计遵循 Given-When-Then 模式。
"""

import hashlib
from datetime import datetime
from uuid import UUID, uuid4

import pytest

from src.domain.entities.blob import Blob

class TestBlobPostInit:
    """__post_init__ 计算 size 和 checksum 测试场景。"""

    def test_should_calculate_size_when_post_init_given_valid_content(self):
        # Given
        content = b"Hello, World!"

        # When
        blob = Blob(content=content)

        # Then
        assert blob.size == len(content)

    def test_should_calculate_checksum_when_post_init_given_valid_content(self):
        # Given
        content = b"Hello, World!"
        expected_checksum = hashlib.sha256(content).hexdigest()

        # When
        blob = Blob(content=content)

        # Then
        assert blob.checksum == expected_checksum

    def test_should_preserve_provided_size_when_post_init_given_size_parameter(self):
        # Given
        content = b"Hello, World!"
        provided_size = 999

        # When
        blob = Blob(content=content, size=provided_size)

        # Then - 如果 size 已提供，不应重新计算
        assert blob.size == provided_size

    def test_should_preserve_provided_checksum_when_post_init_given_checksum_parameter(self):
        # Given
        content = b"Hello, World!"
        provided_checksum = "abc123"

        # When
        blob = Blob(content=content, checksum=provided_checksum)

        # Then - 如果 checksum 已提供，不应重新计算
        assert blob.checksum == provided_checksum

    def test_should_set_zero_size_when_post_init_given_empty_content(self):
        # When
        blob = Blob(content=b"")

        # Then
        assert blob.size == 0

    def test_should_set_empty_checksum_when_post_init_given_empty_content(self):
        # When
        blob = Blob(content=b"")

        # Then
        assert blob.checksum == ""

class TestBlobCreate:
    """create 工厂方法测试场景。"""

    def test_should_create_successfully_when_factory_called_given_valid_content(self):
        # Given
        content = b"Test content"
        expected_checksum = hashlib.sha256(content).hexdigest()

        # When
        blob = Blob.create(content=content)

        # Then
        assert isinstance(blob.id, UUID)
        assert blob.content == content
        assert blob.checksum == expected_checksum
        assert blob.size == len(content)
        assert blob.compressed is False
        assert blob.reference_count == 0
        assert isinstance(blob.created_at, datetime)

    def test_should_create_compressed_when_factory_called_given_compressed_flag(self):
        # Given
        content = b"Test content"

        # When
        blob = Blob.create(content=content, compressed=True)

        # Then
        assert blob.compressed is True

    def test_should_raise_value_error_when_create_given_empty_content(self):
        # When / Then
        with pytest.raises(ValueError) as exc_info:
            Blob.create(content=b"")

        assert "cannot be empty" in str(exc_info.value)

class TestBlobCompress:
    """compress 方法测试场景。"""

    def test_should_compress_when_called_given_uncompressed_blob(self):
        # Given - 使用较大的重复内容确保压缩有效
        content = b"A" * 1000
        blob = Blob.create(content=content)
        original_size = blob.size

        # When
        blob.compress()

        # Then
        assert blob.compressed is True
        assert blob.size < original_size  # 压缩后应该更小
        assert blob.get_raw_content() == content

    def test_should_return_early_when_compress_given_already_compressed(self):
        # Given
        content = b"Test content"
        blob = Blob.create(content=content)
        blob.compress()
        compressed_content = blob.content
        compressed_size = blob.size

        # When - 再次压缩
        blob.compress()

        # Then - 内容不应改变
        assert blob.compressed is True
        assert blob.content == compressed_content
        assert blob.size == compressed_size

class TestBlobDecompress:
    """decompress 方法测试场景。"""

    def test_should_decompress_when_called_given_compressed_blob(self):
        # Given - 使用较大的重复内容确保压缩有效
        original_content = b"A" * 1000
        blob = Blob.create(content=original_content)
        blob.compress()
        compressed_size = blob.size

        # When
        blob.decompress()

        # Then
        assert blob.compressed is False
        assert blob.content == original_content
        assert blob.size == len(original_content)
        assert blob.size > compressed_size  # 解压后应该更大

    def test_should_return_early_when_decompress_given_uncompressed(self):
        # Given
        content = b"Test content"
        blob = Blob.create(content=content)

        # When - 解压未压缩的 blob
        blob.decompress()

        # Then - 内容不应改变
        assert blob.compressed is False
        assert blob.content == content
        assert blob.size == len(content)

class TestBlobGetRawContent:
    """get_raw_content 方法测试场景。"""

    def test_should_return_content_when_get_raw_given_uncompressed(self):
        # Given
        content = b"Uncompressed content"
        blob = Blob.create(content=content)

        # When
        result = blob.get_raw_content()

        # Then
        assert result == content

    def test_should_return_decompressed_when_get_raw_given_compressed(self):
        # Given
        content = b"Content to be compressed"
        blob = Blob.create(content=content)
        blob.compress()

        # When
        result = blob.get_raw_content()

        # Then
        assert result == content

    def test_should_return_original_when_get_raw_given_invalid_compressed(self):
        # Given - 创建一个标记为压缩但实际内容无效的 blob
        blob = Blob(
            content=b"invalid compressed data",
            compressed=True,
            size=len(b"invalid compressed data"),
        )

        # When
        result = blob.get_raw_content()

        # Then - 应该返回原始内容（解压失败时）
        assert result == b"invalid compressed data"

class TestBlobReferenceCount:
    """引用计数管理测试场景。"""

    def test_should_increase_count_when_increment_called_given_valid_blob(self):
        # Given
        blob = Blob.create(content=b"Test")
        assert blob.reference_count == 0

        # When
        blob.increment_reference()

        # Then
        assert blob.reference_count == 1

        # When - 再次递增
        blob.increment_reference()

        # Then
        assert blob.reference_count == 2

    def test_should_decrease_count_when_decrement_called_given_positive_count(self):
        # Given
        blob = Blob.create(content=b"Test")
        blob.reference_count = 3

        # When
        blob.decrement_reference()

        # Then
        assert blob.reference_count == 2

    def test_should_stop_at_zero_when_decrement_called_given_count_one(self):
        # Given
        blob = Blob.create(content=b"Test")
        blob.reference_count = 1

        # When
        blob.decrement_reference()

        # Then
        assert blob.reference_count == 0

        # When - 再次递减（应该保持在 0）
        blob.decrement_reference()

        # Then
        assert blob.reference_count == 0

    def test_should_remain_zero_when_decrement_called_given_count_zero(self):
        # Given
        blob = Blob.create(content=b"Test")
        assert blob.reference_count == 0

        # When
        blob.decrement_reference()

        # Then
        assert blob.reference_count == 0

class TestBlobOrphanStatus:
    """孤儿状态检查测试场景。"""

    def test_should_return_true_when_is_orphaned_called_given_zero_count(self):
        # Given
        blob = Blob.create(content=b"Test")
        assert blob.reference_count == 0

        # When / Then
        assert blob.is_orphaned() is True

    def test_should_return_false_when_is_orphaned_called_given_positive_count(self):
        # Given
        blob = Blob.create(content=b"Test")
        blob.increment_reference()

        # When / Then
        assert blob.is_orphaned() is False

class TestBlobEmptyStatus:
    """空内容检查测试场景。"""

    def test_should_return_true_when_is_empty_called_given_no_content(self):
        # Given
        blob = Blob(content=b"")

        # When / Then
        assert blob.is_empty() is True

    def test_should_return_true_when_is_empty_called_given_empty_bytes(self):
        # When
        blob = Blob.create(content=b"test")
        blob.content = b""

        # Then
        assert blob.is_empty() is True

    def test_should_return_false_when_is_empty_called_given_valid_content(self):
        # Given
        blob = Blob.create(content=b"Test content")

        # When / Then
        assert blob.is_empty() is False

class TestBlobContentPreview:
    """内容预览测试场景。"""

    def test_should_return_text_preview_when_get_preview_called_given_text_content(self):
        # Given
        content = b"Hello, World! This is a test."
        blob = Blob.create(content=content)

        # When
        preview = blob.get_content_preview(max_length=20)

        # Then
        assert preview == "Hello, World! This i"

    def test_should_return_full_content_when_get_preview_called_given_short_content(self):
        # Given
        content = b"Short"
        blob = Blob.create(content=content)

        # When
        preview = blob.get_content_preview(max_length=100)

        # Then
        assert preview == "Short"

    def test_should_handle_binary_when_get_preview_called_given_binary_content(self):
        # Given
        content = bytes([0x80, 0x81, 0x82, 0x83, 0x84])
        blob = Blob.create(content=content)

        # When
        preview = blob.get_content_preview(max_length=10)

        # Then - 错误字符被替换
        assert "�" in preview or len(preview) <= 10

    def test_should_return_decompressed_when_get_preview_called_given_compressed(self):
        # Given
        content = b"This is the content to preview"
        blob = Blob.create(content=content)
        blob.compress()

        # When
        preview = blob.get_content_preview(max_length=20)

        # Then
        assert "This is the content" in preview

class TestBlobValidateContent:
    """内容验证测试场景。"""

    def test_should_return_true_when_validate_called_given_valid_content(self):
        # Given
        content = b"Valid content"
        blob = Blob.create(content=content)

        # When / Then
        assert blob.validate_content() is True

    def test_should_return_false_when_validate_called_given_empty_content(self):
        # Given
        blob = Blob(content=b"")

        # When / Then
        assert blob.validate_content() is False

    def test_should_return_false_when_validate_called_given_corrupted_content(self):
        # Given
        content = b"Original content"
        blob = Blob.create(content=content)
        # 修改内容但不更新 checksum
        blob.content = b"Modified content"

        # When / Then
        assert blob.validate_content() is False

    def test_should_return_false_when_validate_called_given_modified_checksum(self):
        # Given
        content = b"Original content"
        blob = Blob.create(content=content)
        # 修改 checksum
        blob.checksum = "wrong_checksum"

        # When / Then
        assert blob.validate_content() is False

class TestBlobCalculateHash:
    """_calculate_hash 静态方法测试场景。"""

    def test_should_return_sha256_hex_when_calculate_hash_called_given_content(self):
        # Given
        content = b"Test content"
        expected_hash = hashlib.sha256(content).hexdigest()

        # When
        result = Blob._calculate_hash(content)

        # Then
        assert result == expected_hash
        assert len(result) == 64  # SHA256 hex = 64 chars

    def test_should_return_hash_when_calculate_hash_called_given_empty_content(self):
        # Given
        content = b""
        expected_hash = hashlib.sha256(content).hexdigest()

        # When
        result = Blob._calculate_hash(content)

        # Then
        assert result == expected_hash

class TestBlobCreationDefaults:
    """Blob 默认创建测试场景。"""

    def test_should_create_with_defaults_when_instantiate_given_no_args(self):
        # When
        blob = Blob()

        # Then
        assert isinstance(blob.id, UUID)
        assert blob.content == b""
        assert blob.checksum == ""
        assert blob.size == 0
        assert blob.compressed is False
        assert blob.reference_count == 0
        assert isinstance(blob.created_at, datetime)

    def test_should_create_with_all_fields_when_instantiate_given_full_args(self):
        # Given
        blob_id = uuid4()
        content = b"Custom content"
        checksum = hashlib.sha256(content).hexdigest()
        created_at = datetime(2024, 1, 1, 12, 0, 0)

        # When
        blob = Blob(
            id=blob_id,
            content=content,
            checksum=checksum,
            size=len(content),
            compressed=True,
            reference_count=5,
            created_at=created_at,
        )

        # Then
        assert blob.id == blob_id
        assert blob.content == content
        assert blob.checksum == checksum
        assert blob.size == len(content)
        assert blob.compressed is True
        assert blob.reference_count == 5
        assert blob.created_at == created_at

class TestBlobWorkflow:
    """完整工作流测试场景。"""

    def test_should_complete_full_lifecycle_when_all_operations_called_given_new_blob(self):
        # Given - 创建新 blob（使用较大内容确保压缩有效）
        content = b"A" * 1000
        blob = Blob.create(content=content)

        # Then - 初始状态
        assert blob.reference_count == 0
        assert blob.is_orphaned() is True
        assert blob.compressed is False

        # When - 被引用
        blob.increment_reference()

        # Then
        assert blob.reference_count == 1
        assert blob.is_orphaned() is False

        # When - 压缩
        original_size = blob.size
        blob.compress()

        # Then
        assert blob.compressed is True
        assert blob.size < original_size

        # When - 获取原始内容（自动解压）
        raw = blob.get_raw_content()

        # Then
        assert raw == content

        # When - 取消引用
        blob.decrement_reference()

        # Then
        assert blob.reference_count == 0
        assert blob.is_orphaned() is True

        # When - 解压
        blob.decompress()

        # Then
        assert blob.compressed is False
        assert blob.content == content
