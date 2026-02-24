"""Tests for create_tree_handler to cover remaining lines."""

from unittest.mock import AsyncMock

import pytest

from src.application.handlers.create_tree_handler import handle_create_tree
from src.domain.aggregates.tree import Tree
from src.domain.repositories.tree_repository import TreeRepository


class TestCreateTreeHandler:
    """Test create_tree_handler coverage gaps (line 14)."""

    @pytest.mark.asyncio
    async def test_should_create_tree_with_initial_entries(self):
        """Test line 14: create tree with entries list."""
        # Given
        tree_repo = AsyncMock(spec=TreeRepository)
        entries = [{"path": "test_dir/", "type": "tree"}]

        # When
        result = await handle_create_tree(tree_repo, entries)

        # Then
        assert isinstance(result, Tree)
        tree_repo.save.assert_called_once()
