from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.aggregates.skill import Skill
from src.domain.aggregates.tree import Tree
from src.domain.exceptions import ResourceNotFoundError
from src.domain.value_objects.slug import Slug


@pytest.fixture
def shared_skill_repo():
    return AsyncMock()


@pytest.fixture
def skill_repo():
    return AsyncMock()


@pytest.fixture
def tree_repo():
    return AsyncMock()


class TestGetMarketSkillTreeHandler:
    @pytest.mark.asyncio
    async def test_should_return_tree_when_get_market_skill_tree_given_active_shared_skill(
        self, shared_skill_repo, skill_repo, tree_repo
    ):
        from src.application.handlers.get_market_skill_tree_handler import (
            handle_get_market_skill_tree,
        )

        shared_skill_id = uuid.uuid4()
        skill_id = uuid.uuid4()
        tree_id = uuid.uuid4()

        shared_skill = SharedSkill(id=shared_skill_id, skill_id=skill_id, status="active")
        skill = Skill(id=skill_id, tree_id=tree_id)
        tree = Tree(id=tree_id, entries=[])

        shared_skill_repo.find_by_id.return_value = shared_skill
        skill_repo.get_by_id.return_value = skill
        tree_repo.get_by_id.return_value = tree

        result = await handle_get_market_skill_tree(
            shared_skill_id=shared_skill_id,
            shared_skill_repo=shared_skill_repo,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
        )

        assert result.id == tree_id

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_get_market_skill_tree_given_nonexistent_shared_skill(
        self, shared_skill_repo, skill_repo, tree_repo
    ):
        from src.application.handlers.get_market_skill_tree_handler import (
            handle_get_market_skill_tree,
        )

        shared_skill_repo.find_by_id.return_value = None

        with pytest.raises(ResourceNotFoundError):
            await handle_get_market_skill_tree(
                shared_skill_id=uuid.uuid4(),
                shared_skill_repo=shared_skill_repo,
                skill_repo=skill_repo,
                tree_repo=tree_repo,
            )

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_get_market_skill_tree_given_withdrawn_skill(
        self, shared_skill_repo, skill_repo, tree_repo
    ):
        from src.application.handlers.get_market_skill_tree_handler import (
            handle_get_market_skill_tree,
        )

        shared_skill = SharedSkill(id=uuid.uuid4(), skill_id=None, status="withdrawn")
        shared_skill_repo.find_by_id.return_value = shared_skill

        with pytest.raises(ResourceNotFoundError):
            await handle_get_market_skill_tree(
                shared_skill_id=shared_skill.id,
                shared_skill_repo=shared_skill_repo,
                skill_repo=skill_repo,
                tree_repo=tree_repo,
            )

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_get_market_skill_tree_given_skill_without_tree(
        self, shared_skill_repo, skill_repo, tree_repo
    ):
        from src.application.handlers.get_market_skill_tree_handler import (
            handle_get_market_skill_tree,
        )

        skill_id = uuid.uuid4()
        shared_skill = SharedSkill(id=uuid.uuid4(), skill_id=skill_id, status="active")
        skill = Skill(id=skill_id, tree_id=None)

        shared_skill_repo.find_by_id.return_value = shared_skill
        skill_repo.get_by_id.return_value = skill

        with pytest.raises(ResourceNotFoundError):
            await handle_get_market_skill_tree(
                shared_skill_id=shared_skill.id,
                shared_skill_repo=shared_skill_repo,
                skill_repo=skill_repo,
                tree_repo=tree_repo,
            )
