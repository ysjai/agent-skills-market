"""
Get Skill Handler Integration Tests

Tests the handle_get_skill function to cover:
- Successfully retrieving a skill by ID
- Raising ResourceNotFoundError when skill doesn't exist
- Raising ForbiddenError when user doesn't own the skill
"""

from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.handlers.get_skill_handler import handle_get_skill
from src.domain.exceptions import ForbiddenError, ResourceNotFoundError
from src.infra.persistence.models.skill_model import SkillModel
from src.infra.persistence.models.user_model import UserModel
from src.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository


@pytest_asyncio.fixture
async def test_other_user_skill(db_session: AsyncSession, another_user: UserModel) -> SkillModel:
    """Create a skill owned by another user."""
    skill = SkillModel(
        id=uuid4(),
        user_id=another_user.id,
        name="Other User Skill",
        slug="other-user-skill",
        description="Skill owned by another user",
    )
    db_session.add(skill)
    await db_session.flush()
    await db_session.refresh(skill)
    return skill


@pytest_asyncio.fixture
async def test_owned_skill(db_session: AsyncSession, test_user: UserModel) -> SkillModel:
    """Create a skill owned by the test user."""
    skill = SkillModel(
        id=uuid4(),
        user_id=test_user.id,
        name="Owned Skill",
        slug="owned-skill",
        description="Skill owned by test user",
    )
    db_session.add(skill)
    await db_session.flush()
    await db_session.refresh(skill)
    return skill


class TestGetSkillHandler:
    """Get Skill Handler integration tests."""

    @pytest.mark.asyncio
    async def test_should_successfully_retrieve_owned_skill(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_owned_skill: SkillModel,
    ):
        """Given owned skill ID, when getting skill, then skill is returned."""
        # Given
        skill_repo = SqlSkillRepository(db_session)

        # When
        result = await handle_get_skill(
            skill_id=test_owned_skill.id,
            user_id=test_user.id,
            skill_repo=skill_repo,
        )

        # Then
        assert result is not None
        assert result.id == test_owned_skill.id
        assert result.name == test_owned_skill.name
        assert result.user_id == test_user.id

    @pytest.mark.asyncio
    async def test_should_raise_resource_not_found_when_skill_does_not_exist(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """Given non-existent skill ID, when getting skill, then ResourceNotFoundError is raised."""
        # Given
        skill_repo = SqlSkillRepository(db_session)
        non_existent_skill_id = uuid4()

        # When / Then
        with pytest.raises(ResourceNotFoundError) as exc_info:
            await handle_get_skill(
                skill_id=non_existent_skill_id,
                user_id=test_user.id,
                skill_repo=skill_repo,
            )

        assert exc_info.value.code == "RESOURCE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_should_raise_forbidden_when_skill_owned_by_other_user(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_other_user_skill: SkillModel,
    ):
        """Given skill owned by another user, when getting skill, then ForbiddenError is raised."""
        # Given
        skill_repo = SqlSkillRepository(db_session)

        # When / Then
        with pytest.raises(ForbiddenError) as exc_info:
            await handle_get_skill(
                skill_id=test_other_user_skill.id,
                user_id=test_user.id,
                skill_repo=skill_repo,
            )

        assert exc_info.value.code == "FORBIDDEN"
