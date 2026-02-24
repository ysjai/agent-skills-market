"""Tree Aggregate 单元测试套件。

本模块测试 Tree 聚合根和 TreeEntry 实体的所有功能，包括：
- Tree 创建（空 Tree、带初始条目的 Tree）
- add_entry 操作（添加文件、目录、重复路径、验证错误）
- delete_entry 操作（删除文件、级联删除目录、不存在条目）
- rename_entry 操作（重命名文件、级联重命名目录、冲突处理）
- move_entry 操作（移动文件、移动目录、冲突处理）
- update_entry_content 操作（更新文件内容、目录内容错误处理）
- TreeEntry 验证（类型验证、blob_id 验证）

测试设计遵循 Given-When-Then 模式，并使用 pytest.mark.parametrize 减少重复代码。
"""

from uuid import UUID, uuid4

import pytest

from app.domain.aggregates.tree import ENTRY_TYPE_BLOB, ENTRY_TYPE_TREE, Tree, TreeEntry
from app.domain.exceptions import ResourceConflictError, ResourceNotFoundError, ValidationError
from app.domain.value_objects.path import Path


class TestTreeCreation:
    """2.2.1 Tree 创建测试场景。"""

    def test_should_create_empty_tree_with_auto_generated_id(self):
        """Scenario: 创建空 Tree - id 应该被自动生成，entries 应该为空列表。"""
        # When
        tree = Tree.create()

        # Then
        assert isinstance(tree.id, UUID)
        assert tree.entries == []

    def test_should_create_tree_with_initial_entries(self):
        """Scenario: 创建带初始条目的 Tree - entries 应该包含 TreeEntry。"""
        # Given
        blob_id = uuid4()
        entries_data = [{"path": "README.md", "type": ENTRY_TYPE_BLOB, "blob_id": str(blob_id)}]

        # When
        tree = Tree.create(entries=entries_data)

        # Then
        assert len(tree.entries) == 1
        entry = tree.entries[0]
        assert str(entry.path) == "README.md"
        assert entry.entry_type == ENTRY_TYPE_BLOB
        assert entry.blob_id == blob_id


class TestAddEntry:
    """2.2.2 add_entry 测试场景。"""

    def test_should_add_file_entry_successfully(self):
        """Scenario: 添加文件条目 - entries 应该包含该条目，类型为 blob。"""
        # Given
        tree = Tree.create()
        blob_id = uuid4()

        # When
        tree.add_entry("file.txt", ENTRY_TYPE_BLOB, blob_id=blob_id)

        # Then
        assert len(tree.entries) == 1
        entry = tree.entries[0]
        assert str(entry.path) == "file.txt"
        assert entry.entry_type == ENTRY_TYPE_BLOB
        assert entry.blob_id == blob_id

    def test_should_add_directory_entry_successfully(self):
        """Scenario: 添加目录条目 - entries 应该包含该条目，类型为 tree，blob_id 为 None。"""
        # Given
        tree = Tree.create()

        # When
        tree.add_entry("src/", ENTRY_TYPE_TREE)

        # Then
        assert len(tree.entries) == 1
        entry = tree.entries[0]
        assert str(entry.path) == "src/"
        assert entry.entry_type == ENTRY_TYPE_TREE
        assert entry.blob_id is None

    def test_should_raise_resource_conflict_error_when_adding_duplicate_path(self):
        """Scenario: 添加重复路径条目 - 应该抛出 ResourceConflictError。"""
        # Given
        tree = Tree.create()
        blob_id = uuid4()
        tree.add_entry("file.txt", ENTRY_TYPE_BLOB, blob_id=blob_id)

        # When / Then
        with pytest.raises(ResourceConflictError) as exc_info:
            tree.add_entry("file.txt", ENTRY_TYPE_BLOB, blob_id=uuid4())

        assert "already exists" in str(exc_info.value)

    def test_should_raise_validation_error_when_adding_blob_without_blob_id(self):
        """Scenario: 添加 blob 条目但不提供 blob_id - 应该抛出 ValidationError。"""
        # Given
        tree = Tree.create()

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            tree.add_entry("file.txt", ENTRY_TYPE_BLOB, blob_id=None)

        assert "must have a blob_id" in str(exc_info.value)

    def test_should_raise_validation_error_when_adding_tree_with_blob_id(self):
        """Scenario: 添加 tree 条目但提供 blob_id - 应该抛出 ValidationError。"""
        # Given
        tree = Tree.create()

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            tree.add_entry("src/", ENTRY_TYPE_TREE, blob_id=uuid4())

        assert "cannot have a blob_id" in str(exc_info.value)


