"""Tests for Tree factory."""

import uuid

import pytest

from src.domain.aggregates.tree import Tree
from src.domain.exceptions import ValidationError
from src.domain.factories.tree_factory import TreeFactory


class TestTreeFactoryCreate:
    """Test TreeFactory create method."""

    def test_create_with_valid_entries(self):
        """Test creating tree with valid entries (L11-13)."""
        entries = [
            {"path": "test.py", "type": "blob", "blob_id": str(uuid.uuid4())},
            {"path": "docs", "type": "tree"},
        ]

        tree = TreeFactory.create(entries)

        assert isinstance(tree, Tree)
        assert len(tree.entries) == 2

    def test_create_with_none_entries(self):
        """Test creating tree with None entries (L27-28)."""
        tree = TreeFactory.create(None)

        assert isinstance(tree, Tree)

    def test_create_with_empty_entries(self):
        """Test creating tree with empty entries list."""
        tree = TreeFactory.create([])

        assert isinstance(tree, Tree)


class TestTreeFactoryCreateFromFile:
    """Test TreeFactory create_from_file method."""

    def test_create_from_file(self):
        """Test creating tree from file (L16-23)."""
        path = "test/example.py"
        blob_id = uuid.uuid4()

        tree = TreeFactory.create_from_file(path, blob_id)

        assert isinstance(tree, Tree)
        assert len(tree.entries) == 1

    def test_create_from_file_with_different_paths(self):
        """Test create_from_file with various paths (L22)."""
        test_cases = [
            ("root.txt", uuid.uuid4()),
            ("folder/file.py", uuid.uuid4()),
            ("deep/nested/path/file.md", uuid.uuid4()),
        ]

        for path, blob_id in test_cases:
            tree = TreeFactory.create_from_file(path, blob_id)
            assert isinstance(tree, Tree)


class TestTreeFactoryValidation:
    """Test TreeFactory entry validation."""

    def test_validate_entries_missing_path(self):
        """Test validation fails when entry missing path (L31-32)."""
        entries = [{"type": "blob", "blob_id": str(uuid.uuid4())}]

        with pytest.raises(ValidationError, match="must have 'path' field"):
            TreeFactory.create(entries)

    def test_validate_entries_missing_type(self):
        """Test validation fails when entry missing type (L33-34)."""
        entries = [{"path": "test.py", "blob_id": str(uuid.uuid4())}]

        with pytest.raises(ValidationError, match="must have 'type' field"):
            TreeFactory.create(entries)

    def test_validate_entries_invalid_type(self):
        """Test validation fails with invalid type (L36-38)."""
        entries = [{"path": "test.py", "type": "invalid", "blob_id": str(uuid.uuid4())}]

        with pytest.raises(ValidationError, match="Invalid entry type"):
            TreeFactory.create(entries)

    def test_validate_entries_blob_without_id(self):
        """Test validation fails when blob missing blob_id (L40-41)."""
        entries = [{"path": "test.py", "type": "blob"}]

        with pytest.raises(ValidationError, match="must have 'blob_id' field"):
            TreeFactory.create(entries)

    def test_validate_entries_tree_without_blob_id(self):
        """Test tree entries don't require blob_id."""
        entries = [{"path": "folder", "type": "tree"}]

        # Should not raise
        tree = TreeFactory.create(entries)
        assert isinstance(tree, Tree)

    def test_validate_entries_multiple_valid(self):
        """Test validation passes with multiple valid entries."""
        entries = [
            {"path": "file1.py", "type": "blob", "blob_id": str(uuid.uuid4())},
            {"path": "folder", "type": "tree"},
            {"path": "file2.md", "type": "blob", "blob_id": str(uuid.uuid4())},
        ]

        # Should not raise
        tree = TreeFactory.create(entries)
        assert isinstance(tree, Tree)
        assert len(tree.entries) == 3
