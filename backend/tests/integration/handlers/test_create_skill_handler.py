"""
Create Skill Handler Integration Tests

Tests the handle_create_skill function to cover:
- Successfully creating a new skill
- Raising ResourceConflictError when skill with same slug exists
- Creating skill tree and assigning it to skill
"""

from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.handlers.create_skill_handler import handle_create_skill
from src.domain.exceptions import ResourceConflictError
from src.infra.persistence.models.skill_model import SkillModel
from src.infra.persistence.models.tree_model import TreeModel
from src.infra.persistence.models.user_model import UserModel
from src.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository
from src.infra.persistence.repositories.sql_tree_repository import SqlTreeRepository


@pytest_asyncio.fixture
async def test_skill_with_slug(db_session: AsyncSession, test_user: UserModel) -> SkillModel:
    """Create an existing skill with a specific name/slug."""
    skill = SkillModel(
        id=uuid4(),
        user_id=test_user.id,
        name="Existing Skill Name",
        slug="existing-skill-name",
        description="An existing skill for conflict testing",
    )
    db_session.add(skill)
    await db_session.flush()
    await db_session.refresh(skill)
    return skill


class TestCreateSkillHandler:
    """Create Skill Handler integration tests."""

    @pytest.mark.asyncio
    async def test_should_successfully_create_new_skill(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """Given valid skill data, when creating, then skill with tree is returned."""
        # Given
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        skill_name = "New Test Skill"
        skill_description = "A test skill description"

        # When
        result = await handle_create_skill(
            user_id=test_user.id,
            name=skill_name,
            description=skill_description,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
        )
        await db_session.flush()

        # Then
        assert result is not None
        assert result.name == skill_name
        assert result.description == skill_description
        assert str(result.slug) == "new-test-skill"
        assert result.user_id == test_user.id
        assert result.tree_id is not None  # Tree should be assigned

    @pytest.mark.asyncio
    async def test_should_raise_resource_conflict_when_skill_slug_already_exists(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_skill_with_slug: SkillModel,
    ):
        """Given duplicate skill name, when creating, then ResourceConflictError is raised."""
        # Given
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        # Use the same name as existing skill (will generate same slug)
        duplicate_name = "Existing Skill Name"

        # When / Then
        with pytest.raises(ResourceConflictError) as exc_info:
            await handle_create_skill(
                user_id=test_user.id,
                name=duplicate_name,
                description="Some description",
                skill_repo=skill_repo,
                tree_repo=tree_repo,
            )

        assert exc_info.value.code == "RESOURCE_CONFLICT"

    @pytest.mark.asyncio
    async def test_should_create_and_assign_tree_to_skill(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """Given valid skill data, when creating, then tree is created and assigned to skill."""
        # Given
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        skill_name = "Skill With Tree"

        # When
        result = await handle_create_skill(
            user_id=test_user.id,
            name=skill_name,
            description=None,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
        )
        await db_session.flush()

        # Then
        assert result.tree_id is not None
        # Verify tree exists in database
        tree_result = await db_session.execute(
            select(TreeModel).where(TreeModel.id == result.tree_id)
        )
        saved_tree = tree_result.scalar_one_or_none()
        assert saved_tree is not None
        # Verify skill in database has tree_id
        skill_result = await db_session.execute(
            select(SkillModel).where(SkillModel.id == result.id)
        )
        saved_skill = skill_result.scalar_one()
        assert saved_skill.tree_id == result.tree_id