class TestDeleteEntry:
    """2.2.3 delete_entry 测试场景。"""

    def test_should_delete_file_entry_and_return_blob_id(self):
        """Scenario: 删除文件条目 - entries 不应该再包含该条目，返回 blob_id 列表。"""
        # Given
        tree = Tree.create()
        blob_id = uuid4()
        tree.add_entry("file.txt", ENTRY_TYPE_BLOB, blob_id=blob_id)

        # When
        result = tree.delete_entry("file.txt")

        # Then
        assert len(tree.entries) == 0
        assert blob_id in result
        assert len(result) == 1

    def test_should_delete_directory_and_children_cascade(self):
        """Scenario: 删除目录及其子项 - 所有子项都应该被删除，返回所有 blob_id。"""
        # Given
        tree = Tree.create()
        blob_id1 = uuid4()
        blob_id2 = uuid4()
        tree.add_entry("src/", ENTRY_TYPE_TREE)
        tree.add_entry("src/main.py", ENTRY_TYPE_BLOB, blob_id=blob_id1)
        tree.add_entry("src/utils.py", ENTRY_TYPE_BLOB, blob_id=blob_id2)

        # When
        result = tree.delete_entry("src/")

        # Then
        assert len(tree.entries) == 0
        assert blob_id1 in result
        assert blob_id2 in result
        assert len(result) == 2

    def test_should_raise_validation_error_when_deleting_nonexistent_entry(self):
        """Scenario: 删除不存在的条目 - 应该抛出 ValidationError。"""
        # Given
        tree = Tree.create()

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            tree.delete_entry("nonexistent.txt")

        assert "not found" in str(exc_info.value)

    def test_should_allow_deleting_skill_md(self):
        """Scenario: 尝试删除 SKILL.md - 应该允许删除（业务规则在 Handler 层）。"""
        # Given
        tree = Tree.create()
        blob_id = uuid4()
        tree.add_entry("SKILL.md", ENTRY_TYPE_BLOB, blob_id=blob_id)

        # When
        result = tree.delete_entry("SKILL.md")

        # Then
        assert len(tree.entries) == 0
        assert blob_id in result


