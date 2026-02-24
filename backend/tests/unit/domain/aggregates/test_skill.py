"""Skill Aggregate 单元测试套件。

本模块测试 Skill 聚合根的所有功能，包括：
- Skill 创建（默认值、自定义值）
- update_name 操作（有效名称、空值、空白字符、名称变更时slug更新）
- update_description 操作（有效描述、None值）
- set_public 操作（设为公开、设为私有）
- assign_tree 操作（分配Tree、解除分配）
- 版本控制（每次修改version递增、updated_at更新）

测试设计遵循 Given-When-Then 模式。
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from src.domain.aggregates.skill import Skill
from src.domain.value_objects.slug import Slug


class TestSkillCreation:
    """Skill 创建测试场景。"""

    def test_should_create_with_defaults_when_instantiate_given_minimal_values(self):
        # When
        skill = Skill()

        # Then
        assert isinstance(skill.id, UUID)
        assert isinstance(skill.user_id, UUID)
        assert skill.name == ""
        assert isinstance(skill.slug, Slug)
        assert skill.description is None
        assert skill.tree_id is None
        assert skill.is_public is False
        assert skill.version == 1
        assert isinstance(skill.created_at, datetime)
        assert isinstance(skill.updated_at, datetime)

    def test_should_create_with_custom_values_when_instantiate_given_full_args(self):
        # Given
        skill_id = uuid4()
        user_id = uuid4()
        tree_id = uuid4()
        created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        updated_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # When
        skill = Skill(
            id=skill_id,
            user_id=user_id,
            name="Test Skill",
            slug=Slug.from_name("Test Skill"),
            description="A test skill description",
            tree_id=tree_id,
            is_public=True,
            version=5,
            created_at=created_at,
            updated_at=updated_at,
        )

        # Then
        assert skill.id == skill_id
        assert skill.user_id == user_id
        assert skill.name == "Test Skill"
        assert str(skill.slug) == "test-skill"
        assert skill.description == "A test skill description"
        assert skill.tree_id == tree_id
        assert skill.is_public is True
        assert skill.version == 5
        assert skill.created_at == created_at
        assert skill.updated_at == updated_at


class TestSkillNameUpdate:
    """Skill 名称更新测试场景。"""

    def test_should_update_name_and_slug_when_update_name_called_given_valid_name(self):
        # Given
        skill = Skill(name="Old Name")
        original_version = skill.version
        original_updated_at = skill.updated_at

        # When
        skill.update_name("New Name")

        # Then
        assert skill.name == "New Name"
        assert str(skill.slug) == "new-name"
        assert skill.version == original_version + 1
        assert skill.updated_at >= original_updated_at

    def test_should_strip_whitespace_when_update_name_called_given_name_with_spaces(self):
        # Given
        skill = Skill(name="Old Name")

        # When
        skill.update_name("  New Name  ")

        # Then
        assert skill.name == "New Name"
        assert str(skill.slug) == "new-name"

    def test_should_raise_error_when_update_name_called_given_empty_string(self):
        # Given
        skill = Skill(name="Old Name")

        # When / Then
        with pytest.raises(ValueError) as exc_info:
            skill.update_name("")

        assert "cannot be empty" in str(exc_info.value)

    def test_should_raise_error_when_update_name_called_given_whitespace_only(self):
        # Given
        skill = Skill(name="Old Name")

        # When / Then
        with pytest.raises(ValueError) as exc_info:
            skill.update_name("   ")

        assert "cannot be empty" in str(exc_info.value)

    def test_should_raise_error_when_update_name_called_given_none(self):
        # Given
        skill = Skill(name="Old Name")

        # When / Then
        with pytest.raises(ValueError) as exc_info:
            skill.update_name(None)

        assert "cannot be empty" in str(exc_info.value)


class TestSkillDescriptionUpdate:
    """Skill 描述更新测试场景。"""

    def test_should_update_description_when_update_description_called_given_valid_text(self):
        # Given
        skill = Skill(description=None)
        original_version = skill.version
        original_updated_at = skill.updated_at

        # When
        skill.update_description("New description")

        # Then
        assert skill.description == "New description"
        assert skill.version == original_version + 1
        assert skill.updated_at >= original_updated_at

    def test_should_set_none_when_update_description_called_given_none(self):
        # Given
        skill = Skill(description="Existing description")

        # When
        skill.update_description(None)

        # Then
        assert skill.description is None

    def test_should_set_empty_string_when_update_description_called_given_empty_string(self):
        # Given
        skill = Skill(description="Existing description")

        # When
        skill.update_description("")

        # Then
        assert skill.description == ""


class TestSkillVisibility:
    """Skill 可见性设置测试场景。"""

    def test_should_set_public_when_set_public_called_given_true(self):
        # Given
        skill = Skill(is_public=False)
        original_version = skill.version
        original_updated_at = skill.updated_at

        # When
        skill.set_public(True)

        # Then
        assert skill.is_public is True
        assert skill.version == original_version + 1
        assert skill.updated_at >= original_updated_at

    def test_should_set_private_when_set_public_called_given_false(self):
        # Given
        skill = Skill(is_public=True)

        # When
        skill.set_public(False)

        # Then
        assert skill.is_public is False

    def test_should_not_change_visibility_when_set_public_called_given_same_value(self):
        # Given
        skill = Skill(is_public=True)

        # When
        skill.set_public(True)

        # Then - 允许重复设置，版本仍会更新
        assert skill.is_public is True


class TestSkillTreeAssignment:
    """Skill Tree 分配测试场景。"""

    def test_should_assign_tree_when_assign_tree_called_given_valid_tree_id(self):
        # Given
        skill = Skill(tree_id=None)
        tree_id = uuid4()
        original_version = skill.version
        original_updated_at = skill.updated_at

        # When
        skill.assign_tree(tree_id)

        # Then
        assert skill.tree_id == tree_id
        assert skill.version == original_version + 1
        assert skill.updated_at >= original_updated_at

    def test_should_unassign_tree_when_assign_tree_called_given_none(self):
        # Given
        skill = Skill(tree_id=uuid4())

        # When
        skill.assign_tree(None)

        # Then
        assert skill.tree_id is None

    def test_should_change_tree_when_assign_tree_called_given_different_tree_id(self):
        # Given
        old_tree_id = uuid4()
        new_tree_id = uuid4()
        skill = Skill(tree_id=old_tree_id)

        # When
        skill.assign_tree(new_tree_id)

        # Then
        assert skill.tree_id == new_tree_id


class TestSkillVersionControl:
    """Skill 版本控制测试场景。"""

    def test_should_increment_version_on_each_modification(self):
        # Given
        skill = Skill()
        initial_version = skill.version

        # When - 连续修改
        skill.update_name("First Name")
        assert skill.version == initial_version + 1

        skill.update_description("Description")
        assert skill.version == initial_version + 2

        skill.set_public(True)
        assert skill.version == initial_version + 3

        skill.assign_tree(uuid4())
        assert skill.version == initial_version + 4

    def test_should_update_timestamp_on_each_modification(self):
        # Given
        skill = Skill()
        previous_updated_at = skill.updated_at

        # When - 每次修改后时间戳应该更新
        skill.update_name("New Name")
        assert skill.updated_at >= previous_updated_at
        previous_updated_at = skill.updated_at

        skill.update_description("Description")
        assert skill.updated_at >= previous_updated_at
        previous_updated_at = skill.updated_at

        skill.set_public(True)
        assert skill.updated_at >= previous_updated_at


class TestSkillSlugGeneration:
    """Skill Slug 生成测试场景。"""

    def test_should_generate_slug_from_name_when_update_name_called(self):
        # Given
        skill = Skill(name="Old Name")

        # When
        skill.update_name("Python Programming")

        # Then
        assert str(skill.slug) == "python-programming"

    def test_should_normalize_special_chars_when_update_name_called(self):
        # Given
        skill = Skill(name="Old Name")

        # When
        skill.update_name("C++ Programming & Design")

        # Then
        assert str(skill.slug) == "c-programming-design"

    def test_should_handle_unicode_when_update_name_called(self):
        # Given
        skill = Skill(name="Old Name")
        # When / Then - Unicode characters are stripped, but name still works
        # Note: Slug.from_name removes non-ascii chars, so "中文技能名称" becomes empty
        # We test that the error is raised appropriately
        with pytest.raises(Exception):
            skill.update_name("中文技能名称")


class TestSkillWorkflow:
    """Skill 完整工作流测试场景。"""

    def test_should_complete_full_lifecycle_when_all_operations_called_given_new_skill(self):
        # Given - 新创建的技能
        skill = Skill(
            name="Draft Skill",
            description="Initial draft",
            is_public=False,
        )

        # Then - 初始状态
        assert skill.name == "Draft Skill"
        assert skill.is_public is False
        assert skill.version == 1

        # When - 更新名称
        skill.update_name("Published Skill")

        # Then
        assert skill.name == "Published Skill"
        assert str(skill.slug) == "published-skill"

        # When - 更新描述
        skill.update_description("Final published version")

        # Then
        assert skill.description == "Final published version"

        # When - 分配 Tree
        tree_id = uuid4()
        skill.assign_tree(tree_id)

        # Then
        assert skill.tree_id == tree_id

        # When - 设为公开
        skill.set_public(True)

        # Then
        assert skill.is_public is True

        # Then - 验证最终版本号 (5次修改: name初始化时+1, update_name+1, update_description+1, assign_tree+1, set_public+1)
        assert skill.version == 5

    def test_should_handle_reversion_when_skill_modified_multiple_times(self):
        # Given
        skill = Skill(name="Original")
        original_tree_id = uuid4()
        skill.assign_tree(original_tree_id)
        skill.set_public(True)

        # When - 修改后再改回来
        skill.update_name("Changed")
        skill.update_name("Original")
        skill.set_public(False)
        skill.set_public(True)
        skill.assign_tree(None)
        skill.assign_tree(original_tree_id)

        # Then - 状态应该回到类似初始，但版本号反映了所有修改 (1初始 + 8次操作)
        assert skill.name == "Original"
        assert skill.is_public is True
        assert skill.tree_id == original_tree_id
        assert skill.version == 9  # 1 + 8次修改
