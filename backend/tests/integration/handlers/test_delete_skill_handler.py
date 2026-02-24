"""Tests for delete_skill_handler to cover remaining lines."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.application.handlers.delete_skill_handler import handle_delete_skill
from src.domain.aggregates.skill import Skill
from src.domain.repositories.blob_repository import BlobRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository


class TestDeleteSkillHandler:
    """Test delete_skill_handler coverage gaps (lines 17-18)."""

    @pytest.mark.asyncio
    async def test_should_delete_skill_owned_by_user(self):
        """Test line 17-18: delete skill when user is owner."""
        # Given
        skill_repo = AsyncMock(spec=SkillRepository)
        tree_repo = AsyncMock(spec=TreeRepository)
        blob_repo = AsyncMock(spec=BlobRepository)
        user_id = uuid4()
        skill_id = uuid4()

        skill = Mock(spec=Skill)
        skill.user_id = user_id
        skill.tree_id = None
        skill_repo.get_by_id.return_value = skill

        # When
        await handle_delete_skill(skill_id, user_id, skill_repo, tree_repo, blob_repo)

        # Then
        skill_repo.delete.assert_called_once_with(skill_id)
