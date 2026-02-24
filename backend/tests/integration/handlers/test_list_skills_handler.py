"""Tests for list_skills_handler to cover remaining lines."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.handlers.list_skills_handler import handle_list_skills
from src.domain.repositories.skill_repository import SkillRepository


class TestListSkillsHandler:
    """Test list_skills_handler coverage gaps (line 13)."""

    @pytest.mark.asyncio
    async def test_should_return_list_of_skills_with_pagination(self):
        """Test line 13: return skills list."""
        # Given
        skill_repo = AsyncMock(spec=SkillRepository)
        user_id = uuid4()
        expected_skills = []
        skill_repo.find_by_user.return_value = expected_skills

        # When
        result = await handle_list_skills(user_id, 0, 100, skill_repo)

        # Then
        assert result == expected_skills
        skill_repo.find_by_user.assert_called_once_with(user_id, offset=0, limit=100)