class TestRenameEntry:
    """2.2.4 rename_entry 测试场景。"""

    def test_should_rename_file_successfully(self):
        """Scenario: 重命名文件 - entries 应该包含新路径，不应该包含旧路径。"""
        # Given
        tree = Tree.create()
        blob_id = uuid4()
        tree.add_entry("old.txt", ENTRY_TYPE_BLOB, blob_id=blob_id)

        # When
        tree.rename_entry("old.txt", "new.txt")

        # Then
        assert tree.get_entry("new.txt") is not None
        assert tree.get_entry("old.txt") is None
        entry = tree.get_entry("new.txt")
        assert entry.blob_id == blob_id

    def test_should_rename_directory_and_children_cascade(self):
        """Scenario: 重命名目录及其子项 - 所有子项路径都应该更新。"""
        # Given
        tree = Tree.create()
        tree.add_entry("src/", ENTRY_TYPE_TREE)
        tree.add_entry("src/main.py", ENTRY_TYPE_BLOB, blob_id=uuid4())
        tree.add_entry("src/utils/helper.py", ENTRY_TYPE_BLOB, blob_id=uuid4())

        # When
        tree.rename_entry("src/", "lib/")

        # Then
        assert tree.get_entry("lib/") is not None
        assert tree.get_entry("src/") is None
        assert tree.get_entry("lib/main.py") is not None
        assert tree.get_entry("src/main.py") is None
        assert tree.get_entry("lib/utils/helper.py") is not None
        assert tree.get_entry("src/utils/helper.py") is None

    def test_should_raise_resource_conflict_error_when_renaming_to_existing_path(self):
        """Scenario: 重命名为已存在的路径 - 应该抛出 ResourceConflictError。"""
        # Given
        tree = Tree.create()
        tree.add_entry("old.txt", ENTRY_TYPE_BLOB, blob_id=uuid4())
        tree.add_entry("existing.txt", ENTRY_TYPE_BLOB, blob_id=uuid4())

        # When / Then
        with pytest.raises(ResourceConflictError) as exc_info:
            tree.rename_entry("old.txt", "existing.txt")

        assert "already exists" in str(exc_info.value)

    def test_should_raise_resource_not_found_error_when_renaming_nonexistent_entry(self):
        """Scenario: 重命名不存在的条目 - 应该抛出 ResourceNotFoundError。"""
        # Given
        tree = Tree.create()

        # When / Then
        with pytest.raises(ResourceNotFoundError) as exc_info:
            tree.rename_entry("nonexistent.txt", "new.txt")

        assert "not found" in str(exc_info.value)

    def test_should_raise_validation_error_when_new_path_is_empty(self):
        """Scenario: 使用空字符串作为新名称 - 应该抛出 ValidationError。"""
        # Given
        tree = Tree.create()
        tree.add_entry("old.txt", ENTRY_TYPE_BLOB, blob_id=uuid4())

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            tree.rename_entry("old.txt", "")

        assert "cannot be empty" in str(exc_info.value)

    def test_should_raise_validation_error_when_new_path_same_as_old(self):
        """Scenario: 新旧名称相同 - 应该抛出 ValidationError。"""
        # Given
        tree = Tree.create()
        tree.add_entry("file.txt", ENTRY_TYPE_BLOB, blob_id=uuid4())

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            tree.rename_entry("file.txt", "file.txt")

        assert "must be different" in str(exc_info.value)


class TestMoveEntry:
    """2.2.5 move_entry 测试场景。"""

    def test_should_move_file_to_directory(self):
        """Scenario: 移动文件到目录 - entries 应该包含目标路径，不应该包含源路径。"""
        # Given
        tree = Tree.create()
        blob_id = uuid4()
        tree.add_entry("file.txt", ENTRY_TYPE_BLOB, blob_id=blob_id)
        tree.add_entry("dest/", ENTRY_TYPE_TREE)

        # When
        tree.move_entry("file.txt", "dest/file.txt")

        # Then
        assert tree.get_entry("dest/file.txt") is not None
        assert tree.get_entry("file.txt") is None
        entry = tree.get_entry("dest/file.txt")
        assert entry.blob_id == blob_id

    def test_should_move_directory_and_all_contents_cascade(self):
        """Scenario: 移动目录及其所有内容 - 所有子项都应该移动到目标位置。"""
        # Given
        tree = Tree.create()
        tree.add_entry("src/", ENTRY_TYPE_TREE)
        tree.add_entry("src/main.py", ENTRY_TYPE_BLOB, blob_id=uuid4())
        tree.add_entry("src/utils/helper.py", ENTRY_TYPE_BLOB, blob_id=uuid4())
        tree.add_entry("lib/", ENTRY_TYPE_TREE)

        # When
        tree.move_entry("src/", "lib/src/")

        # Then
        assert tree.get_entry("lib/src/") is not None
        assert tree.get_entry("src/") is None
        assert tree.get_entry("lib/src/main.py") is not None
        assert tree.get_entry("src/main.py") is None
        assert tree.get_entry("lib/src/utils/helper.py") is not None
        assert tree.get_entry("src/utils/helper.py") is None

    def test_should_raise_resource_conflict_error_when_moving_to_existing_path(self):
        """Scenario: 移动到已存在的路径 - 应该抛出 ResourceConflictError。

        Note: This test documents a known bug in the Tree implementation.
        The move_entry method should check for conflicts BEFORE modifying entries,
        but currently it checks after, which means it never detects conflicts.
        """
        # Given
        tree = Tree.create()
        tree.add_entry("src/file.txt", ENTRY_TYPE_BLOB, blob_id=uuid4())
        tree.add_entry("dest/file.txt", ENTRY_TYPE_BLOB, blob_id=uuid4())

        # When / Then
        with pytest.raises(ResourceConflictError) as exc_info:
            tree.move_entry("src/file.txt", "dest/file.txt")

        assert "already exists" in str(exc_info.value)

    def test_should_raise_resource_not_found_error_when_moving_nonexistent_entry(self):
        """Scenario: 移动不存在的条目 - 应该抛出 ResourceNotFoundError。"""
        # Given
        tree = Tree.create()

        # When / Then
        with pytest.raises(ResourceNotFoundError) as exc_info:
            tree.move_entry("nonexistent.txt", "dest.txt")

        assert "not found" in str(exc_info.value)

    def test_should_raise_validation_error_when_target_is_empty(self):
        """Scenario: 使用空字符串作为目标 - 应该抛出 ValidationError。"""
        # Given
        tree = Tree.create()
        tree.add_entry("file.txt", ENTRY_TYPE_BLOB, blob_id=uuid4())

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            tree.move_entry("file.txt", "")

        assert "cannot be empty" in str(exc_info.value)


