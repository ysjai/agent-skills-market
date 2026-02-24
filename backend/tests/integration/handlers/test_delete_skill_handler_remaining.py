"""Tests for delete_skill_handler remaining coverage."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.handlers.delete_skill_handler import handle_delete_skill
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.blob_repository import BlobRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository


class TestDeleteSkillHandlerRemaining:
    """Test delete_skill_handler coverage (line 18)."""

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_skill_does_not_exist(self):
        """Test line 18: raise error when skill not found."""
        # Given
        skill_repo = AsyncMock(spec=SkillRepository)
        tree_repo = AsyncMock(spec=TreeRepository)
        blob_repo = AsyncMock(spec=BlobRepository)
        skill_id = uuid4()
        user_id = uuid4()

        skill_repo.get_by_id.return_value = None

        # When/Then
        with pytest.raises(ResourceNotFoundError):
            await handle_delete_skill(skill_id, user_id, skill_repo, tree_repo, blob_repo)
