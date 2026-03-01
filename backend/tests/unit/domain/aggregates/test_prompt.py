"""Prompt Aggregate 单元测试套件。

本模块测试 Prompt 聚合根的所有功能，包括：
- Prompt 创建（默认值、自定义值）
- update_title 操作（有效标题、空值、空白字符、超长标题）
- update_content 操作（有效内容、空值）
- update_description 操作（有效描述、None值）
- update_tags 操作（正常标签、标签规范化、去重、超长标签、过多标签）
- publish_version 操作（快照、版本递增）
- 版本控制（每次修改version递增、updated_at更新）

测试设计遵循 Given-When-Then 模式。
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from src.domain.aggregates.prompt import Prompt
from src.domain.entities.prompt_version import PromptVersion
from src.domain.exceptions import ValidationError


class TestPromptCreation:
    """Prompt 创建测试场景。"""

    def test_should_create_with_defaults_when_instantiate_given_minimal_values(self):
        # When
        prompt = Prompt()

        # Then
        assert isinstance(prompt.id, UUID)
        assert isinstance(prompt.user_id, UUID)
        assert prompt.title == ""
        assert prompt.content == ""
        assert prompt.description is None
        assert prompt.tags == []
        assert prompt.version == 1
        assert isinstance(prompt.created_at, datetime)
        assert isinstance(prompt.updated_at, datetime)

    def test_should_create_with_custom_values_when_instantiate_given_full_args(self):
        # Given
        prompt_id = uuid4()
        user_id = uuid4()
        created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        updated_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # When
        prompt = Prompt(
            id=prompt_id,
            user_id=user_id,
            title="Test Prompt",
            content="Test content body",
            description="A test prompt description",
            tags=["python", "ai"],
            version=5,
            created_at=created_at,
            updated_at=updated_at,
        )

        # Then
        assert prompt.id == prompt_id
        assert prompt.user_id == user_id
        assert prompt.title == "Test Prompt"
        assert prompt.content == "Test content body"
        assert prompt.description == "A test prompt description"
        assert prompt.tags == ["python", "ai"]
        assert prompt.version == 5
        assert prompt.created_at == created_at
        assert prompt.updated_at == updated_at


class TestPromptUpdateTitle:
    """Prompt 标题更新测试场景。"""

    def test_should_update_title_when_update_title_called_given_valid_title(self):
        # Given
        prompt = Prompt(title="Old Title")
        original_version = prompt.version
        original_updated_at = prompt.updated_at

        # When
        prompt.update_title("New Title")

        # Then
        assert prompt.title == "New Title"
        assert prompt.version == original_version + 1
        assert prompt.updated_at >= original_updated_at

    def test_should_strip_whitespace_when_update_title_called_given_title_with_spaces(self):
        # Given
        prompt = Prompt(title="Old Title")

        # When
        prompt.update_title("  New Title  ")

        # Then
        assert prompt.title == "New Title"

    def test_should_raise_error_when_update_title_called_given_empty_string(self):
        # Given
        prompt = Prompt(title="Old Title")

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            prompt.update_title("")

        assert "cannot be empty" in str(exc_info.value)

    def test_should_raise_error_when_update_title_called_given_whitespace_only(self):
        # Given
        prompt = Prompt(title="Old Title")

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            prompt.update_title("   ")

        assert "cannot be empty" in str(exc_info.value)

    def test_should_raise_error_when_update_title_called_given_title_exceeds_200_chars(self):
        # Given
        prompt = Prompt(title="Old Title")
        long_title = "A" * 201

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            prompt.update_title(long_title)

        assert "200" in str(exc_info.value)

    def test_should_accept_title_when_update_title_called_given_exactly_200_chars(self):
        # Given
        prompt = Prompt(title="Old Title")
        exact_title = "A" * 200

        # When
        prompt.update_title(exact_title)

        # Then
        assert prompt.title == exact_title


class TestPromptUpdateContent:
    """Prompt 内容更新测试场景。"""

    def test_should_update_content_when_update_content_called_given_valid_content(self):
        # Given
        prompt = Prompt(content="Old content")
        original_version = prompt.version
        original_updated_at = prompt.updated_at

        # When
        prompt.update_content("New content body")

        # Then
        assert prompt.content == "New content body"
        assert prompt.version == original_version + 1
        assert prompt.updated_at >= original_updated_at

    def test_should_allow_empty_content_when_update_content_called_given_empty_string(self):
        # Given
        prompt = Prompt(content="Old content")

        # When
        prompt.update_content("")

        # Then
        assert prompt.content == ""


class TestPromptUpdateDescription:
    """Prompt 描述更新测试场景。"""

    def test_should_update_description_when_update_description_called_given_valid_text(self):
        # Given
        prompt = Prompt(description=None)
        original_version = prompt.version
        original_updated_at = prompt.updated_at

        # When
        prompt.update_description("New description")

        # Then
        assert prompt.description == "New description"
        assert prompt.version == original_version + 1
        assert prompt.updated_at >= original_updated_at

    def test_should_set_none_when_update_description_called_given_none(self):
        # Given
        prompt = Prompt(description="Existing description")

        # When
        prompt.update_description(None)

        # Then
        assert prompt.description is None

    def test_should_set_empty_string_when_update_description_called_given_empty_string(self):
        # Given
        prompt = Prompt(description="Existing description")

        # When
        prompt.update_description("")

        # Then
        assert prompt.description == ""


class TestPromptUpdateTags:
    """Prompt 标签更新测试场景。"""

    def test_should_update_tags_when_update_tags_called_given_valid_tags(self):
        # Given
        prompt = Prompt(tags=[])
        original_version = prompt.version
        original_updated_at = prompt.updated_at

        # When
        prompt.update_tags(["python", "ai", "testing"])

        # Then
        assert prompt.tags == ["python", "ai", "testing"]
        assert prompt.version == original_version + 1
        assert prompt.updated_at >= original_updated_at

    def test_should_normalize_to_lowercase_when_update_tags_called_given_mixed_case(self):
        # Given
        prompt = Prompt()

        # When
        prompt.update_tags(["Python", "AI", "TESTING"])

        # Then
        assert prompt.tags == ["python", "ai", "testing"]

    def test_should_strip_whitespace_when_update_tags_called_given_tags_with_spaces(self):
        # Given
        prompt = Prompt()

        # When
        prompt.update_tags(["  python  ", " ai ", "testing"])

        # Then
        assert prompt.tags == ["python", "ai", "testing"]

    def test_should_deduplicate_when_update_tags_called_given_duplicate_tags(self):
        # Given
        prompt = Prompt()

        # When
        prompt.update_tags(["python", "Python", "PYTHON", "ai"])

        # Then
        assert prompt.tags == ["python", "ai"]

    def test_should_skip_empty_tags_when_update_tags_called_given_empty_strings(self):
        # Given
        prompt = Prompt()

        # When
        prompt.update_tags(["python", "", "  ", "ai"])

        # Then
        assert prompt.tags == ["python", "ai"]

    def test_should_raise_error_when_update_tags_called_given_tag_exceeds_50_chars(self):
        # Given
        prompt = Prompt()
        long_tag = "a" * 51

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            prompt.update_tags([long_tag])

        assert "50" in str(exc_info.value)

    def test_should_accept_tag_when_update_tags_called_given_tag_exactly_50_chars(self):
        # Given
        prompt = Prompt()
        exact_tag = "a" * 50

        # When
        prompt.update_tags([exact_tag])

        # Then
        assert prompt.tags == [exact_tag]

    def test_should_raise_error_when_update_tags_called_given_more_than_20_tags(self):
        # Given
        prompt = Prompt()
        too_many_tags = [f"tag{i}" for i in range(21)]

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            prompt.update_tags(too_many_tags)

        assert "20" in str(exc_info.value)

    def test_should_accept_tags_when_update_tags_called_given_exactly_20_tags(self):
        # Given
        prompt = Prompt()
        max_tags = [f"tag{i}" for i in range(20)]

        # When
        prompt.update_tags(max_tags)

        # Then
        assert len(prompt.tags) == 20

    def test_should_clear_tags_when_update_tags_called_given_empty_list(self):
        # Given
        prompt = Prompt(tags=["old-tag"])

        # When
        prompt.update_tags([])

        # Then
        assert prompt.tags == []


class TestPromptPublishVersion:
    """Prompt 版本发布测试场景。"""

    def test_should_create_version_snapshot_when_publish_version_called(self):
        # Given
        prompt = Prompt(
            title="My Prompt",
            content="Prompt content",
            description="Prompt description",
            tags=["python", "ai"],
        )
        original_version = prompt.version

        # When
        version = prompt.publish_version()

        # Then
        assert isinstance(version, PromptVersion)
        assert version.prompt_id == prompt.id
        assert version.version_number == original_version
        assert version.title == "My Prompt"
        assert version.content == "Prompt content"
        assert version.description == "Prompt description"
        assert version.tags == ["python", "ai"]

    def test_should_increment_prompt_version_after_publish_version_called(self):
        # Given
        prompt = Prompt(title="My Prompt", content="Content")
        original_version = prompt.version

        # When
        prompt.publish_version()

        # Then
        assert prompt.version == original_version + 1

    def test_should_create_independent_tags_copy_when_publish_version_called(self):
        # Given
        prompt = Prompt(tags=["original"])

        # When
        version = prompt.publish_version()

        # Then - modifying prompt tags should not affect version tags
        prompt.update_tags(["modified"])
        assert version.tags == ["original"]

    def test_should_create_multiple_versions_with_incremental_numbers(self):
        # Given
        prompt = Prompt(title="My Prompt", content="v1 content")

        # When
        v1 = prompt.publish_version()
        prompt.update_content("v2 content")
        v2 = prompt.publish_version()

        # Then
        assert v1.version_number == 1
        assert (
            v2.version_number == 3
        )  # 1 (initial) + 1 (publish_v1) + 1 (update_content) = version 3 before publish_v2
        assert v1.content == "v1 content"
        assert v2.content == "v2 content"


class TestPromptVersionControl:
    """Prompt 版本控制测试场景。"""

    def test_should_increment_version_on_each_modification(self):
        # Given
        prompt = Prompt()
        initial_version = prompt.version

        # When - 连续修改
        prompt.update_title("Title")
        assert prompt.version == initial_version + 1

        prompt.update_content("Content")
        assert prompt.version == initial_version + 2

        prompt.update_description("Description")
        assert prompt.version == initial_version + 3

        prompt.update_tags(["tag1"])
        assert prompt.version == initial_version + 4

    def test_should_update_timestamp_on_each_modification(self):
        # Given
        prompt = Prompt()
        previous_updated_at = prompt.updated_at

        # When - 每次修改后时间戳应该更新
        prompt.update_title("New Title")
        assert prompt.updated_at >= previous_updated_at
        previous_updated_at = prompt.updated_at

        prompt.update_content("New Content")
        assert prompt.updated_at >= previous_updated_at
        previous_updated_at = prompt.updated_at

        prompt.update_description("Description")
        assert prompt.updated_at >= previous_updated_at
        previous_updated_at = prompt.updated_at

        prompt.update_tags(["tag"])
        assert prompt.updated_at >= previous_updated_at


class TestPromptWorkflow:
    """Prompt 完整工作流测试场景。"""

    def test_should_complete_full_lifecycle_when_all_operations_called(self):
        # Given - 新创建的 Prompt
        prompt = Prompt(
            title="Draft Prompt",
            content="Initial content",
            description="Initial draft",
        )

        # Then - 初始状态
        assert prompt.title == "Draft Prompt"
        assert prompt.version == 1

        # When - 更新标题
        prompt.update_title("Published Prompt")

        # Then
        assert prompt.title == "Published Prompt"

        # When - 更新内容
        prompt.update_content("Final content")

        # Then
        assert prompt.content == "Final content"

        # When - 更新描述
        prompt.update_description("Final description")

        # Then
        assert prompt.description == "Final description"

        # When - 更新标签
        prompt.update_tags(["python", "ai"])

        # Then
        assert prompt.tags == ["python", "ai"]

        # When - 发布版本
        version = prompt.publish_version()

        # Then
        assert version.version_number == 5  # 1 initial + 4 updates
        assert prompt.version == 6  # after publish increments

    def test_should_handle_multiple_publish_cycles(self):
        # Given
        prompt = Prompt(title="My Prompt", content="v1")

        # When - first publish
        v1 = prompt.publish_version()

        # When - modify and publish again
        prompt.update_content("v2")
        v2 = prompt.publish_version()

        # When - modify and publish again
        prompt.update_content("v3")
        prompt.update_tags(["final"])
        v3 = prompt.publish_version()

        # Then
        assert v1.content == "v1"
        assert v2.content == "v2"
        assert v3.content == "v3"
        assert v3.tags == ["final"]
        assert v1.version_number < v2.version_number < v3.version_number