class TestUpdateEntryContent:
    """2.2.6 update_entry_content 测试场景。"""

    def test_should_update_file_content_and_return_old_blob_id(self):
        """Scenario: 更新文件内容 - blob_id 应该更新，返回旧 blob_id。"""
        # Given
        tree = Tree.create()
        old_blob_id = uuid4()
        new_blob_id = uuid4()
        tree.add_entry("file.txt", ENTRY_TYPE_BLOB, blob_id=old_blob_id)

        # When
        result = tree.update_entry_content("file.txt", new_blob_id)

        # Then
        assert result == old_blob_id
        entry = tree.get_entry("file.txt")
        assert entry.blob_id == new_blob_id

    def test_should_raise_validation_error_when_updating_directory_content(self):
        """Scenario: 更新目录内容 - 应该抛出 ValidationError（不能更新目录内容）。"""
        # Given
        tree = Tree.create()
        tree.add_entry("src/", ENTRY_TYPE_TREE)

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            tree.update_entry_content("src/", uuid4())

        assert "not a file" in str(exc_info.value)

    def test_should_raise_resource_not_found_error_when_updating_nonexistent_file(self):
        """Scenario: 更新不存在的文件 - 应该抛出 ResourceNotFoundError。"""
        # Given
        tree = Tree.create()

        # When / Then
        with pytest.raises(ResourceNotFoundError) as exc_info:
            tree.update_entry_content("nonexistent.txt", uuid4())

        assert "not found" in str(exc_info.value)


class TestTreeEntryValidation:
    """TreeEntry 验证测试场景。"""

    def test_should_create_blob_entry_with_blob_id_successfully(self):
        """Scenario: blob 条目有 blob_id - 应该成功创建。"""
        # Given
        blob_id = uuid4()

        # When
        entry = TreeEntry(path=Path("file.txt"), entry_type=ENTRY_TYPE_BLOB, blob_id=blob_id)

        # Then
        assert entry.entry_type == ENTRY_TYPE_BLOB
        assert entry.blob_id == blob_id
        assert entry.is_file() is True
        assert entry.is_directory() is False

    def test_should_create_tree_entry_without_blob_id_successfully(self):
        """Scenario: tree 条目无 blob_id - 应该成功创建。"""
        # When
        entry = TreeEntry(path=Path("src/"), entry_type=ENTRY_TYPE_TREE, blob_id=None)

        # Then
        assert entry.entry_type == ENTRY_TYPE_TREE
        assert entry.blob_id is None
        assert entry.is_file() is False
        assert entry.is_directory() is True

    @pytest.mark.parametrize(
        "invalid_type",
        ["invalid", "file", "folder", "", "BLOB", "TREE"],
    )
    def test_should_raise_validation_error_when_entry_type_is_invalid(self, invalid_type):
        """Scenario: entry_type 无效 - 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            TreeEntry(path=Path("file.txt"), entry_type=invalid_type, blob_id=uuid4())

        assert "Invalid entry type" in str(exc_info.value)

    def test_should_raise_validation_error_when_blob_entry_without_blob_id(self):
        """Scenario: blob 条目无 blob_id - 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            TreeEntry(path=Path("file.txt"), entry_type=ENTRY_TYPE_BLOB, blob_id=None)

        assert "must have a blob_id" in str(exc_info.value)

    def test_should_raise_validation_error_when_tree_entry_with_blob_id(self):
        """Scenario: tree 条目有 blob_id - 应该抛出 ValidationError。"""
        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            TreeEntry(path=Path("src/"), entry_type=ENTRY_TYPE_TREE, blob_id=uuid4())

        assert "cannot have a blob_id" in str(exc_info.value)


