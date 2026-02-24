"""
Import Skill Handler Integration Tests

Tests the handle_import_skill function to cover:
- Successfully importing a new skill
- Raising ResourceConflictError when skill with same slug exists
- Importing skill with custom slug
"""

from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.handlers.import_skill_handler import handle_import_skill
from app.domain.exceptions import ResourceConflictError
from app.infra.persistence.models.skill_model import SkillModel
from app.infra.persistence.models.user_model import UserModel
from app.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository
from app.infra.persistence.repositories.sql_tree_repository import SqlTreeRepository


@pytest_asyncio.fixture
async def test_existing_skill(db_session: AsyncSession, test_user: UserModel) -> SkillModel:
    """Create an existing skill for conflict testing."""
    skill = SkillModel(
        id=uuid4(),
        user_id=test_user.id,
        name="My Custom Skill",
        slug="my-custom-slug",
        description="Existing skill",
    )
    db_session.add(skill)
    await db_session.flush()
    await db_session.refresh(skill)
    return skill


class TestImportSkillHandler:
    """Import Skill Handler integration tests."""

    @pytest.mark.asyncio
    async def test_should_successfully_import_new_skill(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """Given valid import data, when importing, then skill with tree is returned."""
        # Given
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        skill_name = "Imported Skill"
        skill_description = "An imported skill"

        # When
        result = await handle_import_skill(
            user_id=test_user.id,
            name=skill_name,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            description=skill_description,
            slug=None,
        )
        await db_session.flush()

        # Then
        assert result is not None
        assert result.name == skill_name
        assert result.description == skill_description
        assert str(result.slug) == "imported-skill"
        assert result.user_id == test_user.id
        assert result.tree_id is not None

    @pytest.mark.asyncio
    async def test_should_raise_resource_conflict_when_slug_already_exists(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_existing_skill: SkillModel,
    ):
        """Given duplicate slug, when importing, then ResourceConflictError is raised."""
        # Given
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)

        # When / Then - Try to import with existing slug
        with pytest.raises(ResourceConflictError) as exc_info:
            await handle_import_skill(
                user_id=test_user.id,
                name="Different Name",
                skill_repo=skill_repo,
                tree_repo=tree_repo,
                description="Different description",
                slug="my-custom-slug",  # Same slug as existing skill
            )

        assert exc_info.value.code == "RESOURCE_CONFLICT"

    @pytest.mark.asyncio
    async def test_should_import_skill_with_custom_slug(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """Given custom slug, when importing, then skill uses custom slug."""
        # Given
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        custom_slug = "my-special-slug-123"
        skill_name = "Special Skill"

        # When
        result = await handle_import_skill(
            user_id=test_user.id,
            name=skill_name,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            description=None,
            slug=custom_slug,
        )
        await db_session.flush()

        # Then
        assert result is not None
        assert str(result.slug) == custom_slug
        assert result.name == skill_name
        # Verify in database
        skill_result = await db_session.execute(
            select(SkillModel).where(SkillModel.id == result.id)
        )
        saved_skill = skill_result.scalar_one()
        assert saved_skill.slug == custom_slug
