"""Tests for get_tree_handler to cover remaining lines."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.application.handlers.get_tree_handler import handle_get_tree
from src.domain.aggregates.tree import Tree
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.tree_repository import TreeRepository


class TestGetTreeHandler:
    """Test get_tree_handler coverage gaps (lines 15-18)."""

    @pytest.mark.asyncio
    async def test_should_return_tree_when_found(self):
        """Test line 15-16: tree found and returned."""
        # Given
        tree_repo = AsyncMock(spec=TreeRepository)
        tree_id = uuid4()
        expected_tree = Mock(spec=Tree)
        tree_repo.get_by_id.return_value = expected_tree

        # When
        result = await handle_get_tree(tree_repo, tree_id)

        # Then
        assert result == expected_tree
        tree_repo.get_by_id.assert_called_once_with(tree_id)

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_tree_missing(self):
        """Test lines 17-18: tree not found raises error."""
        # Given
        tree_repo = AsyncMock(spec=TreeRepository)
        tree_id = uuid4()
        tree_repo.get_by_id.return_value = None

        # When/Then
        with pytest.raises(ResourceNotFoundError) as exc_info:
            await handle_get_tree(tree_repo, tree_id)

        assert str(tree_id) in str(exc_info.value)