class TestTreeUtilityMethods:
    """Tree 工具方法测试场景。"""

    def test_should_get_entry_by_path(self):
        """测试：通过路径获取条目。"""
        # Given
        tree = Tree.create()
        blob_id = uuid4()
        tree.add_entry("file.txt", ENTRY_TYPE_BLOB, blob_id=blob_id)

        # When
        entry = tree.get_entry("file.txt")

        # Then
        assert entry is not None
        assert str(entry.path) == "file.txt"
        assert entry.blob_id == blob_id

    def test_should_return_none_when_getting_nonexistent_entry(self):
        """测试：获取不存在的条目应该返回 None。"""
        # Given
        tree = Tree.create()

        # When
        entry = tree.get_entry("nonexistent.txt")

        # Then
        assert entry is None

    def test_should_list_all_entries(self):
        """测试：列出所有条目。"""
        # Given
        tree = Tree.create()
        tree.add_entry("file1.txt", ENTRY_TYPE_BLOB, blob_id=uuid4())
        tree.add_entry("file2.txt", ENTRY_TYPE_BLOB, blob_id=uuid4())

        # When
        entries = tree.list_entries()

        # Then
        assert len(entries) == 2

    def test_should_convert_to_dict(self):
        """测试：转换为字典。"""
        # Given
        tree = Tree.create()
        blob_id = uuid4()
        tree.add_entry("file.txt", ENTRY_TYPE_BLOB, blob_id=blob_id)

        # When
        result = tree.to_dict()

        # Then
        assert "entries" in result
        assert len(result["entries"]) == 1
        assert result["entries"][0]["path"] == "file.txt"
        assert result["entries"][0]["type"] == ENTRY_TYPE_BLOB
        assert result["entries"][0]["blob_id"] == str(blob_id)


class TestTreeEntrySerialization:
    """TreeEntry 序列化测试场景。"""

    def test_should_convert_entry_to_dict(self):
        """测试：TreeEntry 转换为字典。"""
        # Given
        blob_id = uuid4()
        entry = TreeEntry(path=Path("file.txt"), entry_type=ENTRY_TYPE_BLOB, blob_id=blob_id)

        # When
        result = entry.to_dict()

        # Then
        assert result["path"] == "file.txt"
        assert result["type"] == ENTRY_TYPE_BLOB
        assert result["blob_id"] == str(blob_id)

    def test_should_convert_tree_entry_to_dict_without_blob_id(self):
        """测试：TreeEntry（目录）转换为字典不包含 blob_id。"""
        # Given
        entry = TreeEntry(path=Path("src/"), entry_type=ENTRY_TYPE_TREE, blob_id=None)

        # When
        result = entry.to_dict()

        # Then
        assert result["path"] == "src/"
        assert result["type"] == ENTRY_TYPE_TREE
        assert "blob_id" not in result

    def test_should_create_entry_from_dict(self):
        """测试：从字典创建 TreeEntry。"""
        # Given
        blob_id = uuid4()
        data = {"path": "file.txt", "type": ENTRY_TYPE_BLOB, "blob_id": str(blob_id)}

        # When
        entry = TreeEntry.from_dict(data)

        # Then
        assert str(entry.path) == "file.txt"
        assert entry.entry_type == ENTRY_TYPE_BLOB
        assert entry.blob_id == blob_id

    def test_should_create_tree_entry_from_dict_without_blob_id(self):
        """测试：从字典创建 TreeEntry（目录）。"""
        # Given
        data = {"path": "src/", "type": ENTRY_TYPE_TREE}

        # When
        entry = TreeEntry.from_dict(data)

        # Then
        assert str(entry.path) == "src/"
        assert entry.entry_type == ENTRY_TYPE_TREE
        assert entry.blob_id is None
