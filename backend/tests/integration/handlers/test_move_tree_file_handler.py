"""Tests for move_tree_file_handler."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.application.handlers.move_tree_file_handler import handle_move_tree_file
from src.domain.aggregates.tree import Tree
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.tree_repository import TreeRepository


class TestMoveTreeFileHandler:
    """Test move_tree_file_handler coverage (lines 17-18)."""

    @pytest.mark.asyncio
    async def test_should_move_file_in_tree(self):
        """Test successful file move."""
        # Given
        tree_repo = AsyncMock(spec=TreeRepository)
        tree = Mock(spec=Tree)
        tree_id = uuid4()
        tree_repo.get_by_id.return_value = tree

        # When
        result = await handle_move_tree_file(tree_repo, tree_id, "old/path", "new/path")

        # Then
        assert result == tree
        tree.move_entry.assert_called_once_with("old/path", "new/path")
        tree_repo.save.assert_called_once_with(tree)

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_tree_missing(self):
        """Test lines 17-18: raise error when tree not found."""
        # Given
        tree_repo = AsyncMock(spec=TreeRepository)
        tree_id = uuid4()
        tree_repo.get_by_id.return_value = None

        # When/Then
        with pytest.raises(ResourceNotFoundError) as exc_info:
            await handle_move_tree_file(tree_repo, tree_id, "old", "new")

        assert str(tree_id) in str(exc_info.value)
